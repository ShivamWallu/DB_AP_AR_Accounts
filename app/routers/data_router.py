from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    PaginatedResponse, DayBookRecordResponse, APRecordResponse, ARRecordResponse,
    FilterOptionsResponse
)
from app.auth import get_current_user
from app.services.query_service import (
    query_daybook, query_ap, query_ar, query_master_360, get_filter_options, get_cross_referenced_voucher
)

router = APIRouter(prefix="/api/data", tags=["Data Management"])

@router.get("/filters", response_model=FilterOptionsResponse)
def get_filters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_filter_options(db)

def _parse_int_param(val: Optional[str]) -> Optional[int]:
    if not val:
        return None
    try:
        return int(val)
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
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    b_id = _parse_int_param(batch_id)
    total, records = query_master_360(
        db, page=page, page_size=page_size, search=search,
        site=site, voucher_type=voucher_type, register_type=register_type,
        approved_by=approved_by, batch_id=b_id, sort_by=sort_by, sort_order=sort_order
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": records
    }

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
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    b_id = _parse_int_param(batch_id)
    total, records = query_daybook(
        db, page=page, page_size=page_size, search=search,
        site=site, voucher_type=voucher_type, approved_by=approved_by, batch_id=b_id,
        date_from=date_from, date_to=date_to,
        sort_by=sort_by, sort_order=sort_order
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    items = [DayBookRecordResponse.model_validate(r) for r in records]
    
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
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    b_id = _parse_int_param(batch_id)
    total, records = query_ap(
        db, page=page, page_size=page_size, search=search,
        site=site, voucher_type=voucher_type, voucher_subtype=voucher_subtype,
        approved_by=approved_by, batch_id=b_id, sort_by=sort_by, sort_order=sort_order
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
    sort_by: str = "id",
    sort_order: str = "desc",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    b_id = _parse_int_param(batch_id)
    total, records = query_ar(
        db, page=page, page_size=page_size, search=search,
        site=site, voucher_type=voucher_type, voucher_subtype=voucher_subtype,
        approved_by=approved_by, batch_id=b_id, sort_by=sort_by, sort_order=sort_order
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

@router.get("/cross-reference/{voucher_no}")
def cross_reference(
    voucher_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_cross_referenced_voucher(db, voucher_no)
