import csv
import io
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, VoucherVerification
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

def clean_val(val: Any) -> str:
    """Sanitize string values, eliminating any Unicode em-dash, None, or null to prevent Excel mojibake (â€”)"""
    if val is None:
        return ""
    s = str(val).strip()
    if s in ("—", "-", "None", "null", "undefined"):
        return ""
    return s

def clean_num(val: Any) -> str:
    """Sanitize numeric values for clean Excel display without garbled characters or NaN"""
    if val is None:
        return ""
    s = str(val).strip()
    if s in ("", "—", "-", "None", "null", "undefined"):
        return ""
    try:
        f = float(val)
        return f"{f:.2f}"
    except (ValueError, TypeError):
        return ""

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
    # If client did not provide verifications or only partial, pull all from database
    if not verifications:
        verifications = {}
    try:
        db_verifs = db.query(VoucherVerification).all()
        for v in db_verifs:
            if v.voucher_number and str(v.voucher_number) not in verifications:
                verifications[str(v.voucher_number)] = v.verified_by
            if v.record_id and str(v.record_id) not in verifications:
                verifications[str(v.record_id)] = v.verified_by
    except Exception as e:
        print(f"Warning: Failed to load db verifications for export: {e}")

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
            "Site", "Voucher No.", "Voucher Date", "Voucher Type",
            "Status", "Party Code", "Party Description", "Account Description",
            "Narration", "Created By", "Approved By", "Verified Status"
        ]
        writer.writerow(headers)
        for r in records:
            writer.writerow([
                clean_val(r.transaction_site),
                clean_val(r.voucher_number),
                clean_val(r.voucher_date),
                clean_val(r.voucher_type),
                clean_val(r.voucher_status),
                clean_val(r.party_code),
                clean_val(r.party_description),
                clean_val(r.account_description),
                clean_val(r.narration),
                clean_val(r.created_by),
                clean_val(r.approved_by),
                clean_val(resolve_verifier_name(r, verifications))
            ])

    elif ds_lower == "ap":
        _, records = query_ap(
            db, page=1, page_size=1000000, search=search,
            site=site, voucher_type=voucher_type, voucher_subtype=voucher_subtype,
            approved_by=approved_by, batch_id=batch_id
        )
        total_exported = len(records)
        headers = [
            "Site Code", "Voucher No.", "Voucher Type", "Voucher Sub-Type",
            "Party GST TIN", "Invoice No.", "Invoice Date", "Due Date",
            "Item / Service Description", "Expense Account",
            "Quantity", "Rate (INR)", "Detail Amount (INR)",
            "Tax Amount (INR)", "Total Voucher Amount (INR)", "Total TDS (INR)",
            "Narration", "Created By", "Approved By", "Verified Status"
        ]
        writer.writerow(headers)
        for r in records:
            writer.writerow([
                clean_val(r.get("accounting_site_code")),
                clean_val(r.get("voucher_number")),
                clean_val(r.get("voucher_type")),
                clean_val(r.get("voucher_sub_type")),
                clean_val(r.get("party_gst_tin")),
                clean_val(r.get("invoice_number")),
                clean_val(r.get("invoice_date")),
                clean_val(r.get("due_date")),
                clean_val(r.get("item_service_description")),
                clean_val(r.get("item_service_expense_account_desc")),
                clean_val(r.get("booked_item_quantity")),
                clean_num(r.get("item_service_rate")),
                clean_num(r.get("item_service_detail_amount")),
                clean_num(r.get("total_tax_amount")),
                clean_num(r.get("total_voucher_amount")),
                clean_num(r.get("total_tds")),
                clean_val(r.get("narration")),
                clean_val(r.get("created_by")),
                clean_val(r.get("approved_by")),
                clean_val(resolve_verifier_name(r, verifications))
            ])

    elif ds_lower == "ar":
        _, records = query_ar(
            db, page=1, page_size=1000000, search=search,
            site=site, voucher_type=voucher_type, voucher_subtype=voucher_subtype,
            approved_by=approved_by, batch_id=batch_id
        )
        total_exported = len(records)
        headers = [
            "Site Code", "Voucher No.", "Voucher Type", "Voucher Sub-Type",
            "Item / Service Description", "Item Qty", "Rate (INR)",
            "Amount (INR)", "Charges (INR)", "Net of Discount (INR)",
            "Taxes (INR)", "Net Amount (INR)", "Total CGST (INR)", "Total SGST (INR)", "Total IGST (INR)",
            "Narration", "Created By", "Approved By", "Verified Status"
        ]
        writer.writerow(headers)
        for r in records:
            writer.writerow([
                clean_val(r.get("accounting_site_code")),
                clean_val(r.get("voucher_number")),
                clean_val(r.get("voucher_type")),
                clean_val(r.get("voucher_sub_type")),
                clean_val(r.get("item_service_description")),
                clean_val(r.get("item_quantity")),
                clean_num(r.get("item_service_rate")),
                clean_num(r.get("item_service_amount")),
                clean_num(r.get("item_service_charges")),
                clean_num(r.get("item_amount_net_off_discount")),
                clean_num(r.get("item_service_taxes")),
                clean_num(r.get("net_amount")),
                clean_num(r.get("total_cgst")),
                clean_num(r.get("total_sgst")),
                clean_num(r.get("total_igst")),
                clean_val(r.get("narration")),
                clean_val(r.get("created_by")),
                clean_val(r.get("approved_by")),
                clean_val(resolve_verifier_name(r, verifications))
            ])

    elif ds_lower == "master":
        _, records = query_master_360(
            db, page=1, page_size=1000000, search=search,
            site=site, voucher_type=voucher_type, register_type=register_type,
            approved_by=approved_by, batch_id=batch_id
        )
        total_exported = len(records)
        headers = [
            "Site", "Voucher No.", "Party Name", "Voucher Date", "Voucher Type",
            "Item / Expense Description", "Expense Account", "Quantity", "Rate (INR)",
            "Total Amount (INR)", "Tax Amount (GST)", "Status",
            "Narration", "Created By", "Approved By", "Verified Status"
        ]
        writer.writerow(headers)
        prev_v_no = None
        for r in records:
            raw_v_no = clean_val(r.get("voucher_number"))
            display_v_no = "" if (prev_v_no is not None and raw_v_no and raw_v_no == prev_v_no) else raw_v_no
            prev_v_no = raw_v_no
            party_name = clean_val(r.get("party_description") or r.get("party_code"))

            raw_qty = r.get("unified_quantity")
            try:
                num_qty = float(raw_qty) if raw_qty is not None and str(raw_qty).strip() != "" else 0.0
            except (ValueError, TypeError):
                num_qty = 0.0

            export_qty = clean_val(raw_qty) if num_qty > 0 else ""
            export_rate = clean_num(r.get("unified_rate")) if num_qty > 0 else ""

            writer.writerow([
                clean_val(r.get("transaction_site")),
                display_v_no,
                party_name,
                clean_val(r.get("voucher_date")),
                clean_val(r.get("voucher_type")),
                clean_val(r.get("unified_item_description")),
                clean_val(r.get("expense_account") or r.get("account_description")),
                export_qty,
                export_rate,
                clean_num(r.get("combined_amount")),
                clean_num(r.get("unified_tax_amount")),
                clean_val(r.get("voucher_status")),
                clean_val(r.get("narration")),
                clean_val(r.get("created_by")),
                clean_val(r.get("approved_by")),
                clean_val(resolve_verifier_name(r, verifications))
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
