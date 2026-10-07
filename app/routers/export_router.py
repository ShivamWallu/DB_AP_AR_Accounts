import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import oauth2_scheme, SECRET_KEY, ALGORITHM
import jwt
from app.services.query_service import query_daybook, query_ap, query_ar, query_master_360
from app.services.audit_service import log_activity

router = APIRouter(prefix="/api/export", tags=["Export"])

def get_user_from_header_or_query(
    token_param: Optional[str] = Query(None, alias="token"),
    auth_header_token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    token = auth_header_token or token_param
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required for data export."
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not active")
    return user

from pydantic import BaseModel
from typing import Optional, Dict, Any
import json

class ExportPayload(BaseModel):
    search: Optional[str] = None
    site: Optional[str] = None
    voucher_type: Optional[str] = None
    voucher_subtype: Optional[str] = None
    register_type: Optional[str] = None
    approved_by: Optional[str] = None
    batch_id: Optional[int] = None
    verifications: Optional[Dict[str, str]] = None

def resolve_verifier_name(r_or_dict, verifications_map: Optional[Dict[str, str]] = None) -> str:
    """
    Dynamically resolves the actual name of the user/auditor who verified the voucher.
    Checks dynamic client-side verifications map first, then record verified_by.
    Returns 'Pending' if not verified.
    """
    if isinstance(r_or_dict, dict):
        v_no = r_or_dict.get("voucher_number")
        r_id = str(r_or_dict.get("id", ""))
        v_by = r_or_dict.get("verified_by")
        is_v = r_or_dict.get("is_verified", False)
    else:
        v_no = getattr(r_or_dict, "voucher_number", None)
        r_id = str(getattr(r_or_dict, "id", ""))
        v_by = getattr(r_or_dict, "verified_by", None)
        is_v = getattr(r_or_dict, "is_verified", False)

    # 1. Dynamic Verifications Map from active session / UI
    if verifications_map:
        if v_no and str(v_no) in verifications_map:
            val = verifications_map[str(v_no)]
            if val and str(val).strip():
                return str(val).strip()
        if r_id and r_id in verifications_map:
            val = verifications_map[r_id]
            if val and str(val).strip():
                return str(val).strip()

    # 2. Database explicit verified_by field
    if v_by and str(v_by).strip() and str(v_by).strip() not in ("—", "-", "None"):
        return str(v_by).strip()

    # 3. If digitally marked verified without name
    if is_v:
        return "Verified"

    # 4. Default: Pending verification
    return "Pending"

def build_export_response(
    dataset: str,
    search: Optional[str],
    site: Optional[str],
    voucher_type: Optional[str],
    voucher_subtype: Optional[str],
    register_type: Optional[str],
    approved_by: Optional[str],
    batch_id: Optional[int],
    verifications: Optional[Dict[str, str]],
    db: Session,
    current_user: User
) -> Response:
    output = io.StringIO()
    # Write UTF-8 BOM so Microsoft Excel cleanly renders symbols and UTF-8 characters
    output.write('\ufeff')
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

    ds_lower = dataset.lower().strip()
    total_exported = 0

    if ds_lower == "daybook":
        _, records = query_daybook(
            db, page=1, page_size=1000000, search=search,
            site=site, voucher_type=voucher_type, approved_by=approved_by, batch_id=batch_id
        )
        total_exported = len(records)
        headers = [
            "ID", "Transaction Site", "Voucher Number", "Voucher Date", "Voucher Type",
            "Voucher Status", "Party Code", "Party Description", "Account Description",
            "Narration", "Created By", "Approved By", "Verified Status"
        ]
        writer.writerow(headers)
        for r in records:
            writer.writerow([
                r.id,
                r.transaction_site or "",
                r.voucher_number or "",
                r.voucher_date or "",
                r.voucher_type or "",
                r.voucher_status or "",
                r.party_code or "",
                r.party_description or "",
                r.account_description or "",
                r.narration or "",
                r.created_by or "",
                r.approved_by or "",
                resolve_verifier_name(r, verifications)
            ])

    elif ds_lower == "ap":
        _, records = query_ap(
            db, page=1, page_size=1000000, search=search,
            site=site, voucher_type=voucher_type, voucher_subtype=voucher_subtype,
            approved_by=approved_by, batch_id=batch_id
        )
        total_exported = len(records)
        headers = [
            "ID", "Accounting Site Code", "Voucher Number", "Voucher Type", "Voucher Sub-Type",
            "Party GST TIN", "Invoice Number", "Invoice Date", "Due Date",
            "Item/Service Description", "Expense Account Description",
            "Booked Quantity", "Rate", "Detail Amount",
            "Tax Amount", "Total Voucher Amount", "Total TDS",
            "Narration", "Created By", "Approved By"
        ]
        writer.writerow(headers)
        for r in records:
            writer.writerow([
                r.get("id", ""),
                r.get("accounting_site_code", ""),
                r.get("voucher_number", ""),
                r.get("voucher_type", ""),
                r.get("voucher_sub_type", ""),
                r.get("party_gst_tin", ""),
                r.get("invoice_number", ""),
                r.get("invoice_date", ""),
                r.get("due_date", ""),
                r.get("item_service_description", ""),
                r.get("item_service_expense_account_desc", ""),
                r.get("booked_item_quantity", ""),
                f"{float(r.get('item_service_rate') or 0):.2f}" if r.get("item_service_rate") is not None else "",
                f"{float(r.get('item_service_detail_amount') or 0):.2f}" if r.get("item_service_detail_amount") is not None else "",
                f"{float(r.get('total_tax_amount') or 0):.2f}" if r.get("total_tax_amount") is not None else "",
                f"{float(r.get('total_voucher_amount') or 0):.2f}" if r.get("total_voucher_amount") is not None else "",
                f"{float(r.get('total_tds') or 0):.2f}" if r.get("total_tds") is not None else "",
                r.get("narration", ""),
                r.get("created_by", ""),
                r.get("approved_by", "")
            ])

    elif ds_lower == "ar":
        _, records = query_ar(
            db, page=1, page_size=1000000, search=search,
            site=site, voucher_type=voucher_type, voucher_subtype=voucher_subtype,
            approved_by=approved_by, batch_id=batch_id
        )
        total_exported = len(records)
        headers = [
            "ID", "Accounting Site Code", "Voucher Number", "Voucher Type", "Voucher Sub-Type",
            "Item/Service Description", "Item Quantity", "Rate",
            "Item Amount", "Charges", "Net Off Discount",
            "Taxes", "Net Amount", "Total CGST", "Total SGST", "Total IGST",
            "Narration", "Created By", "Approved By"
        ]
        writer.writerow(headers)
        for r in records:
            writer.writerow([
                r.get("id", ""),
                r.get("accounting_site_code", ""),
                r.get("voucher_number", ""),
                r.get("voucher_type", ""),
                r.get("voucher_sub_type", ""),
                r.get("item_service_description", ""),
                r.get("item_quantity", ""),
                f"{float(r.get('item_service_rate') or 0):.2f}" if r.get("item_service_rate") is not None else "",
                f"{float(r.get('item_service_amount') or 0):.2f}" if r.get("item_service_amount") is not None else "",
                f"{float(r.get('item_service_charges') or 0):.2f}" if r.get("item_service_charges") is not None else "",
                f"{float(r.get('item_amount_net_off_discount') or 0):.2f}" if r.get("item_amount_net_off_discount") is not None else "",
                f"{float(r.get('item_service_taxes') or 0):.2f}" if r.get("item_service_taxes") is not None else "",
                f"{float(r.get('net_amount') or 0):.2f}" if r.get("net_amount") is not None else "",
                f"{float(r.get('total_cgst') or 0):.2f}" if r.get("total_cgst") is not None else "",
                f"{float(r.get('total_sgst') or 0):.2f}" if r.get("total_sgst") is not None else "",
                f"{float(r.get('total_igst') or 0):.2f}" if r.get("total_igst") is not None else "",
                r.get("narration", ""),
                r.get("created_by", ""),
                r.get("approved_by", "")
            ])

    elif ds_lower == "master":
        _, records = query_master_360(
            db, page=1, page_size=1000000, search=search,
            site=site, voucher_type=voucher_type, register_type=register_type,
            approved_by=approved_by, batch_id=batch_id
        )
        total_exported = len(records)
        headers = [
            "Source Register", "Transaction Site", "Voucher Number", "Voucher Date", "Voucher Type",
            "Voucher Status", "Party Code", "Party Description", "Account Description",
            "Linked AP Invoice No", "Linked AP Party GST", "Linked AP Item", "Linked AP Amount", "Linked AP Tax", "Linked AP TDS",
            "Linked AR Sub-Type", "Linked AR Item", "Linked AR Net Amount", "Linked AR Tax",
            "Total Financial Amount (INR)", "Tax Amount (GST)", "Narration", "Created By", "Approved By",
            "Verified Status"
        ]
        writer.writerow(headers)
        for r in records:
            writer.writerow([
                r.get("source_tag", ""),
                r.get("transaction_site", ""),
                r.get("voucher_number", ""),
                r.get("voucher_date", ""),
                r.get("voucher_type", ""),
                r.get("voucher_status", ""),
                r.get("party_code", ""),
                r.get("party_description", ""),
                r.get("account_description", ""),
                r.get("ap_invoice_number", ""),
                r.get("ap_party_gst", ""),
                r.get("ap_item_description", ""),
                f"{float(r.get('ap_total_amount') or 0):.2f}" if r.get("ap_total_amount") is not None else "",
                f"{float(r.get('ap_tax_amount') or 0):.2f}" if r.get("ap_tax_amount") is not None else "",
                f"{float(r.get('ap_total_tds') or 0):.2f}" if r.get("ap_total_tds") is not None else "",
                r.get("ar_subtype", ""),
                r.get("ar_item_description", ""),
                f"{float(r.get('ar_net_amount') or 0):.2f}" if r.get("ar_net_amount") is not None else "",
                f"{float(r.get('ar_tax_amount') or 0):.2f}" if r.get("ar_tax_amount") is not None else "",
                f"{float(r.get('combined_amount') or 0):.2f}" if r.get("combined_amount") is not None else "",
                f"{float(r.get('unified_tax_amount') or 0):.2f}" if r.get("unified_tax_amount") is not None else "",
                r.get("narration", ""),
                r.get("created_by", ""),
                r.get("approved_by", ""),
                resolve_verifier_name(r, verifications)
            ])

    else:
        return Response(content="Invalid dataset requested", status_code=400)

    log_activity(
        db=db,
        username=current_user.username,
        role=current_user.role,
        action="Data Export",
        details=f"Exported {total_exported} records from {dataset} dataset (CSV with UTF-8 BOM)"
    )

    output.seek(0)
    csv_bytes = output.getvalue().encode('utf-8')
    filename = f"KOGM_{dataset.upper()}_Export_{total_exported}rows.csv"

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@router.post("/{dataset}")
def export_dataset_post(
    dataset: str,
    payload: ExportPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_header_or_query)
):
    return build_export_response(
        dataset=dataset,
        search=payload.search,
        site=payload.site,
        voucher_type=payload.voucher_type,
        voucher_subtype=payload.voucher_subtype,
        register_type=payload.register_type,
        approved_by=payload.approved_by,
        batch_id=payload.batch_id,
        verifications=payload.verifications,
        db=db,
        current_user=current_user
    )

@router.get("/{dataset}")
def export_dataset_get(
    dataset: str,
    search: Optional[str] = None,
    site: Optional[str] = None,
    voucher_type: Optional[str] = None,
    voucher_subtype: Optional[str] = None,
    register_type: Optional[str] = None,
    approved_by: Optional[str] = None,
    batch_id: Optional[int] = None,
    verifications: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_header_or_query)
):
    verifications_dict = None
    if verifications:
        try:
            verifications_dict = json.loads(verifications)
        except Exception:
            verifications_dict = None

    return build_export_response(
        dataset=dataset,
        search=search,
        site=site,
        voucher_type=voucher_type,
        voucher_subtype=voucher_subtype,
        register_type=register_type,
        approved_by=approved_by,
        batch_id=batch_id,
        verifications=verifications_dict,
        db=db,
        current_user=current_user
    )
