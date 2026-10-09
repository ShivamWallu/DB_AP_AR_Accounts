import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.database import engine, Base, SessionLocal, init_db
from app.auth import init_default_users
from app.routers import (
    auth_router, upload_router, data_router,
    dashboard_router, imports_router, audit_router, export_router
)
from app.models import ImportBatch, User, DayBookRecord
from app.services.upload_service import process_import_batch, cleanup_old_batches
from app.excel_parser import detect_file_type
from app.config import DATA_DIR, BASE_DIR

# Ensure DB tables and default users exist immediately
init_db()
_db_init = SessionLocal()
try:
    init_default_users(_db_init)
    cleanup_old_batches(_db_init, retention_days=14)
    # Backfill voucher_date_range for existing batches if needed
    existing_batches = _db_init.query(ImportBatch).all()
    for eb in existing_batches:
        if not eb.voucher_date_range:
            first_db_rec = _db_init.query(DayBookRecord).filter(DayBookRecord.batch_id == eb.id, DayBookRecord.voucher_date.isnot(None)).first()
            if first_db_rec and first_db_rec.voucher_date:
                eb.voucher_date_range = first_db_rec.voucher_date
            else:
                eb.voucher_date_range = eb.upload_date_str
    _db_init.commit()
finally:
    _db_init.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize default demo users (Admin and Employee)
    db = SessionLocal()
    try:
        init_default_users(db)
        # Enforce 14-day retention lifecycle on startup
        cleanup_old_batches(db, retention_days=14)
        
        # Check if database has any existing batches, if not, auto-import data_files
        existing_batch = db.query(ImportBatch).first()
        if not existing_batch and DATA_DIR.exists():
            admin_user = db.query(User).filter(User.username == "admin").first()
            if admin_user:
                excel_files = [f for f in os.listdir(DATA_DIR) if f.endswith((".xlsx", ".xls"))]
                file_map = {}
                for f in excel_files:
                    full_path = str(DATA_DIR / f)
                    doc_type = detect_file_type(full_path)
                    if doc_type in ["Day Book", "AP", "AR"]:
                        file_map[doc_type] = full_path

                if len(file_map) == 3:
                    print("Auto-seeding initial 3 Excel files from data_files...")
                    process_import_batch(db, file_map, admin_user, "127.0.0.1")
                    print("Initial data seeded successfully!")
    finally:
        db.close()
    
    yield

app = FastAPI(
    title="Excel Data Management, Filtering & Historical Log System",
    description="Enterprise Web-Based Excel Data Management & Analysis System for Day Book, AP, and AR",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router.router)
app.include_router(upload_router.router)
app.include_router(data_router.router)
app.include_router(dashboard_router.router)
app.include_router(imports_router.router)
app.include_router(audit_router.router)
app.include_router(export_router.router)

# Mount Static Files
static_path = BASE_DIR / "static"
static_path.mkdir(exist_ok=True, parents=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

@app.get("/")
def read_root():
    return FileResponse(str(static_path / "index.html"))
