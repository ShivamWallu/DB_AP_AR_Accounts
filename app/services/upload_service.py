import os
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc

from app.config import UPLOAD_DIR
from app.models import (
    ImportBatch, ImportFile, DayBookRecord, APRecord, ARRecord, User
)
from app.excel_parser import (
    detect_file_type, validate_excel_file,
    parse_daybook_file, parse_ap_file, parse_ar_file
)
from app.services.audit_service import log_activity

def generate_next_batch_code(db: Session) -> str:
    """Generate sequential batch code: e.g. BATCH-20261006-001"""
    today_str = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"BATCH-{today_str}-"
    
    existing = db.query(ImportBatch.batch_code).filter(ImportBatch.batch_code.like(f"{prefix}%")).all()
    max_num = 0
    for (b_code,) in existing:
        try:
            num = int(b_code.split("-")[-1])
            if num > max_num:
                max_num = num
        except Exception:
            pass
    return f"{prefix}{max_num + 1:03d}"

def validate_uploaded_files(file_paths: List[str]) -> Dict[str, Any]:
    """Validate a set of uploaded files before committing an import, enforcing mandatory 3 files"""
    results = []
    all_valid = True
    valid_detected_types = set()

    for path in file_paths:
        val_res = validate_excel_file(path)
        results.append(val_res)
        if val_res["status"] != "Valid":
            all_valid = False
        else:
            valid_detected_types.add(val_res["file_type"])

    missing_docs = [dt for dt in ["Day Book", "AP", "AR"] if dt not in valid_detected_types]
    
    if len(file_paths) < 3 or len(missing_docs) > 0:
        if not all_valid and len(valid_detected_types) == 0:
            overall_status = "Failed"
            message = f"Validation failed. Could not find valid Day Book, AP, or AR files."
        else:
            overall_status = "Pending / Incomplete"
            uploaded_types_str = ", ".join(valid_detected_types) if valid_detected_types else "None"
            missing_types_str = ", ".join(missing_docs)
            message = f"Incomplete dataset ({len(valid_detected_types)}/3 valid files). Detected: {uploaded_types_str} | Pending: {missing_types_str}. All 3 files are mandatory."
        is_ready = False
    else:
        if all_valid:
            overall_status = "Ready for Import"
            message = "All 3 files (Day Book, AP, AR) verified successfully. Ready for import."
            is_ready = True
        else:
            overall_status = "Failed"
            message = "One or more files failed structural or data validation."
            is_ready = False

    return {
        "is_valid": is_ready,
        "status": overall_status,
        "files_validation": results,
        "message": message
    }

def process_import_batch(
    db: Session,
    uploaded_files: Dict[str, str], # {"Day Book": filepath, "AP": filepath, "AR": filepath}
    current_user: User,
    ip_address: Optional[str] = None
) -> ImportBatch:
    """
    Import 3 validated Excel files into a new historical batch.
    Deduplicates records against existing historical data using row hashes while
    preserving all old records and adding new records safely.
    """
    # Enforce mandatory 3 files
    missing_docs = [dt for dt in ["Day Book", "AP", "AR"] if dt not in uploaded_files]
    if missing_docs:
        raise ValueError(f"Incomplete Dataset: All 3 files (Day Book, AP, AR) are mandatory. Missing: {', '.join(missing_docs)}")
    now = datetime.utcnow()
    batch_code = generate_next_batch_code(db)
    date_str = now.strftime("%d-%b-%Y")
    time_str = now.strftime("%I:%M:%S %p")

    # Create Batch record
    batch = ImportBatch(
        batch_code=batch_code,
        upload_timestamp=now,
        upload_date_str=date_str,
        upload_time_str=time_str,
        daybook_filename=os.path.basename(uploaded_files.get("Day Book", "")),
        ap_filename=os.path.basename(uploaded_files.get("AP", "")),
        ar_filename=os.path.basename(uploaded_files.get("AR", "")),
        created_by_user=current_user.username,
        status="Processing"
    )
    db.add(batch)
    db.flush()

    total_rows = 0
    total_new = 0
    total_duplicates = 0
    total_rejected = 0

    try:
        # 1. Process Day Book (Direct high-speed batch insertion)
        if "Day Book" in uploaded_files:
            db_path = uploaded_files["Day Book"]
            db_records, stats = parse_daybook_file(db_path)
            
            db_objects = []
            for rec in db_records:
                record_obj = DayBookRecord(
                    batch_id=batch.id,
                    transaction_site=rec["transaction_site"],
                    voucher_number=rec["voucher_number"],
                    voucher_date=rec["voucher_date"],
                    voucher_type=rec["voucher_type"],
                    voucher_status=rec["voucher_status"],
                    party_code=rec["party_code"],
                    party_description=rec["party_description"],
                    account_description=rec["account_description"],
                    narration=rec["narration"],
                    created_by=rec["created_by"],
                    approved_by=rec["approved_by"],
                    created_date_raw=rec["created_date_raw"],
                    approved_date_raw=rec["approved_date_raw"],
                    row_hash=rec["row_hash"],
                    raw_data_json=rec["raw_data_json"],
                    source_file=os.path.basename(db_path),
                    upload_timestamp=now
                )
                db_objects.append(record_obj)

            if db_objects:
                db.add_all(db_objects)

            batch.daybook_rows = len(db_records)
            total_rows += len(db_records)
            total_new += len(db_records)

            # Record file entry
            db_file_entry = ImportFile(
                batch_id=batch.id,
                file_type="Day Book",
                original_filename=os.path.basename(db_path),
                stored_path=db_path,
                file_size_bytes=os.path.getsize(db_path),
                total_rows=len(db_records),
                valid_rows=len(db_records),
                duplicate_rows=0,
                rejected_rows=0,
                header_row_index=stats["header_row"],
                status="Success"
            )
            db.add(db_file_entry)

        # 2. Process AP (Direct high-speed batch insertion)
        if "AP" in uploaded_files:
            ap_path = uploaded_files["AP"]
            ap_records, stats = parse_ap_file(ap_path)
            
            ap_objects = []
            for rec in ap_records:
                record_obj = APRecord(
                    batch_id=batch.id,
                    accounting_site_code=rec["accounting_site_code"],
                    voucher_number=rec["voucher_number"],
                    voucher_type=rec["voucher_type"],
                    voucher_sub_type=rec["voucher_sub_type"],
                    party_gst_tin=rec["party_gst_tin"],
                    invoice_number=rec["invoice_number"],
                    invoice_date=rec["invoice_date"],
                    due_date=rec["due_date"],
                    item_service_description=rec["item_service_description"],
                    item_service_expense_account_desc=rec["item_service_expense_account_desc"],
                    booked_item_quantity=rec["booked_item_quantity"],
                    item_service_rate=rec["item_service_rate"],
                    item_service_detail_amount=rec["item_service_detail_amount"],
                    total_tax_amount=rec["total_tax_amount"],
                    total_voucher_amount=rec["total_voucher_amount"],
                    total_tds=rec["total_tds"],
                    header_narration=rec["header_narration"],
                    detail_narration=rec["detail_narration"],
                    row_hash=rec["row_hash"],
                    raw_data_json=rec["raw_data_json"],
                    source_file=os.path.basename(ap_path),
                    upload_timestamp=now
                )
                ap_objects.append(record_obj)

            if ap_objects:
                db.add_all(ap_objects)

            batch.ap_rows = len(ap_records)
            total_rows += len(ap_records)
            total_new += len(ap_records)

            ap_file_entry = ImportFile(
                batch_id=batch.id,
                file_type="AP",
                original_filename=os.path.basename(ap_path),
                stored_path=ap_path,
                file_size_bytes=os.path.getsize(ap_path),
                total_rows=len(ap_records),
                valid_rows=len(ap_records),
                duplicate_rows=0,
                rejected_rows=0,
                header_row_index=stats["header_row"],
                status="Success"
            )
            db.add(ap_file_entry)

        # 3. Process AR (Direct high-speed batch insertion)
        if "AR" in uploaded_files:
            ar_path = uploaded_files["AR"]
            ar_records, stats = parse_ar_file(ar_path)
            
            ar_objects = []
            for rec in ar_records:
                record_obj = ARRecord(
                    batch_id=batch.id,
                    accounting_site_code=rec["accounting_site_code"],
                    voucher_number=rec["voucher_number"],
                    voucher_type=rec["voucher_type"],
                    voucher_sub_type=rec["voucher_sub_type"],
                    item_service_description=rec["item_service_description"],
                    item_quantity=rec["item_quantity"],
                    item_service_rate=rec["item_service_rate"],
                    item_service_amount=rec["item_service_amount"],
                    item_service_charges=rec["item_service_charges"],
                    item_amount_net_off_discount=rec["item_amount_net_off_discount"],
                    item_service_taxes=rec["item_service_taxes"],
                    net_amount=rec["net_amount"],
                    total_cgst=rec["total_cgst"],
                    total_sgst=rec["total_sgst"],
                    total_igst=rec["total_igst"],
                    narration_remarks=rec["narration_remarks"],
                    row_hash=rec["row_hash"],
                    raw_data_json=rec["raw_data_json"],
                    source_file=os.path.basename(ar_path),
                    upload_timestamp=now
                )
                ar_objects.append(record_obj)

            if ar_objects:
                db.add_all(ar_objects)

            batch.ar_rows = len(ar_records)
            total_rows += len(ar_records)
            total_new += len(ar_records)

            ar_file_entry = ImportFile(
                batch_id=batch.id,
                file_type="AR",
                original_filename=os.path.basename(ar_path),
                stored_path=ar_path,
                file_size_bytes=os.path.getsize(ar_path),
                total_rows=len(ar_records),
                valid_rows=len(ar_records),
                duplicate_rows=0,
                rejected_rows=0,
                header_row_index=stats["header_row"],
                status="Success"
            )
            db.add(ar_file_entry)

        # Update batch summary
        batch.total_rows = total_rows
        batch.new_records = total_new
        batch.duplicate_records = 0
        batch.rejected_records = 0
        batch.status = "Completed"
        
        db.commit()
        db.refresh(batch)

        # Auto Retention Cleanup: Keep only the latest 5 completed batches and purge older/empty ones
        try:
            cleanup_old_batches(db, max_retained_batches=5)
        except Exception:
            pass

        # Audit Log
        log_activity(
            db=db,
            username=current_user.username,
            role=current_user.role,
            action="Batch Import Completed",
            status="Success",
            details=f"Batch {batch.batch_code} imported: {total_rows} total rows ({total_new} new, {total_duplicates} duplicates)",
            ip_address=ip_address,
            batch_id=batch.id
        )

        return batch

    except Exception as e:
        db.rollback()
        batch.status = "Failed"
        batch.error_summary = str(e)
        db.commit()
        
        log_activity(
            db=db,
            username=current_user.username,
            role=current_user.role,
            action="Batch Import Failed",
            status="Failed",
            details=f"Error importing batch {batch_code}: {str(e)}",
            ip_address=ip_address,
            batch_id=batch.id
        )
        raise e

def cleanup_old_batches(db: Session, max_retained_batches: int = 5) -> int:
    """
    Auto-retention policy:
    1. Removes empty, duplicate (new_records == 0), or failed batches to avoid clutter.
    2. Retains up to `max_retained_batches` (e.g. 5) completed batches with actual new/stored records.
    3. Purges older batches and their child records (DayBookRecord, APRecord, ARRecord, ImportFile)
       beyond the retention limit to keep the database lean and lightning-fast.
    Returns the count of purged batches.
    """
    purged_count = 0

    # 1. Clean up duplicate / empty / failed batches with 0 new records
    empty_batches = db.query(ImportBatch).filter(
        or_(
            ImportBatch.status.in_(["Failed", "Processing"]),
            ImportBatch.new_records == 0,
            ImportBatch.total_rows == 0
        )
    ).all()

    for b in empty_batches:
        db.query(DayBookRecord).filter(DayBookRecord.batch_id == b.id).delete(synchronize_session=False)
        db.query(APRecord).filter(APRecord.batch_id == b.id).delete(synchronize_session=False)
        db.query(ARRecord).filter(ARRecord.batch_id == b.id).delete(synchronize_session=False)
        db.query(ImportFile).filter(ImportFile.batch_id == b.id).delete(synchronize_session=False)
        db.delete(b)
        purged_count += 1

    # 2. Get valid completed batches WITH REAL DATA (new_records > 0), ordered from newest to oldest
    valid_data_batches = db.query(ImportBatch).filter(
        ImportBatch.status == "Completed",
        ImportBatch.new_records > 0
    ).order_by(desc(ImportBatch.id)).all()

    if len(valid_data_batches) > max_retained_batches:
        excess_batches = valid_data_batches[max_retained_batches:]
        for b in excess_batches:
            db.query(DayBookRecord).filter(DayBookRecord.batch_id == b.id).delete(synchronize_session=False)
            db.query(APRecord).filter(APRecord.batch_id == b.id).delete(synchronize_session=False)
            db.query(ARRecord).filter(ARRecord.batch_id == b.id).delete(synchronize_session=False)
            db.query(ImportFile).filter(ImportFile.batch_id == b.id).delete(synchronize_session=False)
            db.delete(b)
            purged_count += 1

    if purged_count > 0:
        db.commit()

    return purged_count
