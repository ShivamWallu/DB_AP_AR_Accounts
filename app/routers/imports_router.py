from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import User, ImportBatch, DayBookRecord, APRecord, ARRecord, ImportFile
from app.schemas import ImportBatchResponse
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/imports", tags=["Import History"])

@router.get("", response_model=List[ImportBatchResponse])
def get_all_batches(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batches = db.query(ImportBatch).filter(
        ImportBatch.status == "Completed",
        ImportBatch.total_rows > 0
    ).order_by(desc(ImportBatch.id)).limit(20).all()
    return batches

@router.get("/{batch_id}", response_model=ImportBatchResponse)
def get_batch(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch with ID {batch_id} not found.")
    return batch

@router.delete("/{batch_id}")
def delete_batch(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    batch = db.query(ImportBatch).filter(ImportBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch with ID {batch_id} not found.")
    
    db.query(DayBookRecord).filter(DayBookRecord.batch_id == batch_id).delete(synchronize_session=False)
    db.query(APRecord).filter(APRecord.batch_id == batch_id).delete(synchronize_session=False)
    db.query(ARRecord).filter(ARRecord.batch_id == batch_id).delete(synchronize_session=False)
    db.query(ImportFile).filter(ImportFile.batch_id == batch_id).delete(synchronize_session=False)
    db.delete(batch)
    db.commit()
    return {"message": f"Batch {batch.batch_code} deleted successfully."}
