import os
import shutil
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR
from app.database import get_db
from app.models import User, ImportBatch, ImportFile, DayBookRecord
from app.auth import get_current_user
from app.excel_parser import validate_daybook_file, parse_daybook_file, DAYBOOK_COLUMNS_44
from app.services.upload_service import generate_next_batch_code
from app.services.audit_service import log_activity

router = APIRouter(prefix="/api/daybook", tags=["Day Book Operations"])

@router.post("/validate")
async def validate_daybook_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Validates a Day Book Excel file before committing:
    - Verifies Excel format (.xlsx, .xls)
    - Validates all 44 original columns in the exact sequence
    - Runs 3-way date logic verification (V = A, C = A, V = C, etc.)
    - Checks duplicate transactions against active database
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format for '{file.filename}'. Only Excel (.xlsx, .xls) files are supported."
        )

    temp_dir = UPLOAD_DIR / "temp_daybook_val"
    temp_dir.mkdir(exist_ok=True, parents=True)
    temp_path = temp_dir / file.filename

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        validation_result = validate_daybook_file(str(temp_path))
        return validation_result

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to validate Day Book Excel file: {str(e)}")
    finally:
        if temp_path.exists():
            try:
                os.remove(temp_path)
            except Exception:
                pass


@router.post("/upload")
async def upload_and_save_daybook(
    file: UploadFile = File(...),
    req: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Uploads, validates, deduplicates, and saves Day Book transactions into the database.
    - Preserves all 44 original Excel columns in exact sequence.
    - Computes validation status for every record.
    - Skips duplicate transactions using business deduplication hash.
    - Updates Day Book Dashboard immediately.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format for '{file.filename}'. Only Excel (.xlsx, .xls) files are supported."
        )

    now = datetime.utcnow()
    date_str = now.strftime("%d/%m/%Y")
    time_str = now.strftime("%I:%M %p")
    batch_ts = int(now.timestamp())
    batch_dir = UPLOAD_DIR / f"daybook_upload_{batch_ts}"
    batch_dir.mkdir(exist_ok=True, parents=True)
    saved_path = batch_dir / file.filename

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Parse and validate Day Book records
        records, stats = parse_daybook_file(str(saved_path))
        if not records:
            raise HTTPException(status_code=400, detail="The uploaded Day Book Excel file contains no valid data rows.")

        # 2. Check for duplicate transactions across database
        existing_hashes = set(
            h[0] for h in db.query(DayBookRecord.row_hash).all()
        )

        db_objects = []
        new_records_count = 0
        duplicate_records_count = 0

        # Unique voucher dates for batch date range
        unique_vdates = []

        for rec in records:
            r_hash = rec["row_hash"]
            if r_hash in existing_hashes:
                duplicate_records_count += 1
                continue

            existing_hashes.add(r_hash)
            new_records_count += 1

            vd = rec.get("voucher_date")
            if vd and str(vd).strip() and str(vd).strip() not in ("None", "-", "—", "null", "undefined"):
                vd_clean = str(vd).strip()
                if vd_clean not in unique_vdates:
                    unique_vdates.append(vd_clean)

        # 3. Create or attach batch
        batch_code = generate_next_batch_code(db)
        vdate_range = (
            unique_vdates[0] if len(unique_vdates) == 1
            else (f"{unique_vdates[0]} to {unique_vdates[-1]}" if len(unique_vdates) > 1 else date_str)
        )

        batch = ImportBatch(
            batch_code=batch_code,
            upload_timestamp=now,
            upload_date_str=date_str,
            upload_time_str=time_str,
            daybook_filename=file.filename,
            voucher_date_range=vdate_range,
            total_rows=len(records),
            daybook_rows=new_records_count,
            new_records=new_records_count,
            duplicate_records=duplicate_records_count,
            created_by_user=current_user.username,
            status="Completed"
        )
        db.add(batch)
        db.flush()

        # 4. Save new records
        for rec in records:
            r_hash = rec["row_hash"]
            # Only add records that are new
            # If all are duplicates, we record the batch but skip duplicates
            if new_records_count > 0 and r_hash not in [o.row_hash for o in db_objects]:
                # Check if it was marked as duplicate
                # We can re-check against initial existing_hashes or track newly added
                pass

        # Build objects for new records
        tracked_hashes = set(
            h[0] for h in db.query(DayBookRecord.row_hash).all()
        )
        for rec in records:
            if rec["row_hash"] not in tracked_hashes:
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
                    validation_status=rec.get("validation_status", "Pending / Check Dates"),
                    row_hash=rec["row_hash"],
                    raw_data_json=rec["raw_data_json"],
                    source_file=file.filename,
                    upload_timestamp=now
                )
                db_objects.append(record_obj)
                tracked_hashes.add(rec["row_hash"])

        if db_objects:
            db.add_all(db_objects)

        # 5. Record file entry
        file_size = os.path.getsize(str(saved_path))
        import_file = ImportFile(
            batch_id=batch.id,
            file_type="Day Book",
            original_filename=file.filename,
            stored_path=str(saved_path),
            file_size_bytes=file_size,
            total_rows=len(records),
            valid_rows=new_records_count,
            duplicate_rows=duplicate_records_count,
            rejected_rows=0,
            status="Success"
        )
        db.add(import_file)
        db.commit()

        # Audit activity
        ip = req.client.host if req and req.client else "127.0.0.1"
        try:
            log_activity(
                db=db,
                username=current_user.username,
                role=current_user.role,
                action="DAYBOOK_UPLOAD",
                status="Success",
                details=f"Uploaded Day Book '{file.filename}': {new_records_count} new, {duplicate_records_count} duplicates skipped",
                ip_address=ip,
                batch_id=batch.id
            )
        except Exception:
            pass

        msg = (
            f"Successfully uploaded and validated Day Book. {new_records_count} new transactions saved."
            if duplicate_records_count == 0
            else f"Day Book processed: {new_records_count} new transactions saved, {duplicate_records_count} duplicates skipped."
        )

        return {
            "status": "Success",
            "message": msg,
            "batch_id": batch.id,
            "batch_code": batch.batch_code,
            "total_rows": len(records),
            "new_records": new_records_count,
            "inserted": new_records_count,
            "duplicate_records": duplicate_records_count,
            "duplicates": duplicate_records_count,
            "stats": stats
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Upload processing failed: {str(e)}")
