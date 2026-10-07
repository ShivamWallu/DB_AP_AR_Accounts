from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import User, AuditLog
from app.schemas import AuditLogResponse
from app.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/audit", tags=["Audit Logs"])

@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action}%"))
    logs = q.order_by(desc(AuditLog.id)).limit(limit).all()
    return logs
