from datetime import datetime, date
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models import DayBookRecord, APRecord, ARRecord, ImportBatch

def get_dashboard_data(db: Session) -> Dict[str, Any]:
    """Calculate all real-time stats and metrics for the dashboard with single-pass aggregated queries"""
    # 1. Day Book count
    total_db = db.query(func.count(DayBookRecord.id)).scalar() or 0

    # 2. AP aggregates (count, total amount, tax amount in 1 query)
    ap_count, ap_sum, ap_tax = db.query(
        func.count(APRecord.id),
        func.sum(APRecord.total_voucher_amount),
        func.sum(APRecord.total_tax_amount)
    ).first()
    total_ap = ap_count or 0
    ap_sum = ap_sum or 0.0
    ap_tax = ap_tax or 0.0

    # 3. AR aggregates (count, net amount, CGST, SGST, IGST in 1 query)
    ar_count, ar_sum, ar_cgst, ar_sgst, ar_igst = db.query(
        func.count(ARRecord.id),
        func.sum(ARRecord.net_amount),
        func.sum(ARRecord.total_cgst),
        func.sum(ARRecord.total_sgst),
        func.sum(ARRecord.total_igst)
    ).first()
    total_ar = ar_count or 0
    ar_sum = ar_sum or 0.0
    ar_cgst = ar_cgst or 0.0
    ar_sgst = ar_sgst or 0.0
    ar_igst = ar_igst or 0.0

    total_historical = total_db + total_ap + total_ar
    total_taxes = round(ap_tax + ar_cgst + ar_sgst + ar_igst, 2)

    # 4. Last batch details & total batches
    last_batch = db.query(ImportBatch).order_by(desc(ImportBatch.id)).first()
    last_upload_date = last_batch.upload_date_str if last_batch else None
    last_upload_time = last_batch.upload_time_str if last_batch else None
    last_batch_status = last_batch.status if last_batch else "No Uploads"
    last_batch_code = last_batch.batch_code if last_batch else None
    total_batches = db.query(func.count(ImportBatch.id)).scalar() or 0

    # 5. Today's imported records
    today_str = datetime.utcnow().strftime("%d-%b-%Y")
    today_records = db.query(func.sum(ImportBatch.new_records)).filter(
        ImportBatch.upload_date_str == today_str
    ).scalar() or 0

    # 6. Site Distribution (aggregate across Day Book, AP, AR)
    site_counts = {}
    for r in db.query(DayBookRecord.transaction_site, func.count(DayBookRecord.id)).group_by(DayBookRecord.transaction_site).all():
        if r[0]:
            site_counts[r[0]] = site_counts.get(r[0], 0) + r[1]
    for r in db.query(APRecord.accounting_site_code, func.count(APRecord.id)).group_by(APRecord.accounting_site_code).all():
        if r[0]:
            site_counts[r[0]] = site_counts.get(r[0], 0) + r[1]
    for r in db.query(ARRecord.accounting_site_code, func.count(ARRecord.id)).group_by(ARRecord.accounting_site_code).all():
        if r[0]:
            site_counts[r[0]] = site_counts.get(r[0], 0) + r[1]

    site_distribution = [{"site": k, "count": v} for k, v in sorted(site_counts.items(), key=lambda x: x[1], reverse=True)[:10]]

    # 7. Voucher Type Distribution
    vtype_counts = {}
    for r in db.query(DayBookRecord.voucher_type, func.count(DayBookRecord.id)).group_by(DayBookRecord.voucher_type).all():
        if r[0]:
            vtype_counts[r[0]] = vtype_counts.get(r[0], 0) + r[1]
    for r in db.query(APRecord.voucher_type, func.count(APRecord.id)).group_by(APRecord.voucher_type).all():
        if r[0]:
            vtype_counts[r[0]] = vtype_counts.get(r[0], 0) + r[1]
    for r in db.query(ARRecord.voucher_type, func.count(ARRecord.id)).group_by(ARRecord.voucher_type).all():
        if r[0]:
            vtype_counts[r[0]] = vtype_counts.get(r[0], 0) + r[1]

    vtype_distribution = [{"voucher_type": k, "count": v} for k, v in sorted(vtype_counts.items(), key=lambda x: x[1], reverse=True)[:10]]

    # 8. Voucher Sub-Type Distribution (AP & AR)
    vsubtype_counts = {}
    for r in db.query(APRecord.voucher_sub_type, func.count(APRecord.id)).group_by(APRecord.voucher_sub_type).all():
        if r[0]:
            vsubtype_counts[r[0]] = vsubtype_counts.get(r[0], 0) + r[1]
    for r in db.query(ARRecord.voucher_sub_type, func.count(ARRecord.id)).group_by(ARRecord.voucher_sub_type).all():
        if r[0]:
            vsubtype_counts[r[0]] = vsubtype_counts.get(r[0], 0) + r[1]

    vsubtype_distribution = [{"voucher_subtype": k, "count": v} for k, v in sorted(vsubtype_counts.items(), key=lambda x: x[1], reverse=True)[:10]]

    return {
        "total_daybook_records": total_db,
        "total_ap_records": total_ap,
        "total_ar_records": total_ar,
        "total_historical_records": total_historical,
        "today_imported_records": today_records,
        "last_upload_date": last_upload_date,
        "last_upload_time": last_upload_time,
        "last_batch_status": last_batch_status,
        "last_batch_code": last_batch_code,
        "total_batches": total_batches,
        "ap_total_amount": round(ap_sum, 2),
        "ar_total_amount": round(ar_sum, 2),
        "total_tax_collected_or_paid": total_taxes,
        "site_distribution": site_distribution,
        "voucher_type_distribution": vtype_distribution,
        "voucher_subtype_distribution": vsubtype_distribution
    }
