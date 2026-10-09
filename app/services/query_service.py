from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc, func
from app.models import DayBookRecord, APRecord, ARRecord, ImportBatch, VoucherVerification

def get_filter_options(db: Session) -> Dict[str, Any]:
    """Retrieve dynamic unique filter values across all tables"""
    # Unique Sites across all 3 tables
    db_sites = [r[0] for r in db.query(DayBookRecord.transaction_site).distinct().filter(DayBookRecord.transaction_site.isnot(None)).all()]
    ap_sites = [r[0] for r in db.query(APRecord.accounting_site_code).distinct().filter(APRecord.accounting_site_code.isnot(None)).all()]
    ar_sites = [r[0] for r in db.query(ARRecord.accounting_site_code).distinct().filter(ARRecord.accounting_site_code.isnot(None)).all()]
    all_sites = sorted(list(set(db_sites + ap_sites + ar_sites)))

    # Unique Voucher Types across all 3 tables
    db_vtypes = [r[0] for r in db.query(DayBookRecord.voucher_type).distinct().filter(DayBookRecord.voucher_type.isnot(None)).all()]
    ap_vtypes = [r[0] for r in db.query(APRecord.voucher_type).distinct().filter(APRecord.voucher_type.isnot(None)).all()]
    ar_vtypes = [r[0] for r in db.query(ARRecord.voucher_type).distinct().filter(ARRecord.voucher_type.isnot(None)).all()]
    all_vtypes = sorted(list(set(db_vtypes + ap_vtypes + ar_vtypes)))

    # Unique Voucher Sub-Types across AP and AR
    ap_subtypes = [r[0] for r in db.query(APRecord.voucher_sub_type).distinct().filter(APRecord.voucher_sub_type.isnot(None)).all()]
    ar_subtypes = [r[0] for r in db.query(ARRecord.voucher_sub_type).distinct().filter(ARRecord.voucher_sub_type.isnot(None)).all()]
    all_subtypes = sorted(list(set(ap_subtypes + ar_subtypes)))

    # Unique Approvers across Day Book records
    db_approvers = [
        r[0] for r in db.query(DayBookRecord.approved_by).distinct().filter(DayBookRecord.approved_by.isnot(None)).all()
        if r[0] and r[0].strip() and r[0].strip() not in ("None", "-", "—", "null", "undefined")
    ]
    all_approvers = sorted(list(set(db_approvers)))

    # Batch list - all active batches within 14-day retention lifecycle
    batches = db.query(ImportBatch).filter(
        ImportBatch.status == "Completed",
        ImportBatch.total_rows > 0
    ).order_by(desc(ImportBatch.id)).all()
    batch_list = []
    for b in batches:
        v_range = getattr(b, 'voucher_date_range', None)
        if not v_range or v_range == b.upload_date_str:
            # Dynamically extract distinct voucher dates from records for this batch
            raw_vdates = [
                r[0] for r in db.query(DayBookRecord.voucher_date).distinct()
                .filter(DayBookRecord.batch_id == b.id, DayBookRecord.voucher_date.isnot(None)).all()
                if r[0] and str(r[0]).strip() and str(r[0]).strip() not in ("None", "-", "—", "null", "undefined")
            ]
            if raw_vdates:
                if len(raw_vdates) == 1:
                    v_range = raw_vdates[0]
                elif len(raw_vdates) == 2:
                    v_range = f"{raw_vdates[0]}, {raw_vdates[1]}"
                else:
                    v_range = f"{raw_vdates[0]} ~ {raw_vdates[-1]}"
            else:
                v_range = b.upload_date_str

        batch_list.append({
            "id": b.id,
            "batch_code": b.batch_code,
            "date": b.upload_date_str,
            "time": b.upload_time_str,
            "voucher_date_range": v_range,
            "status": b.status
        })

    return {
        "sites": all_sites,
        "voucher_types": all_vtypes,
        "voucher_subtypes": all_subtypes,
        "approvers": all_approvers,
        "batches": batch_list
    }

def expand_voucher_type_synonyms(vt: str) -> List[str]:
    """Map voucher type synonyms between Day Book, AP, and AR registers"""
    clean = vt.strip()
    synonyms = {clean}
    if clean in ("Sales Invoice", "Sales ( Commercial )"):
        synonyms.update(["Sales Invoice", "Sales ( Commercial )"])
    elif clean in ("Receipt Voucher", "Receipt against Sales Invoice"):
        synonyms.update(["Receipt Voucher", "Receipt against Sales Invoice"])
    elif clean in ("Sales Return", "SalesReturn"):
        synonyms.update(["Sales Return", "SalesReturn"])
    elif clean in ("Expense Voucher", "Service Expense Voucher"):
        synonyms.update(["Expense Voucher", "Service Expense Voucher"])
    return list(synonyms)

def parse_multi_filter(val: Optional[Any], default_all_names: Tuple[str, ...] = ("all", "all sites", "all voucher types", "all approvers", "")) -> List[str]:
    """Parse single or multi-select comma-delimited filter values into clean string list"""
    if not val:
        return []
    if isinstance(val, list):
        return [str(s).strip() for s in val if s and str(s).strip() and str(s).strip().lower() not in default_all_names]
    raw = str(val).strip()
    if raw.lower() in default_all_names:
        return []
    parts = [s.strip() for s in raw.split(",") if s.strip() and s.strip().lower() not in default_all_names]
    return parts

def parse_site_filter(site: Optional[Any]) -> List[str]:
    """Parse single or multi-select comma-delimited sites into clean list"""
    return parse_multi_filter(site, ("all", "all sites", "all_sites", ""))

def expand_voucher_types_multi(vtypes_raw: Optional[Any]) -> List[str]:
    """Expand synonyms across multiple selected voucher types"""
    selected = parse_multi_filter(vtypes_raw, ("all", "all voucher types", "all_voucher_types", ""))
    if not selected:
        return []
    all_expanded = set()
    for vt in selected:
        for syn in expand_voucher_type_synonyms(vt):
            all_expanded.add(syn)
    return list(all_expanded)

def build_approvers_conditions(model_class, approved_by_raw: Optional[Any]):
    """Build SQLAlchemy filter condition for multi-selected approvers"""
    approvers_list = parse_multi_filter(approved_by_raw, ("all", "all approvers", "all_approvers", ""))
    if not approvers_list:
        return None

    conditions = []
    has_approved_special = "approved" in approvers_list
    has_pending_special = "pending" in approvers_list or "unapproved" in approvers_list
    specific_names = [a for a in approvers_list if a not in ("approved", "pending", "unapproved")]

    if has_approved_special:
        conditions.append(
            and_(
                model_class.approved_by.isnot(None),
                model_class.approved_by != "",
                model_class.approved_by != "—",
                model_class.approved_by != "-"
            )
        )
    if has_pending_special:
        conditions.append(
            or_(
                model_class.approved_by.is_(None),
                model_class.approved_by == "",
                model_class.approved_by == "—",
                model_class.approved_by == "-"
            )
        )
    if specific_names:
        if len(specific_names) == 1:
            conditions.append(model_class.approved_by == specific_names[0])
        else:
            conditions.append(model_class.approved_by.in_(specific_names))

    if conditions:
        return or_(*conditions) if len(conditions) > 1 else conditions[0]
    return None

def query_daybook(
    db: Session,
    page: int = 1,
    page_size: int = 15,
    search: Optional[str] = None,
    site: Optional[str] = None,
    voucher_type: Optional[str] = None,
    approved_by: Optional[str] = None,
    batch_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    verify_status: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc"
) -> Tuple[int, List[DayBookRecord]]:
    """Query Day Book records with server-side filters, search, and pagination"""
    q = db.query(DayBookRecord)

    sites_list = parse_site_filter(site)
    if sites_list:
        if len(sites_list) == 1:
            q = q.filter(DayBookRecord.transaction_site == sites_list[0])
        else:
            q = q.filter(DayBookRecord.transaction_site.in_(sites_list))

    syns = expand_voucher_types_multi(voucher_type)
    if syns:
        if len(syns) == 1:
            q = q.filter(DayBookRecord.voucher_type == syns[0])
        else:
            q = q.filter(DayBookRecord.voucher_type.in_(syns))

    appr_cond = build_approvers_conditions(DayBookRecord, approved_by)
    if appr_cond is not None:
        q = q.filter(appr_cond)
    if batch_id:
        q = q.filter(DayBookRecord.batch_id == batch_id)
    if date_from and date_from.strip():
        q = q.filter(DayBookRecord.voucher_date >= date_from.strip())
    if date_to and date_to.strip():
        q = q.filter(DayBookRecord.voucher_date <= date_to.strip())

    # Verification status filter
    if verify_status and verify_status.strip().lower() in ("verified", "pending"):
        v_status = verify_status.strip().lower()
        verified_subq = db.query(VoucherVerification.voucher_number).filter(
            VoucherVerification.voucher_number.isnot(None)
        ).scalar_subquery()
        verified_id_subq = db.query(VoucherVerification.record_id).filter(
            VoucherVerification.dataset_type == "daybook",
            VoucherVerification.record_id.isnot(None)
        ).scalar_subquery()

        if v_status == "verified":
            q = q.filter(
                or_(
                    DayBookRecord.voucher_number.in_(verified_subq),
                    DayBookRecord.id.in_(verified_id_subq)
                )
            )
        elif v_status == "pending":
            q = q.filter(
                ~DayBookRecord.voucher_number.in_(verified_subq),
                ~DayBookRecord.id.in_(verified_id_subq)
            )

    if search and search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(
            or_(
                DayBookRecord.voucher_number.ilike(term),
                DayBookRecord.party_code.ilike(term),
                DayBookRecord.party_description.ilike(term),
                DayBookRecord.account_description.ilike(term),
                DayBookRecord.narration.ilike(term),
                DayBookRecord.created_by.ilike(term),
                DayBookRecord.approved_by.ilike(term)
            )
        )

    total = q.count()

    # Sort
    col = getattr(DayBookRecord, sort_by, DayBookRecord.id)
    if sort_order.lower() == "asc":
        q = q.order_by(asc(col))
    else:
        q = q.order_by(desc(col))

    # Paginate
    records = q.offset((page - 1) * page_size).limit(page_size).all()
    return total, records


def query_ap(
    db: Session,
    page: int = 1,
    page_size: int = 15,
    search: Optional[str] = None,
    site: Optional[str] = None,
    voucher_type: Optional[str] = None,
    voucher_subtype: Optional[str] = None,
    approved_by: Optional[str] = None,
    batch_id: Optional[int] = None,
    verify_status: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc"
) -> Tuple[int, List[Dict[str, Any]]]:
    """Query AP records with linked Day Book audit fields (Narration, Created By, Approved By)"""
    q = db.query(APRecord)

    sites_list = parse_site_filter(site)
    if sites_list:
        if len(sites_list) == 1:
            q = q.filter(APRecord.accounting_site_code == sites_list[0])
        else:
            q = q.filter(APRecord.accounting_site_code.in_(sites_list))

    syns = expand_voucher_types_multi(voucher_type)
    if syns:
        q = q.filter(or_(APRecord.voucher_type.in_(syns), APRecord.voucher_sub_type.in_(syns)))

    if voucher_subtype and voucher_subtype.strip():
        q = q.filter(APRecord.voucher_sub_type == voucher_subtype.strip())

    appr_cond = build_approvers_conditions(DayBookRecord, approved_by)
    if appr_cond is not None:
        db_appr_q = db.query(DayBookRecord.voucher_number).filter(DayBookRecord.voucher_number.isnot(None), appr_cond)
        q = q.filter(APRecord.voucher_number.in_(db_appr_q.scalar_subquery()))

    if batch_id:
        q = q.filter(APRecord.batch_id == batch_id)

    # Verification status filter
    if verify_status and verify_status.strip().lower() in ("verified", "pending"):
        v_status = verify_status.strip().lower()
        verified_subq = db.query(VoucherVerification.voucher_number).filter(
            VoucherVerification.voucher_number.isnot(None)
        ).scalar_subquery()
        verified_id_subq = db.query(VoucherVerification.record_id).filter(
            VoucherVerification.dataset_type == "ap",
            VoucherVerification.record_id.isnot(None)
        ).scalar_subquery()

        if v_status == "verified":
            q = q.filter(
                or_(
                    APRecord.voucher_number.in_(verified_subq),
                    APRecord.id.in_(verified_id_subq)
                )
            )
        elif v_status == "pending":
            q = q.filter(
                ~APRecord.voucher_number.in_(verified_subq),
                ~APRecord.id.in_(verified_id_subq)
            )

    if search and search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(
            or_(
                APRecord.voucher_number.ilike(term),
                APRecord.invoice_number.ilike(term),
                APRecord.party_gst_tin.ilike(term),
                APRecord.item_service_description.ilike(term),
                APRecord.item_service_expense_account_desc.ilike(term),
                APRecord.header_narration.ilike(term),
                APRecord.detail_narration.ilike(term)
            )
        )

    total = q.count()

    # Sort
    col = getattr(APRecord, sort_by, APRecord.id)
    if sort_order.lower() == "asc":
        q = q.order_by(asc(col))
    else:
        q = q.order_by(desc(col))

    records = q.offset((page - 1) * page_size).limit(page_size).all()

    # Enrich with linked Day Book Audit details if available
    v_numbers = [r.voucher_number for r in records if r.voucher_number]
    linked_db = {}
    if v_numbers:
        db_matches = db.query(
            DayBookRecord.voucher_number,
            DayBookRecord.narration,
            DayBookRecord.created_by,
            DayBookRecord.approved_by
        ).filter(DayBookRecord.voucher_number.in_(v_numbers)).all()
        for dm in db_matches:
            if dm[0] not in linked_db:
                linked_db[dm[0]] = dm

    enriched = []
    for r in records:
        link = linked_db.get(r.voucher_number)
        # Choose narration from AP direct or Day Book
        narr = r.header_narration or r.detail_narration or (link[1] if link else None)
        created_by = link[2] if link else None
        approved_by = link[3] if link else None

        enriched.append({
            "id": r.id,
            "batch_id": r.batch_id,
            "accounting_site_code": r.accounting_site_code,
            "voucher_number": r.voucher_number,
            "voucher_type": r.voucher_type,
            "voucher_sub_type": r.voucher_sub_type,
            "party_gst_tin": r.party_gst_tin,
            "invoice_number": r.invoice_number,
            "invoice_date": r.invoice_date,
            "due_date": r.due_date,
            "item_service_description": r.item_service_description,
            "item_service_expense_account_desc": r.item_service_expense_account_desc,
            "expense_account": r.item_service_expense_account_desc,
            "booked_item_quantity": r.booked_item_quantity,
            "item_service_rate": r.item_service_rate,
            "item_service_detail_amount": r.item_service_detail_amount,
            "total_tax_amount": r.total_tax_amount,
            "total_voucher_amount": r.total_voucher_amount,
            "total_tds": r.total_tds,
            "narration": narr,
            "created_by": created_by,
            "approved_by": approved_by,
            "source_file": r.source_file,
            "upload_timestamp": r.upload_timestamp
        })

    return total, enriched

def query_ar(
    db: Session,
    page: int = 1,
    page_size: int = 15,
    search: Optional[str] = None,
    site: Optional[str] = None,
    voucher_type: Optional[str] = None,
    voucher_subtype: Optional[str] = None,
    approved_by: Optional[str] = None,
    batch_id: Optional[int] = None,
    verify_status: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc"
) -> Tuple[int, List[Dict[str, Any]]]:
    """Query AR records with linked Day Book audit fields (Narration, Created By, Approved By)"""
    q = db.query(ARRecord)

    sites_list = parse_site_filter(site)
    if sites_list:
        if len(sites_list) == 1:
            q = q.filter(ARRecord.accounting_site_code == sites_list[0])
        else:
            q = q.filter(ARRecord.accounting_site_code.in_(sites_list))

    syns = expand_voucher_types_multi(voucher_type)
    if syns:
        q = q.filter(or_(ARRecord.voucher_type.in_(syns), ARRecord.voucher_sub_type.in_(syns)))

    if voucher_subtype and voucher_subtype.strip():
        q = q.filter(ARRecord.voucher_sub_type == voucher_subtype.strip())

    appr_cond = build_approvers_conditions(DayBookRecord, approved_by)
    if appr_cond is not None:
        db_appr_q = db.query(DayBookRecord.voucher_number).filter(DayBookRecord.voucher_number.isnot(None), appr_cond)
        q = q.filter(ARRecord.voucher_number.in_(db_appr_q.scalar_subquery()))

    if batch_id:
        q = q.filter(ARRecord.batch_id == batch_id)

    # Verification status filter
    if verify_status and verify_status.strip().lower() in ("verified", "pending"):
        v_status = verify_status.strip().lower()
        verified_subq = db.query(VoucherVerification.voucher_number).filter(
            VoucherVerification.voucher_number.isnot(None)
        ).scalar_subquery()
        verified_id_subq = db.query(VoucherVerification.record_id).filter(
            VoucherVerification.dataset_type == "ar",
            VoucherVerification.record_id.isnot(None)
        ).scalar_subquery()

        if v_status == "verified":
            q = q.filter(
                or_(
                    ARRecord.voucher_number.in_(verified_subq),
                    ARRecord.id.in_(verified_id_subq)
                )
            )
        elif v_status == "pending":
            q = q.filter(
                ~ARRecord.voucher_number.in_(verified_subq),
                ~ARRecord.id.in_(verified_id_subq)
            )

    if search and search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(
            or_(
                ARRecord.voucher_number.ilike(term),
                ARRecord.item_service_description.ilike(term),
                ARRecord.narration_remarks.ilike(term)
            )
        )

    total = q.count()

    # Sort
    col = getattr(ARRecord, sort_by, ARRecord.id)
    if sort_order.lower() == "asc":
        q = q.order_by(asc(col))
    else:
        q = q.order_by(desc(col))

    records = q.offset((page - 1) * page_size).limit(page_size).all()

    # Enrich with linked Day Book Audit details if available
    v_numbers = [r.voucher_number for r in records if r.voucher_number]
    linked_db = {}
    if v_numbers:
        db_matches = db.query(
            DayBookRecord.voucher_number,
            DayBookRecord.narration,
            DayBookRecord.created_by,
            DayBookRecord.approved_by
        ).filter(DayBookRecord.voucher_number.in_(v_numbers)).all()
        for dm in db_matches:
            if dm[0] not in linked_db:
                linked_db[dm[0]] = dm

    enriched = []
    for r in records:
        link = linked_db.get(r.voucher_number)
        narr = r.narration_remarks or (link[1] if link else None)
        created_by = link[2] if link else None
        approved_by = link[3] if link else None

        enriched.append({
            "id": r.id,
            "batch_id": r.batch_id,
            "accounting_site_code": r.accounting_site_code,
            "voucher_number": r.voucher_number,
            "voucher_type": r.voucher_type,
            "voucher_sub_type": r.voucher_sub_type,
            "item_service_description": r.item_service_description,
            "item_quantity": r.item_quantity,
            "item_service_rate": r.item_service_rate,
            "item_service_amount": r.item_service_amount,
            "item_service_charges": r.item_service_charges,
            "item_amount_net_off_discount": r.item_amount_net_off_discount,
            "item_service_taxes": r.item_service_taxes,
            "net_amount": r.net_amount,
            "total_cgst": r.total_cgst,
            "total_sgst": r.total_sgst,
            "total_igst": r.total_igst,
            "narration": narr,
            "created_by": created_by,
            "approved_by": approved_by,
            "source_file": r.source_file,
            "upload_timestamp": r.upload_timestamp
        })

    return total, enriched

def get_cross_referenced_voucher(db: Session, voucher_no: str) -> Dict[str, Any]:
    """Retrieve interconnected Day Book, AP, and AR records for a given voucher number"""
    v_clean = voucher_no.strip()
    db_recs = db.query(DayBookRecord).filter(DayBookRecord.voucher_number == v_clean).all()
    ap_recs = db.query(APRecord).filter(APRecord.voucher_number == v_clean).all()
    ar_recs = db.query(ARRecord).filter(ARRecord.voucher_number == v_clean).all()

    return {
        "voucher_number": v_clean,
        "daybook_count": len(db_recs),
        "ap_count": len(ap_recs),
        "ar_count": len(ar_recs),
        "daybook_records": db_recs,
        "ap_records": ap_recs,
        "ar_records": ar_recs
    }

def query_master_360(
    db: Session,
    page: int = 1,
    page_size: int = 15,
    search: Optional[str] = None,
    site: Optional[str] = None,
    voucher_type: Optional[str] = None,
    register_type: Optional[str] = None, # 'all', 'ap', 'ar', 'daybook_only'
    approved_by: Optional[str] = None,
    batch_id: Optional[int] = None,
    verify_status: Optional[str] = None,
    sort_by: str = "id",
    sort_order: str = "desc"
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Day Book Master 360° Ledger: True Multi-Register Unified Engine.
    Expands multi-item vouchers into detailed individual item lines (retaining parent voucher metadata,
    approval status, verification, and site info) so that all multi-line items from AP and AR are 100% visible.
    """
    syns = expand_voucher_types_multi(voucher_type)
    sites_list = parse_site_filter(site)

    # 1. Base Query on DayBookRecord
    q_db = db.query(DayBookRecord)
    if sites_list:
        if len(sites_list) == 1:
            q_db = q_db.filter(DayBookRecord.transaction_site == sites_list[0])
        else:
            q_db = q_db.filter(DayBookRecord.transaction_site.in_(sites_list))

    if batch_id:
        q_db = q_db.filter(DayBookRecord.batch_id == batch_id)
    if syns:
        vt_subq_ap = db.query(APRecord.voucher_number).filter(
            or_(
                APRecord.voucher_type.in_(syns),
                APRecord.voucher_sub_type.in_(syns)
            )
        )
        if batch_id:
            vt_subq_ap = vt_subq_ap.filter(APRecord.batch_id == batch_id)
        vt_subq_ap = vt_subq_ap.scalar_subquery()

        vt_subq_ar = db.query(ARRecord.voucher_number).filter(
            or_(
                ARRecord.voucher_type.in_(syns),
                ARRecord.voucher_sub_type.in_(syns)
            )
        )
        if batch_id:
            vt_subq_ar = vt_subq_ar.filter(ARRecord.batch_id == batch_id)
        vt_subq_ar = vt_subq_ar.scalar_subquery()

        q_db = q_db.filter(
            or_(
                DayBookRecord.voucher_type.in_(syns),
                DayBookRecord.voucher_number.in_(vt_subq_ap),
                DayBookRecord.voucher_number.in_(vt_subq_ar)
            )
        )
    appr_cond = build_approvers_conditions(DayBookRecord, approved_by)
    if appr_cond is not None:
        q_db = q_db.filter(appr_cond)

    # Order DayBook query
    if sort_order.lower() == "desc":
        q_db = q_db.order_by(desc(DayBookRecord.id))
    else:
        q_db = q_db.order_by(asc(DayBookRecord.id))

    db_records = q_db.all()

    # Pre-fetch all AP and AR records matching this batch for rapid in-memory expansion
    q_all_ap = db.query(APRecord)
    q_all_ar = db.query(ARRecord)
    if batch_id:
        q_all_ap = q_all_ap.filter(APRecord.batch_id == batch_id)
        q_all_ar = q_all_ar.filter(ARRecord.batch_id == batch_id)

    ap_rows = q_all_ap.all()
    ar_rows = q_all_ar.all()

    ap_map: Dict[Tuple[str, Optional[int]], List[APRecord]] = {}
    ar_map: Dict[Tuple[str, Optional[int]], List[ARRecord]] = {}
    matched_ap_ids = set()
    matched_ar_ids = set()

    for ap in ap_rows:
        if ap.voucher_number:
            key = (ap.voucher_number, ap.batch_id)
            if key not in ap_map:
                ap_map[key] = []
            ap_map[key].append(ap)

    for ar in ar_rows:
        if ar.voucher_number:
            key = (ar.voucher_number, ar.batch_id)
            if key not in ar_map:
                ar_map[key] = []
            ar_map[key].append(ar)

    master_list = []

    # 1. Expand Day Book Records
    for dbr in db_records:
        v_no = dbr.voucher_number
        b_id = dbr.batch_id
        ap_list = ap_map.get((v_no, b_id), []) if v_no else []
        ar_list = ar_map.get((v_no, b_id), []) if v_no else []

        has_ap = len(ap_list) > 0
        has_ar = len(ar_list) > 0

        # Filter by register type if requested
        if register_type == "ap" and not has_ap:
            continue
        if register_type == "ar" and not has_ar:
            continue
        if register_type == "daybook_only" and (has_ap or has_ar):
            continue

        if has_ar and not has_ap:
            # Expand each AR item line
            for ar in ar_list:
                matched_ar_ids.add(ar.id)
                ar_tax = (ar.total_cgst or 0.0) + (ar.total_sgst or 0.0) + (ar.total_igst or 0.0)
                exp_acc = ar.voucher_sub_type or dbr.account_description or dbr.voucher_type
                master_list.append({
                    "id": f"{dbr.id}_ar_{ar.id}",
                    "batch_id": dbr.batch_id,
                    "transaction_site": dbr.transaction_site or ar.accounting_site_code,
                    "voucher_number": dbr.voucher_number,
                    "voucher_date": dbr.voucher_date,
                    "voucher_type": ar.voucher_type or dbr.voucher_type,
                    "voucher_status": dbr.voucher_status or "Verified",
                    "party_code": dbr.party_code,
                    "party_description": dbr.party_description or dbr.party_code or "",
                    "account_description": exp_acc,
                    "expense_account": exp_acc,
                    "narration": ar.narration_remarks or dbr.narration or f"Voucher transaction: {dbr.voucher_type}",
                    "created_by": dbr.created_by or "",
                    "approved_by": dbr.approved_by or "",
                    "created_date_raw": dbr.created_date_raw,
                    "approved_date_raw": dbr.approved_date_raw,
                    "source_tag": "DayBook + AR",
                    "has_ap": False,
                    "has_ar": True,
                    "ap_count": 0,
                    "ar_count": len(ar_list),
                    "unified_invoice_no": ar.voucher_number or dbr.voucher_number,
                    "unified_quantity": ar.item_quantity,
                    "unified_rate": ar.item_service_rate,
                    "combined_amount": ar.net_amount or ((ar.item_amount or 0.0) + (ar.item_charges or 0.0)),
                    "unified_tax_amount": ar_tax,
                    "unified_item_description": ar.item_service_description or dbr.account_description or dbr.voucher_type,
                    "ap_invoice_number": None,
                    "ap_party_gst": None,
                    "ap_item_description": None,
                    "ap_total_amount": None,
                    "ap_tax_amount": None,
                    "ap_total_tds": None,
                    "ar_subtype": ar.voucher_sub_type,
                    "ar_item_description": ar.item_service_description,
                    "ar_net_amount": ar.net_amount,
                    "ar_tax_amount": ar_tax,
                    "source_file": dbr.source_file,
                    "upload_timestamp": dbr.upload_timestamp
                })
        elif has_ap and not has_ar:
            # Expand each AP item line
            for ap in ap_list:
                matched_ap_ids.add(ap.id)
                exp_acc = ap.item_service_expense_account_desc or dbr.account_description or dbr.voucher_type
                master_list.append({
                    "id": f"{dbr.id}_ap_{ap.id}",
                    "batch_id": dbr.batch_id,
                    "transaction_site": dbr.transaction_site or ap.accounting_site_code,
                    "voucher_number": dbr.voucher_number,
                    "voucher_date": dbr.voucher_date,
                    "voucher_type": ap.voucher_type or dbr.voucher_type,
                    "voucher_status": dbr.voucher_status or "Verified",
                    "party_code": ap.party_gst_tin or dbr.party_code,
                    "party_description": dbr.party_description or dbr.party_code or "",
                    "account_description": exp_acc,
                    "expense_account": exp_acc,
                    "narration": ap.header_narration or ap.detail_narration or dbr.narration or f"Voucher transaction: {dbr.voucher_type}",
                    "created_by": dbr.created_by or "",
                    "approved_by": dbr.approved_by or "",
                    "created_date_raw": dbr.created_date_raw,
                    "approved_date_raw": dbr.approved_date_raw,
                    "source_tag": "DayBook + AP",
                    "has_ap": True,
                    "has_ar": False,
                    "ap_count": len(ap_list),
                    "ar_count": 0,
                    "unified_invoice_no": ap.invoice_number or dbr.voucher_number,
                    "unified_quantity": ap.booked_item_quantity,
                    "unified_rate": ap.item_service_rate,
                    "combined_amount": ap.total_voucher_amount,
                    "unified_tax_amount": ap.total_tax_amount,
                    "unified_item_description": ap.item_service_description or dbr.account_description or dbr.voucher_type,
                    "ap_invoice_number": ap.invoice_number,
                    "ap_party_gst": ap.party_gst_tin,
                    "ap_item_description": ap.item_service_description,
                    "ap_total_amount": ap.total_voucher_amount,
                    "ap_tax_amount": ap.total_tax_amount,
                    "ap_total_tds": ap.total_tds,
                    "ar_subtype": None,
                    "ar_item_description": None,
                    "ar_net_amount": None,
                    "ar_tax_amount": None,
                    "source_file": dbr.source_file,
                    "upload_timestamp": dbr.upload_timestamp
                })
        elif has_ap and has_ar:
            for ap in ap_list:
                matched_ap_ids.add(ap.id)
                exp_acc = ap.item_service_expense_account_desc or dbr.account_description
                master_list.append({
                    "id": f"{dbr.id}_ap_{ap.id}",
                    "batch_id": dbr.batch_id,
                    "transaction_site": dbr.transaction_site or ap.accounting_site_code,
                    "voucher_number": dbr.voucher_number,
                    "voucher_date": dbr.voucher_date,
                    "voucher_type": ap.voucher_type or dbr.voucher_type,
                    "voucher_status": dbr.voucher_status or "Verified",
                    "party_code": ap.party_gst_tin or dbr.party_code,
                    "party_description": dbr.party_description or dbr.party_code or "",
                    "account_description": exp_acc,
                    "expense_account": exp_acc,
                    "narration": ap.header_narration or ap.detail_narration or dbr.narration,
                    "created_by": dbr.created_by or "",
                    "approved_by": dbr.approved_by or "",
                    "created_date_raw": dbr.created_date_raw,
                    "approved_date_raw": dbr.approved_date_raw,
                    "source_tag": "DayBook + AP + AR",
                    "has_ap": True,
                    "has_ar": True,
                    "ap_count": len(ap_list),
                    "ar_count": len(ar_list),
                    "unified_invoice_no": ap.invoice_number or dbr.voucher_number,
                    "unified_quantity": ap.booked_item_quantity,
                    "unified_rate": ap.item_service_rate,
                    "combined_amount": ap.total_voucher_amount,
                    "unified_tax_amount": ap.total_tax_amount,
                    "unified_item_description": ap.item_service_description,
                    "ap_invoice_number": ap.invoice_number,
                    "ap_party_gst": ap.party_gst_tin,
                    "ap_item_description": ap.item_service_description,
                    "ap_total_amount": ap.total_voucher_amount,
                    "ap_tax_amount": ap.total_tax_amount,
                    "ap_total_tds": ap.total_tds,
                    "ar_subtype": None,
                    "ar_item_description": None,
                    "ar_net_amount": None,
                    "ar_tax_amount": None,
                    "source_file": dbr.source_file,
                    "upload_timestamp": dbr.upload_timestamp
                })
            for ar in ar_list:
                matched_ar_ids.add(ar.id)
                ar_tax = (ar.total_cgst or 0.0) + (ar.total_sgst or 0.0) + (ar.total_igst or 0.0)
                exp_acc = ar.voucher_sub_type or dbr.account_description
                master_list.append({
                    "id": f"{dbr.id}_ar_{ar.id}",
                    "batch_id": dbr.batch_id,
                    "transaction_site": dbr.transaction_site or ar.accounting_site_code,
                    "voucher_number": dbr.voucher_number,
                    "voucher_date": dbr.voucher_date,
                    "voucher_type": ar.voucher_type or dbr.voucher_type,
                    "voucher_status": dbr.voucher_status or "Verified",
                    "party_code": dbr.party_code,
                    "party_description": dbr.party_description or dbr.party_code or "",
                    "account_description": exp_acc,
                    "expense_account": exp_acc,
                    "narration": ar.narration_remarks or dbr.narration,
                    "created_by": dbr.created_by or "",
                    "approved_by": dbr.approved_by or "",
                    "created_date_raw": dbr.created_date_raw,
                    "approved_date_raw": dbr.approved_date_raw,
                    "source_tag": "DayBook + AP + AR",
                    "has_ap": True,
                    "has_ar": True,
                    "ap_count": len(ap_list),
                    "ar_count": len(ar_list),
                    "unified_invoice_no": ar.voucher_number or dbr.voucher_number,
                    "unified_quantity": ar.item_quantity,
                    "unified_rate": ar.item_service_rate,
                    "combined_amount": ar.net_amount or ((ar.item_amount or 0.0) + (ar.item_charges or 0.0)),
                    "unified_tax_amount": ar_tax,
                    "unified_item_description": ar.item_service_description,
                    "ap_invoice_number": None,
                    "ap_party_gst": None,
                    "ap_item_description": None,
                    "ap_total_amount": None,
                    "ap_tax_amount": None,
                    "ap_total_tds": None,
                    "ar_subtype": ar.voucher_sub_type,
                    "ar_item_description": ar.item_service_description,
                    "ar_net_amount": ar.net_amount,
                    "ar_tax_amount": ar_tax,
                    "source_file": dbr.source_file,
                    "upload_timestamp": dbr.upload_timestamp
                })
        else:
            # Pure Day Book entry (no AP/AR)
            exp_acc = dbr.account_description or dbr.voucher_type
            master_list.append({
                "id": dbr.id,
                "batch_id": dbr.batch_id,
                "transaction_site": dbr.transaction_site,
                "voucher_number": dbr.voucher_number,
                "voucher_date": dbr.voucher_date,
                "voucher_type": dbr.voucher_type,
                "voucher_status": dbr.voucher_status or "Verified",
                "party_code": dbr.party_code,
                "party_description": dbr.party_description or dbr.party_code or "",
                "account_description": exp_acc,
                "expense_account": exp_acc,
                "narration": dbr.narration or f"Voucher transaction: {dbr.voucher_type} - {dbr.party_description or dbr.party_code or dbr.transaction_site}",
                "created_by": dbr.created_by or "",
                "approved_by": dbr.approved_by or "",
                "created_date_raw": dbr.created_date_raw,
                "approved_date_raw": dbr.approved_date_raw,
                "source_tag": "Day Book Only",
                "has_ap": False,
                "has_ar": False,
                "ap_count": 0,
                "ar_count": 0,
                "unified_invoice_no": dbr.voucher_number,
                "unified_quantity": None,
                "unified_rate": None,
                "combined_amount": None,
                "unified_tax_amount": 0.0,
                "unified_item_description": dbr.account_description or dbr.voucher_type,
                "ap_invoice_number": None,
                "ap_party_gst": None,
                "ap_item_description": None,
                "ap_total_amount": None,
                "ap_tax_amount": None,
                "ap_total_tds": None,
                "ar_subtype": None,
                "ar_item_description": None,
                "ar_net_amount": None,
                "ar_tax_amount": None,
                "source_file": dbr.source_file,
                "upload_timestamp": dbr.upload_timestamp
            })

    # 2. Append Standalone AP Records (vouchers in AP but not in Day Book)
    if register_type != "daybook_only" and register_type != "ar" and not (approved_by and approved_by.strip()):
        for ap in ap_rows:
            if ap.id not in matched_ap_ids:
                if sites_list and ap.accounting_site_code not in sites_list:
                    continue
                if syns and (ap.voucher_type not in syns and ap.voucher_sub_type not in syns):
                    continue
                exp_acc = ap.item_service_expense_account_desc or ap.item_service_description
                master_list.append({
                    "id": f"ap_{ap.id}",
                    "batch_id": ap.batch_id,
                    "transaction_site": ap.accounting_site_code,
                    "voucher_number": ap.voucher_number,
                    "voucher_date": ap.invoice_date or (ap.upload_timestamp.strftime("%d/%m/%Y") if ap.upload_timestamp else ""),
                    "voucher_type": ap.voucher_type or "Purchase Voucher",
                    "voucher_status": "Reconciled (AP)",
                    "party_code": ap.party_gst_tin or "",
                    "party_description": ap.item_service_expense_account_desc or "Supplier / Vendor",
                    "account_description": exp_acc,
                    "expense_account": exp_acc,
                    "narration": ap.header_narration or ap.detail_narration or f"AP Entry: {ap.item_service_description}",
                    "created_by": "",
                    "approved_by": "",
                    "created_date_raw": None,
                    "approved_date_raw": None,
                    "source_tag": "AP Register Only",
                    "has_ap": True,
                    "has_ar": False,
                    "ap_count": 1,
                    "ar_count": 0,
                    "unified_invoice_no": ap.invoice_number or ap.voucher_number,
                    "unified_quantity": ap.booked_item_quantity,
                    "unified_rate": ap.item_service_rate,
                    "combined_amount": ap.total_voucher_amount,
                    "unified_tax_amount": ap.total_tax_amount,
                    "unified_item_description": ap.item_service_description,
                    "ap_invoice_number": ap.invoice_number,
                    "ap_party_gst": ap.party_gst_tin,
                    "ap_item_description": ap.item_service_description,
                    "ap_total_amount": ap.total_voucher_amount,
                    "ap_tax_amount": ap.total_tax_amount,
                    "ap_total_tds": ap.total_tds,
                    "ar_subtype": None,
                    "ar_item_description": None,
                    "ar_net_amount": None,
                    "ar_tax_amount": None,
                    "source_file": ap.source_file,
                    "upload_timestamp": ap.upload_timestamp
                })

    # 3. Append Standalone AR Records (vouchers in AR but not in Day Book)
    if register_type != "daybook_only" and register_type != "ap" and not (approved_by and approved_by.strip()):
        for ar in ar_rows:
            if ar.id not in matched_ar_ids:
                if sites_list and ar.accounting_site_code not in sites_list:
                    continue
                if syns and (ar.voucher_type not in syns and ar.voucher_sub_type not in syns):
                    continue
                ar_tax = (ar.total_cgst or 0.0) + (ar.total_sgst or 0.0) + (ar.total_igst or 0.0)
                exp_acc = ar.voucher_sub_type or ar.item_service_description
                master_list.append({
                    "id": f"ar_{ar.id}",
                    "batch_id": ar.batch_id,
                    "transaction_site": ar.accounting_site_code,
                    "voucher_number": ar.voucher_number,
                    "voucher_date": ar.upload_timestamp.strftime("%d/%m/%Y") if ar.upload_timestamp else "",
                    "voucher_type": ar.voucher_type or "Sales Invoice",
                    "voucher_status": "Reconciled (AR)",
                    "party_code": "",
                    "party_description": ar.voucher_sub_type or "Customer Account",
                    "account_description": exp_acc,
                    "expense_account": exp_acc,
                    "narration": ar.narration_remarks or f"AR Entry: {ar.item_service_description}",
                    "created_by": "",
                    "approved_by": "",
                    "created_date_raw": None,
                    "approved_date_raw": None,
                    "source_tag": "AR Register Only",
                    "has_ap": False,
                    "has_ar": True,
                    "ap_count": 0,
                    "ar_count": 1,
                    "unified_invoice_no": ar.voucher_number,
                    "unified_quantity": ar.item_quantity,
                    "unified_rate": ar.item_service_rate,
                    "combined_amount": ar.net_amount or ((ar.item_amount or 0.0) + (ar.item_charges or 0.0)),
                    "unified_tax_amount": ar_tax,
                    "unified_item_description": ar.item_service_description,
                    "ap_invoice_number": None,
                    "ap_party_gst": None,
                    "ap_item_description": None,
                    "ap_total_amount": None,
                    "ap_tax_amount": None,
                    "ap_total_tds": None,
                    "ar_subtype": ar.voucher_sub_type,
                    "ar_item_description": ar.item_service_description,
                    "ar_net_amount": ar.net_amount,
                    "ar_tax_amount": ar_tax,
                    "source_file": ar.source_file,
                    "upload_timestamp": ar.upload_timestamp
                })

    # Normalize Quantity and Rate (Accounting rule: If Quantity is absent or 0, Rate must be empty)
    for r in master_list:
        raw_q = r.get("unified_quantity")
        try:
            num_q = float(raw_q) if raw_q is not None and str(raw_q).strip() != "" else 0.0
        except (ValueError, TypeError):
            num_q = 0.0

        if num_q <= 0:
            r["unified_quantity"] = None
            r["unified_rate"] = None

    # 4. Search Filter (if search query passed)
    if search and search.strip():
        term = search.strip().lower()
        master_list = [
            r for r in master_list
            if term in str(r.get("voucher_number") or "").lower()
            or term in str(r.get("party_code") or "").lower()
            or term in str(r.get("party_description") or "").lower()
            or term in str(r.get("account_description") or "").lower()
            or term in str(r.get("unified_item_description") or "").lower()
            or term in str(r.get("unified_invoice_no") or "").lower()
            or term in str(r.get("narration") or "").lower()
            or term in str(r.get("created_by") or "").lower()
            or term in str(r.get("approved_by") or "").lower()
            or term in str(r.get("transaction_site") or "").lower()
        ]

    # 5. Verification Status Filter
    if verify_status and verify_status.strip().lower() in ("verified", "pending"):
        v_status = verify_status.strip().lower()
        verified_vnos = {
            r[0] for r in db.query(VoucherVerification.voucher_number).filter(
                VoucherVerification.voucher_number.isnot(None)
            ).all() if r[0]
        }
        verified_keys = {
            r[0] for r in db.query(VoucherVerification.identifier_key).all() if r[0]
        }
        if v_status == "verified":
            master_list = [
                r for r in master_list
                if (r.get("voucher_number") and r.get("voucher_number") in verified_vnos)
                or f"voucher_verified_master_{r.get('id')}" in verified_keys
                or f"voucher_verified_daybook_{r.get('id')}" in verified_keys
                or f"voucher_verified_ap_{r.get('id')}" in verified_keys
                or f"voucher_verified_ar_{r.get('id')}" in verified_keys
            ]
        elif v_status == "pending":
            master_list = [
                r for r in master_list
                if not (
                    (r.get("voucher_number") and r.get("voucher_number") in verified_vnos)
                    or f"voucher_verified_master_{r.get('id')}" in verified_keys
                    or f"voucher_verified_daybook_{r.get('id')}" in verified_keys
                    or f"voucher_verified_ap_{r.get('id')}" in verified_keys
                    or f"voucher_verified_ar_{r.get('id')}" in verified_keys
                )
            ]

    total = len(master_list)
    offset = (page - 1) * page_size
    paged_items = master_list[offset:offset + page_size]

    return total, paged_items

