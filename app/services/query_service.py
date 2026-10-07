from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc, func
from app.models import DayBookRecord, APRecord, ARRecord, ImportBatch

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

    # Batch list - only show valid completed batches with data, max latest 5
    batches = db.query(ImportBatch).filter(
        ImportBatch.status == "Completed",
        ImportBatch.total_rows > 0
    ).order_by(desc(ImportBatch.id)).limit(5).all()
    batch_list = [
        {
            "id": b.id,
            "batch_code": b.batch_code,
            "date": b.upload_date_str,
            "time": b.upload_time_str,
            "status": b.status
        }
        for b in batches
    ]

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
    sort_by: str = "id",
    sort_order: str = "desc"
) -> Tuple[int, List[DayBookRecord]]:
    """Query Day Book records with server-side filters, search, and pagination"""
    q = db.query(DayBookRecord)

    if site and site.strip():
        q = q.filter(DayBookRecord.transaction_site == site.strip())
    if voucher_type and voucher_type.strip():
        syns = expand_voucher_type_synonyms(voucher_type)
        q = q.filter(DayBookRecord.voucher_type.in_(syns))
    if approved_by and approved_by.strip():
        appr = approved_by.strip()
        if appr == "approved":
            q = q.filter(
                DayBookRecord.approved_by.isnot(None),
                DayBookRecord.approved_by != "",
                DayBookRecord.approved_by != "—",
                DayBookRecord.approved_by != "-"
            )
        elif appr in ("pending", "unapproved"):
            q = q.filter(
                or_(
                    DayBookRecord.approved_by.is_(None),
                    DayBookRecord.approved_by == "",
                    DayBookRecord.approved_by == "—",
                    DayBookRecord.approved_by == "-"
                )
            )
        else:
            q = q.filter(DayBookRecord.approved_by == appr)
    if batch_id:
        q = q.filter(DayBookRecord.batch_id == batch_id)
    if date_from and date_from.strip():
        q = q.filter(DayBookRecord.voucher_date >= date_from.strip())
    if date_to and date_to.strip():
        q = q.filter(DayBookRecord.voucher_date <= date_to.strip())

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
    sort_by: str = "id",
    sort_order: str = "desc"
) -> Tuple[int, List[Dict[str, Any]]]:
    """Query AP records with linked Day Book audit fields (Narration, Created By, Approved By)"""
    q = db.query(APRecord)

    if site and site.strip():
        q = q.filter(APRecord.accounting_site_code == site.strip())
    if voucher_type and voucher_type.strip():
        syns = expand_voucher_type_synonyms(voucher_type)
        q = q.filter(or_(APRecord.voucher_type.in_(syns), APRecord.voucher_sub_type.in_(syns)))
    if voucher_subtype and voucher_subtype.strip():
        q = q.filter(APRecord.voucher_sub_type == voucher_subtype.strip())
    if approved_by and approved_by.strip():
        appr = approved_by.strip()
        db_appr_q = db.query(DayBookRecord.voucher_number).filter(DayBookRecord.voucher_number.isnot(None))
        if appr == "approved":
            db_appr_q = db_appr_q.filter(
                DayBookRecord.approved_by.isnot(None),
                DayBookRecord.approved_by != "",
                DayBookRecord.approved_by != "—",
                DayBookRecord.approved_by != "-"
            )
        elif appr in ("pending", "unapproved"):
            db_appr_q = db_appr_q.filter(
                or_(
                    DayBookRecord.approved_by.is_(None),
                    DayBookRecord.approved_by == "",
                    DayBookRecord.approved_by == "—",
                    DayBookRecord.approved_by == "-"
                )
            )
        else:
            db_appr_q = db_appr_q.filter(DayBookRecord.approved_by == appr)
        q = q.filter(APRecord.voucher_number.in_(db_appr_q.scalar_subquery()))
    if batch_id:
        q = q.filter(APRecord.batch_id == batch_id)

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
    sort_by: str = "id",
    sort_order: str = "desc"
) -> Tuple[int, List[Dict[str, Any]]]:
    """Query AR records with linked Day Book audit fields (Narration, Created By, Approved By)"""
    q = db.query(ARRecord)

    if site and site.strip():
        q = q.filter(ARRecord.accounting_site_code == site.strip())
    if voucher_type and voucher_type.strip():
        syns = expand_voucher_type_synonyms(voucher_type)
        q = q.filter(or_(ARRecord.voucher_type.in_(syns), ARRecord.voucher_sub_type.in_(syns)))
    if voucher_subtype and voucher_subtype.strip():
        q = q.filter(ARRecord.voucher_sub_type == voucher_subtype.strip())
    if approved_by and approved_by.strip():
        appr = approved_by.strip()
        db_appr_q = db.query(DayBookRecord.voucher_number).filter(DayBookRecord.voucher_number.isnot(None))
        if appr == "approved":
            db_appr_q = db_appr_q.filter(
                DayBookRecord.approved_by.isnot(None),
                DayBookRecord.approved_by != "",
                DayBookRecord.approved_by != "—",
                DayBookRecord.approved_by != "-"
            )
        elif appr in ("pending", "unapproved"):
            db_appr_q = db_appr_q.filter(
                or_(
                    DayBookRecord.approved_by.is_(None),
                    DayBookRecord.approved_by == "",
                    DayBookRecord.approved_by == "—",
                    DayBookRecord.approved_by == "-"
                )
            )
        else:
            db_appr_q = db_appr_q.filter(DayBookRecord.approved_by == appr)
        q = q.filter(ARRecord.voucher_number.in_(db_appr_q.scalar_subquery()))
    if batch_id:
        q = q.filter(ARRecord.batch_id == batch_id)

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
    sort_by: str = "id",
    sort_order: str = "desc"
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Day Book Master 360° Ledger: True Multi-Register Unified Engine.
    Aggregates Day Book (enriched with matching AP & AR), plus any standalone AP & AR records
    so that if Day Book data is absent or AP/AR contains extra data, it is 100% visible and filterable.
    """
    syns = expand_voucher_type_synonyms(voucher_type) if (voucher_type and voucher_type.strip()) else []

    # 1. Base Query on DayBookRecord
    q_db = db.query(DayBookRecord)
    if site and site.strip():
        q_db = q_db.filter(DayBookRecord.transaction_site == site.strip())
    if syns:
        vt_subq_ap = db.query(APRecord.voucher_number).filter(
            or_(
                APRecord.voucher_type.in_(syns),
                APRecord.voucher_sub_type.in_(syns)
            )
        ).scalar_subquery()
        vt_subq_ar = db.query(ARRecord.voucher_number).filter(
            or_(
                ARRecord.voucher_type.in_(syns),
                ARRecord.voucher_sub_type.in_(syns)
            )
        ).scalar_subquery()
        q_db = q_db.filter(
            or_(
                DayBookRecord.voucher_type.in_(syns),
                DayBookRecord.voucher_number.in_(vt_subq_ap),
                DayBookRecord.voucher_number.in_(vt_subq_ar)
            )
        )
    if approved_by and approved_by.strip():
        appr = approved_by.strip()
        if appr == "approved":
            q_db = q_db.filter(
                DayBookRecord.approved_by.isnot(None),
                DayBookRecord.approved_by != "",
                DayBookRecord.approved_by != "—",
                DayBookRecord.approved_by != "-"
            )
        elif appr in ("pending", "unapproved"):
            q_db = q_db.filter(
                or_(
                    DayBookRecord.approved_by.is_(None),
                    DayBookRecord.approved_by == "",
                    DayBookRecord.approved_by == "—",
                    DayBookRecord.approved_by == "-"
                )
            )
        else:
            q_db = q_db.filter(DayBookRecord.approved_by == appr)
    if batch_id:
        q_db = q_db.filter(DayBookRecord.batch_id == batch_id)

    # Filter by linked register type
    if register_type == "ap":
        ap_vouchers_subq = db.query(APRecord.voucher_number).filter(APRecord.voucher_number.isnot(None)).scalar_subquery()
        q_db = q_db.filter(DayBookRecord.voucher_number.in_(ap_vouchers_subq))
    elif register_type == "ar":
        ar_vouchers_subq = db.query(ARRecord.voucher_number).filter(ARRecord.voucher_number.isnot(None)).scalar_subquery()
        q_db = q_db.filter(DayBookRecord.voucher_number.in_(ar_vouchers_subq))
    elif register_type == "daybook_only":
        ap_vouchers_subq = db.query(APRecord.voucher_number).filter(APRecord.voucher_number.isnot(None)).scalar_subquery()
        ar_vouchers_subq = db.query(ARRecord.voucher_number).filter(ARRecord.voucher_number.isnot(None)).scalar_subquery()
        q_db = q_db.filter(
            ~DayBookRecord.voucher_number.in_(ap_vouchers_subq),
            ~DayBookRecord.voucher_number.in_(ar_vouchers_subq)
        )

    if search and search.strip():
        term = f"%{search.strip()}%"
        q_db = q_db.filter(
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

    db_total = q_db.count()

    # 2. Query Standalone AP Records (vouchers in AP but not in Day Book)
    all_db_v_subq = db.query(DayBookRecord.voucher_number).filter(DayBookRecord.voucher_number.isnot(None)).scalar_subquery()
    include_standalone_ap = (register_type != "daybook_only" and register_type != "ar")
    
    q_ap_standalone = None
    ap_standalone_total = 0
    if include_standalone_ap:
        q_ap_standalone = db.query(APRecord).filter(~APRecord.voucher_number.in_(all_db_v_subq))
        if site and site.strip():
            q_ap_standalone = q_ap_standalone.filter(APRecord.accounting_site_code == site.strip())
        if syns:
            q_ap_standalone = q_ap_standalone.filter(or_(APRecord.voucher_type.in_(syns), APRecord.voucher_sub_type.in_(syns)))
        if batch_id:
            q_ap_standalone = q_ap_standalone.filter(APRecord.batch_id == batch_id)
        if search and search.strip():
            term = f"%{search.strip()}%"
            q_ap_standalone = q_ap_standalone.filter(
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
        ap_standalone_total = q_ap_standalone.count()

    # 3. Query Standalone AR Records (vouchers in AR but not in Day Book)
    include_standalone_ar = (register_type != "daybook_only" and register_type != "ap")
    q_ar_standalone = None
    ar_standalone_total = 0
    if include_standalone_ar:
        q_ar_standalone = db.query(ARRecord).filter(~ARRecord.voucher_number.in_(all_db_v_subq))
        if site and site.strip():
            q_ar_standalone = q_ar_standalone.filter(ARRecord.accounting_site_code == site.strip())
        if syns:
            q_ar_standalone = q_ar_standalone.filter(or_(ARRecord.voucher_type.in_(syns), ARRecord.voucher_sub_type.in_(syns)))
        if batch_id:
            q_ar_standalone = q_ar_standalone.filter(ARRecord.batch_id == batch_id)
        if search and search.strip():
            term = f"%{search.strip()}%"
            q_ar_standalone = q_ar_standalone.filter(
                or_(
                    ARRecord.voucher_number.ilike(term),
                    ARRecord.item_service_description.ilike(term),
                    ARRecord.narration_remarks.ilike(term)
                )
            )
        ar_standalone_total = q_ar_standalone.count()

    total = db_total + ap_standalone_total + ar_standalone_total

    # Sort Day Book base query
    if sort_by == "id":
        ap_subq = db.query(APRecord.voucher_number).filter(APRecord.voucher_number.isnot(None)).scalar_subquery()
        ar_subq = db.query(ARRecord.voucher_number).filter(ARRecord.voucher_number.isnot(None)).scalar_subquery()
        has_match = or_(
            DayBookRecord.voucher_number.in_(ap_subq),
            DayBookRecord.voucher_number.in_(ar_subq)
        )
        if sort_order.lower() == "desc":
            q_db = q_db.order_by(has_match.desc(), desc(DayBookRecord.id))
        else:
            q_db = q_db.order_by(has_match.desc(), asc(DayBookRecord.id))
    else:
        col = getattr(DayBookRecord, sort_by, DayBookRecord.id)
        if sort_order.lower() == "asc":
            q_db = q_db.order_by(asc(col))
        else:
            q_db = q_db.order_by(desc(col))

    # Pagination handling across combined datasets
    offset = (page - 1) * page_size
    db_records = []
    ap_records = []
    ar_records = []

    if offset < db_total:
        db_records = q_db.offset(offset).limit(page_size).all()
        slots_left = page_size - len(db_records)
        
        if slots_left > 0 and q_ap_standalone is not None and ap_standalone_total > 0:
            ap_records = q_ap_standalone.limit(slots_left).all()
            slots_left -= len(ap_records)
            
        if slots_left > 0 and q_ar_standalone is not None and ar_standalone_total > 0:
            ar_records = q_ar_standalone.limit(slots_left).all()
    else:
        ap_offset = offset - db_total
        if ap_offset < ap_standalone_total and q_ap_standalone is not None:
            ap_records = q_ap_standalone.offset(ap_offset).limit(page_size).all()
            slots_left = page_size - len(ap_records)
            if slots_left > 0 and q_ar_standalone is not None and ar_standalone_total > 0:
                ar_records = q_ar_standalone.limit(slots_left).all()
        else:
            ar_offset = ap_offset - ap_standalone_total
            if q_ar_standalone is not None:
                ar_records = q_ar_standalone.offset(ar_offset).limit(page_size).all()

    # Collect voucher numbers for current page DayBook records to bulk fetch AP and AR
    v_numbers = [r.voucher_number for r in db_records if r.voucher_number]
    ap_map: Dict[str, List[APRecord]] = {}
    ar_map: Dict[str, List[ARRecord]] = {}

    if v_numbers:
        matched_ap = db.query(APRecord).filter(APRecord.voucher_number.in_(v_numbers)).all()
        for ap in matched_ap:
            if ap.voucher_number not in ap_map:
                ap_map[ap.voucher_number] = []
            ap_map[ap.voucher_number].append(ap)

        matched_ar = db.query(ARRecord).filter(ARRecord.voucher_number.in_(v_numbers)).all()
        for ar in matched_ar:
            if ar.voucher_number not in ar_map:
                ar_map[ar.voucher_number] = []
            ar_map[ar.voucher_number].append(ar)

    master_list = []

    # 1. Format Day Book records
    for dbr in db_records:
        v_no = dbr.voucher_number
        ap_list = ap_map.get(v_no, [])
        ar_list = ar_map.get(v_no, [])

        has_ap = len(ap_list) > 0
        has_ar = len(ar_list) > 0

        # Aggregate AP details
        ap_total_amt = sum((ap.total_voucher_amount or 0.0) for ap in ap_list) if ap_list else None
        ap_tax_amt = sum((ap.total_tax_amount or 0.0) for ap in ap_list) if ap_list else None
        ap_tds_amt = sum((ap.total_tds or 0.0) for ap in ap_list) if ap_list else None
        ap_qty = sum((ap.booked_item_quantity or 0.0) for ap in ap_list) if ap_list else None
        ap_rate = ap_list[0].item_service_rate if (ap_list and ap_list[0].item_service_rate is not None) else None
        ap_invoices = ", ".join(sorted(list(set(ap.invoice_number for ap in ap_list if ap.invoice_number)))) if ap_list else None
        ap_items = ", ".join(sorted(list(set(ap.item_service_description for ap in ap_list if ap.item_service_description)))) if ap_list else None
        ap_gst = ap_list[0].party_gst_tin if ap_list and ap_list[0].party_gst_tin else None

        # Aggregate AR details
        ar_net_amt = sum((ar.net_amount or 0.0) for ar in ar_list) if ar_list else None
        ar_tax_amt = sum(((ar.total_cgst or 0.0) + (ar.total_sgst or 0.0) + (ar.total_igst or 0.0)) for ar in ar_list) if ar_list else None
        ar_qty = sum((ar.item_quantity or 0.0) for ar in ar_list) if ar_list else None
        ar_rate = ar_list[0].item_service_rate if (ar_list and ar_list[0].item_service_rate is not None) else None
        ar_subtypes = ", ".join(sorted(list(set(ar.voucher_sub_type for ar in ar_list if ar.voucher_sub_type)))) if ar_list else None
        ar_items = ", ".join(sorted(list(set(ar.item_service_description for ar in ar_list if ar.item_service_description)))) if ar_list else None

        # Determine Primary Amount & Tax & Qty & Rate
        combined_amount = None
        if ap_total_amt is not None and ar_net_amt is not None:
            combined_amount = ap_total_amt + ar_net_amt
        elif ap_total_amt is not None:
            combined_amount = ap_total_amt
        elif ar_net_amt is not None:
            combined_amount = ar_net_amt

        combined_tax = None
        if ap_tax_amt is not None and ar_tax_amt is not None:
            combined_tax = ap_tax_amt + ar_tax_amt
        elif ap_tax_amt is not None:
            combined_tax = ap_tax_amt
        elif ar_tax_amt is not None:
            combined_tax = ar_tax_amt
        else:
            combined_tax = 0.0

        combined_qty = ap_qty if ap_qty is not None else ar_qty
        combined_rate = ap_rate if ap_rate is not None else ar_rate

        # Smart fallback fields
        unified_invoice = ap_invoices or (ar_list[0].voucher_number if ar_list else dbr.voucher_number)
        unified_item = ap_items or ar_items or (dbr.account_description if dbr.account_description else dbr.voucher_type)
        unified_account = dbr.account_description or (ap_list[0].item_service_expense_account_desc if ap_list and ap_list[0].item_service_expense_account_desc else dbr.party_description or dbr.voucher_type)
        
        ap_narr_candidate = (ap_list[0].header_narration or ap_list[0].detail_narration) if ap_list else None
        ar_narr_candidate = ar_list[0].narration_remarks if ar_list else None
        unified_narr = dbr.narration or ap_narr_candidate or ar_narr_candidate or f"Voucher transaction: {dbr.voucher_type} - {dbr.party_description or dbr.party_code or dbr.transaction_site}"

        if has_ap and has_ar:
            source_tag = "DayBook + AP + AR"
        elif has_ap:
            source_tag = "DayBook + AP"
        elif has_ar:
            source_tag = "DayBook + AR"
        else:
            source_tag = "Day Book Only"

        master_list.append({
            "id": dbr.id,
            "batch_id": dbr.batch_id,
            "transaction_site": dbr.transaction_site,
            "voucher_number": dbr.voucher_number,
            "voucher_date": dbr.voucher_date,
            "voucher_type": dbr.voucher_type,
            "voucher_status": dbr.voucher_status or "Verified",
            "party_code": dbr.party_code,
            "party_description": dbr.party_description or dbr.party_code or "—",
            "account_description": unified_account,
            "narration": unified_narr,
            "created_by": dbr.created_by or "—",
            "approved_by": dbr.approved_by or "—",
            "created_date_raw": dbr.created_date_raw,
            "approved_date_raw": dbr.approved_date_raw,
            "source_tag": source_tag,
            "has_ap": has_ap,
            "has_ar": has_ar,
            "ap_count": len(ap_list),
            "ar_count": len(ar_list),
            "unified_invoice_no": unified_invoice,
            "unified_quantity": combined_qty,
            "unified_rate": combined_rate,
            "combined_amount": combined_amount,
            "unified_tax_amount": combined_tax,
            "unified_item_description": unified_item,
            "ap_invoice_number": ap_invoices,
            "ap_party_gst": ap_gst,
            "ap_item_description": ap_items,
            "ap_total_amount": ap_total_amt,
            "ap_tax_amount": ap_tax_amt,
            "ap_total_tds": ap_tds_amt,
            "ar_subtype": ar_subtypes,
            "ar_item_description": ar_items,
            "ar_net_amount": ar_net_amt,
            "ar_tax_amount": ar_tax_amt,
            "source_file": dbr.source_file,
            "upload_timestamp": dbr.upload_timestamp
        })

    # 2. Format Standalone AP records (if any)
    for ap in ap_records:
        master_list.append({
            "id": ap.id,
            "batch_id": ap.batch_id,
            "transaction_site": ap.accounting_site_code,
            "voucher_number": ap.voucher_number,
            "voucher_date": ap.invoice_date or (ap.upload_timestamp.strftime("%d/%m/%Y") if ap.upload_timestamp else "—"),
            "voucher_type": ap.voucher_type or "Purchase Voucher",
            "voucher_status": "Reconciled (AP)",
            "party_code": ap.party_gst_tin or "—",
            "party_description": ap.item_service_expense_account_desc or "Supplier / Vendor",
            "account_description": ap.item_service_expense_account_desc or ap.item_service_description,
            "narration": ap.header_narration or ap.detail_narration or f"AP Entry: {ap.item_service_description}",
            "created_by": "—",
            "approved_by": "—",
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

    # 3. Format Standalone AR records (if any)
    for ar in ar_records:
        ar_tax = (ar.total_cgst or 0.0) + (ar.total_sgst or 0.0) + (ar.total_igst or 0.0)
        master_list.append({
            "id": ar.id,
            "batch_id": ar.batch_id,
            "transaction_site": ar.accounting_site_code,
            "voucher_number": ar.voucher_number,
            "voucher_date": ar.upload_timestamp.strftime("%d/%m/%Y") if ar.upload_timestamp else "—",
            "voucher_type": ar.voucher_type or "Sales Invoice",
            "voucher_status": "Reconciled (AR)",
            "party_code": "—",
            "party_description": ar.voucher_sub_type or "Customer",
            "account_description": ar.item_service_description or ar.voucher_sub_type,
            "narration": ar.narration_remarks or f"AR Entry: {ar.item_service_description}",
            "created_by": "—",
            "approved_by": "—",
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
            "combined_amount": ar.net_amount,
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

    return total, master_list
