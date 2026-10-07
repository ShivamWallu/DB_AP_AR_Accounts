from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models import AuditLog

def log_activity(
    db: Session,
    username: str,
    role: str,
    action: str,
    status: str = "Success",
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    batch_id: Optional[int] = None
) -> AuditLog:
    """Record an audit trail event in the database"""
    try:
        log_entry = AuditLog(
            user_username=username,
            user_role=role,
            action=action,
            status=status,
            details=details,
            ip_address=ip_address,
            batch_id=batch_id,
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception as e:
        db.rollback()
        print(f"Error writing audit log: {e}")
        return None
