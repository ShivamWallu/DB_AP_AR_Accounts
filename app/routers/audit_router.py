from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.database import get_db
from app.models import User, AuditLog
from app.schemas import AuditLogResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/audit", tags=["Audit Logs"])

@router.get("/logs")
def get_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=1000),
    limit: Optional[int] = Query(None, ge=1, le=1000),
    search: Optional[str] = None,
    action: Optional[str] = None,
    user: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    actual_page_size = limit if limit is not None else page_size
    q = db.query(AuditLog)

    if search and search.strip():
        term = f"%{search.strip()}%"
        q = q.filter(
            or_(
                AuditLog.action.ilike(term),
                AuditLog.user_username.ilike(term),
                AuditLog.details.ilike(term),
                AuditLog.ip_address.ilike(term)
            )
        )
    if action and action.strip():
        q = q.filter(AuditLog.action.ilike(f"%{action.strip()}%"))
    if user and user.strip():
        q = q.filter(AuditLog.user_username.ilike(f"%{user.strip()}%"))
    if role and role.strip():
        q = q.filter(AuditLog.user_role == role.strip())
    if status and status.strip():
        q = q.filter(AuditLog.status == status.strip())

    total = q.count()
    total_pages = (total + actual_page_size - 1) // actual_page_size if total > 0 else 1
    logs = q.order_by(desc(AuditLog.id)).offset((page - 1) * actual_page_size).limit(actual_page_size).all()
    items = [AuditLogResponse.model_validate(l) for l in logs]

    return {
        "total": total,
        "page": page,
        "page_size": actual_page_size,
        "total_pages": total_pages,
        "items": items
    }

