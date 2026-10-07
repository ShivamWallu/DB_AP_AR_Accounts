import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR, DATA_DIR
from app.database import get_db
from app.models import User, ImportBatch
from app.schemas import PreUploadValidationResponse, ImportBatchResponse
from app.auth import get_current_user, require_admin
from app.services.upload_service import validate_uploaded_files, process_import_batch
from app.services.audit_service import log_activity
from app.excel_parser import detect_file_type

router = APIRouter(prefix="/api/upload", tags=["Upload & Import"])

@router.post("/validate", response_model=PreUploadValidationResponse)
async def validate_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(require_admin)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    saved_paths = []
    temp_dir = UPLOAD_DIR / "temp_validation"
    temp_dir.mkdir(exist_ok=True, parents=True)

    try:
        for f in files:
            if not f.filename.endswith((".xlsx", ".xls")):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file format for '{f.filename}'. Only Excel (.xlsx, .xls) files are accepted."
                )
            dest = temp_dir / f.filename
            with open(dest, "wb") as buffer:
                shutil.copyfileobj(f.file, buffer)
            saved_paths.append(str(dest))

        validation_result = validate_uploaded_files(saved_paths)
        return validation_result

    finally:
        # Clean temp directory
        for p in saved_paths:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

@router.post("/import", response_model=ImportBatchResponse)
async def import_files(
    files: List[UploadFile] = File(...),
    req: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for import.")

    # Save files to batch directory
    batch_timestamp = int(os.times().system)
    batch_dir = UPLOAD_DIR / f"batch_upload_{batch_timestamp}"
    batch_dir.mkdir(exist_ok=True, parents=True)

    file_map = {}
    saved_paths = []

    for f in files:
        if not f.filename.endswith((".xlsx", ".xls")):
            raise HTTPException(status_code=400, detail=f"File {f.filename} is not an Excel file.")
        dest = batch_dir / f.filename
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(f.file, buffer)
        saved_paths.append(str(dest))

        doc_type = detect_file_type(str(dest))
        if doc_type in ["Day Book", "AP", "AR"]:
            file_map[doc_type] = str(dest)

    missing_docs = [dt for dt in ["Day Book", "AP", "AR"] if dt not in file_map]
    if missing_docs:
        detected_str = ", ".join(file_map.keys()) if file_map else "None"
        missing_str = ", ".join(missing_docs)
        raise HTTPException(
            status_code=400,
            detail=f"Incomplete Dataset: All 3 files (Day Book, AP, AR) are strictly mandatory. Detected: {detected_str} | Missing: {missing_str}"
        )

    ip = req.client.host if req and req.client else None
    try:
        batch = process_import_batch(db, file_map, current_user, ip)
        return batch
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

@router.post("/import-initial-data", response_model=ImportBatchResponse)
def import_initial_data(
    req: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Import the 3 initial Excel files present in the data_files directory"""
    if not DATA_DIR.exists():
        raise HTTPException(status_code=404, detail="data_files directory not found.")

    excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith((".xlsx", ".xls"))]
    if not excel_files:
        raise HTTPException(status_code=404, detail="No Excel files found in data_files directory.")

    file_map = {}
    for f in excel_files:
        full_path = str(DATA_DIR / f)
        doc_type = detect_file_type(full_path)
        if doc_type in ["Day Book", "AP", "AR"]:
            file_map[doc_type] = full_path

    if not file_map:
        raise HTTPException(status_code=400, detail="No matching Day Book, AP, or AR files found in data_files.")

    ip = req.client.host if req and req.client else None
    batch = process_import_batch(db, file_map, current_user, ip)
    return batch
