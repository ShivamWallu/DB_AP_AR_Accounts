import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, ImportBatch, VoucherVerification
from app.schemas import (
    PaginatedResponse, DayBookRecordResponse, APRecordResponse, ARRecordResponse,
    FilterOptionsResponse, ToggleVerificationRequest, VerificationListResponse
)
from app.auth import get_current_user
from app.services.query_service import (
    query_daybook, query_ap, query_ar, query_master_360, get_filter_options,
    get_cross_referenced_voucher, get_daybook_dashboard_stats
)
from app.services.audit_service import log_activity

router = APIRouter(prefix="/api/data", tags=["Data Management"])

@router.get("/filters", response_model=FilterOptionsResponse)
def get_filters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_filter_options(db)

def _resolve_batch_id(db: Session, batch_id: Optional[str]) -> Optional[int]:
    """
    Smart Batch Resolution:
    - If empty/omitted -> defaults to the LATEST active batch ID with actual records.
    - If explicitly 'all' or 'all_batches' -> returns None (all batches).
    - If specific numeric ID -> returns integer ID.
    """
    if not batch_id or not str(batch_id).strip():
        latest = db.query(ImportBatch).filter(
            ImportBatch.status == "Completed",
            ImportBatch.new_records > 0
        ).order_by(ImportBatch.id.desc()).first()
        if not latest:
            latest = db.query(ImportBatch).filter(ImportBatch.status == "Completed").order_by(ImportBatch.id.desc()).first()
        return latest.id if latest else None
    if str(batch_id).strip().lower() in ("all", "all_batches", "0", "-1"):
        return None
    try:
        return int(batch_id)
    except (ValueError, TypeError):
        return None

@router.get("/master")
def get_master_360_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=1000000),
    search: Optional[str] = None,
    site: Optional[str] = None,
    voucher_type: Optional[str] = None,
    register_type: Optional[str] = None,
    approved_by: Optional[str] = None,
    batch_id: Optional[str] = None,
    verify_status: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    b_id = _resolve_batch_id(db, batch_id)
    total, records = query_master_360(
        db, page=page, page_size=page_size, search=search,
        site=site, voucher_type=voucher_type, register_type=register_type,
        approved_by=approved_by, batch_id=b_id, verify_status=verify_status,
        sort_by=sort_by, sort_order=sort_order
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": records
    }

@router.get("/daybook/stats")
def get_daybook_stats(
    batch_id: Optional[str] = None,
    site: Optional[str] = None,
    voucher_type: Optional[str] = None,
    approved_by: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None,
    voucher_status: Optional[str] = None,
    party_code: Optional[str] = None,
    created_date: Optional[str] = None,
    approved_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    b_id = _resolve_batch_id(db, batch_id)
    return get_daybook_dashboard_stats(
        db, batch_id=b_id, site=site, voucher_type=voucher_type,
        approved_by=approved_by, date_from=date_from, date_to=date_to,
        search=search, voucher_status=voucher_status, party_code=party_code,
        created_date=created_date, approved_date=approved_date
    )

@router.get("/daybook", response_model=PaginatedResponse)
def get_daybook_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=1000000),
    search: Optional[str] = None,
    site: Optional[str] = None,
    voucher_type: Optional[str] = None,
    approved_by: Optional[str] = None,
    batch_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    verify_status: Optional[str] = None,
    validation_status: Optional[str] = None,
    voucher_status: Optional[str] = None,
    party_code: Optional[str] = None,
    created_date: Optional[str] = None,
    approved_date: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    b_id = _resolve_batch_id(db, batch_id)
    total, records = query_daybook(
        db, page=page, page_size=page_size, search=search,
        site=site, voucher_type=voucher_type, approved_by=approved_by, batch_id=b_id,
        date_from=date_from, date_to=date_to, verify_status=verify_status,
        validation_status=validation_status, voucher_status=voucher_status,
        party_code=party_code, created_date=created_date, approved_date=approved_date,
        sort_by=sort_by, sort_order=sort_order
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    items = []
    for r in records:
        raw_dict = json.loads(r.raw_data_json) if r.raw_data_json else {}
        item = {**raw_dict}
        item["id"] = r.id
        item["batch_id"] = r.batch_id
        item["validation_status"] = r.validation_status or "Pending / Check Dates"
        # Standard snake_case compatibility aliases
        item["transaction_site"] = r.transaction_site or item.get("Transaction Site")
        item["voucher_number"] = r.voucher_number or item.get("Voucher Number")
        item["voucher_date"] = r.voucher_date or item.get("Voucher Date")
        item["voucher_type"] = r.voucher_type or item.get("Voucher Type")
        item["voucher_status"] = r.voucher_status or item.get("Voucher Status")
        item["party_code"] = r.party_code or item.get("Party Code")
        item["party_description"] = r.party_description or item.get("Party Description")
        item["account_description"] = r.account_description or item.get("Account Description")
        item["narration"] = r.narration or item.get("Narration")
        item["created_by"] = r.created_by or item.get("Created By")
        item["approved_by"] = r.approved_by or item.get("Approved By")
        item["created_date_raw"] = r.created_date_raw or item.get("Created Date")
        item["approved_date_raw"] = r.approved_date_raw or item.get("Approved Date")
        item["created_date"] = r.created_date_raw or item.get("Created Date")
        item["approved_date"] = r.approved_date_raw or item.get("Approved Date")
        items.append(item)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": items
    }

@router.get("/ap", response_model=PaginatedResponse)
def get_ap_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=1000000),
    search: Optional[str] = None,
    site: Optional[str] = None,
    voucher_type: Optional[str] = None,
    voucher_subtype: Optional[str] = None,
    approved_by: Optional[str] = None,
    batch_id: Optional[str] = None,
    verify_status: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    b_id = _resolve_batch_id(db, batch_id)
    total, records = query_ap(
        db, page=page, page_size=page_size, search=search,
        site=site, voucher_type=voucher_type, voucher_subtype=voucher_subtype,
        approved_by=approved_by, batch_id=b_id, verify_status=verify_status,
        sort_by=sort_by, sort_order=sort_order
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    items = [APRecordResponse(**r) for r in records]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": items
    }

@router.get("/ar", response_model=PaginatedResponse)
def get_ar_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=1000000),
    search: Optional[str] = None,
    site: Optional[str] = None,
    voucher_type: Optional[str] = None,
    voucher_subtype: Optional[str] = None,
    approved_by: Optional[str] = None,
    batch_id: Optional[str] = None,
    verify_status: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    b_id = _resolve_batch_id(db, batch_id)
    total, records = query_ar(
        db, page=page, page_size=page_size, search=search,
        site=site, voucher_type=voucher_type, voucher_subtype=voucher_subtype,
        approved_by=approved_by, batch_id=b_id, verify_status=verify_status,
        sort_by=sort_by, sort_order=sort_order
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    items = [ARRecordResponse(**r) for r in records]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": items
    }

@router.get("/cross-reference/{voucher_no:path}")
def cross_reference(
    voucher_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_cross_referenced_voucher(db, voucher_no)


@router.get("/verifications", response_model=VerificationListResponse)
def get_verifications(
    dataset_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns all active server-persisted verifications across all vouchers.
    Enables live dynamic sync for all logged-in accounts.
    """
    query = db.query(VoucherVerification)
    if dataset_type and dataset_type != "all":
        query = query.filter(VoucherVerification.dataset_type == dataset_type)
    
    rows = query.order_by(VoucherVerification.created_at.desc()).all()
    result = {}
    for r in rows:
        verif_data = {
            "verified_by": r.verified_by,
            "role": r.user_role or "User",
            "timestamp": r.timestamp_str or "",
            "date": r.date_str or "",
            "voucher_number": r.voucher_number,
            "dataset_type": r.dataset_type,
            "record_id": r.record_id
        }
        result[r.identifier_key] = verif_data
        
        # Also index by plain voucher number and generic key for cross-dataset matching
        if r.voucher_number and str(r.voucher_number).strip() not in ("—", "-", "null", "None", ""):
            v_str = str(r.voucher_number).strip()
            result[f"voucher_{v_str}"] = verif_data
            result[f"voucher_verified_master_{v_str}"] = verif_data
            result[f"voucher_verified_daybook_{v_str}"] = verif_data
            result[f"voucher_verified_ap_{v_str}"] = verif_data
            result[f"voucher_verified_ar_{v_str}"] = verif_data

    return {
        "verifications": result,
        "total": len(rows)
    }


@router.post("/verify")
def toggle_verification(
    payload: ToggleVerificationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atomically toggles verification for a voucher record in the central database.
    Updates in real-time for all connected users.
    """
    v_no = payload.voucher_number
    if v_no in ("—", "-", "null", "None", ""):
        v_no = None
    
    ident = v_no if v_no else str(payload.record_id or "0")
    key = f"voucher_verified_{payload.dataset_type}_{ident}"
    user_name = current_user.full_name or current_user.username or "Authorized Verifier"
    
    # Check if verification already exists
    if v_no:
        existing = db.query(VoucherVerification).filter(
            (VoucherVerification.identifier_key == key) |
            (VoucherVerification.voucher_number == v_no)
        ).first()
    else:
        existing = db.query(VoucherVerification).filter(
            VoucherVerification.identifier_key == key
        ).first()

    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%d/%m/%Y")

    if existing:
        # Toggle OFF (Unverify)
        del_vno = existing.voucher_number
        del_id = existing.record_id
        db.delete(existing)
        db.commit()
        
        log_activity(
            db=db,
            username=current_user.username,
            role=current_user.role,
            action="Voucher Unverified",
            status="Success",
            details=f"Unverified voucher {del_vno or del_id} in {payload.dataset_type}"
        )
        return {
            "status": "unverified",
            "identifier_key": key,
            "voucher_number": v_no,
            "record_id": payload.record_id,
            "dataset_type": payload.dataset_type,
            "message": f"Verification unmarked for {v_no or payload.record_id}"
        }
    else:
        # Toggle ON (Verify)
        new_verif = VoucherVerification(
            dataset_type=payload.dataset_type,
            identifier_key=key,
            voucher_number=v_no,
            record_id=payload.record_id,
            verified_by=user_name,
            user_role=current_user.role,
            timestamp_str=time_str,
            date_str=date_str,
            created_at=datetime.utcnow()
        )
        db.add(new_verif)
        db.commit()
        db.refresh(new_verif)
        
        log_activity(
            db=db,
            username=current_user.username,
            role=current_user.role,
            action="Voucher Verified",
            status="Success",
            details=f"Verified voucher {v_no or payload.record_id} in {payload.dataset_type} as {user_name}"
        )
        return {
            "status": "verified",
            "identifier_key": key,
            "voucher_number": v_no,
            "record_id": payload.record_id,
            "dataset_type": payload.dataset_type,
            "data": {
                "verified_by": user_name,
                "role": current_user.role,
                "timestamp": time_str,
                "date": date_str
            },
            "message": f"Successfully verified by {user_name}"
        }

