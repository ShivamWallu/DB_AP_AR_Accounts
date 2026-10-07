from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import DashboardStatsResponse
from app.auth import get_current_user
from app.services.dashboard_service import get_dashboard_data

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_dashboard_data(db)
