from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="Employee", nullable=False) # 'Admin' or 'Employee'
    full_name = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), index=True, nullable=False)
    otp_code = Column(String(10), nullable=False)
    purpose = Column(String(50), default="registration", nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)



class ImportBatch(Base):
    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_code = Column(String(100), unique=True, index=True, nullable=False) # e.g. BATCH-20261006-001
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    upload_date_str = Column(String(50), nullable=False)
    upload_time_str = Column(String(50), nullable=False)
    
    daybook_filename = Column(String(255), nullable=True)
    ap_filename = Column(String(255), nullable=True)
    ar_filename = Column(String(255), nullable=True)
    
    total_rows = Column(Integer, default=0)
    daybook_rows = Column(Integer, default=0)
    ap_rows = Column(Integer, default=0)
    ar_rows = Column(Integer, default=0)
    
    new_records = Column(Integer, default=0)
    duplicate_records = Column(Integer, default=0)
    rejected_records = Column(Integer, default=0)
    
    status = Column(String(50), default="Completed") # Completed, Partial, Failed
    error_summary = Column(Text, nullable=True)
    created_by_user = Column(String(100), default="System")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    files = relationship("ImportFile", back_populates="batch", cascade="all, delete-orphan")
    daybook_records = relationship("DayBookRecord", back_populates="batch", cascade="all, delete-orphan")
    ap_records = relationship("APRecord", back_populates="batch", cascade="all, delete-orphan")
    ar_records = relationship("ARRecord", back_populates="batch", cascade="all, delete-orphan")


class ImportFile(Base):
    __tablename__ = "import_files"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("import_batches.id"), nullable=False)
    file_type = Column(String(50), nullable=False) # 'Day Book', 'AP', 'AR'
    original_filename = Column(String(255), nullable=False)
    stored_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    total_rows = Column(Integer, default=0)
    valid_rows = Column(Integer, default=0)
    duplicate_rows = Column(Integer, default=0)
    rejected_rows = Column(Integer, default=0)
    header_row_index = Column(Integer, default=1)
    status = Column(String(50), default="Success")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("ImportBatch", back_populates="files")


class DayBookRecord(Base):
    __tablename__ = "daybook_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("import_batches.id"), index=True, nullable=False)
    row_hash = Column(String(64), index=True, nullable=False) # Unique business deduplication hash

    # Mapped Main & Common Columns
    transaction_site = Column(String(100), index=True, nullable=True) # Col A
    voucher_number = Column(String(150), index=True, nullable=True) # Col F
    voucher_date = Column(String(50), index=True, nullable=True) # Col H
    voucher_type = Column(String(150), index=True, nullable=True) # Col K
    voucher_status = Column(String(100), index=True, nullable=True) # Col L
    party_code = Column(String(100), index=True, nullable=True) # Col M
    party_description = Column(String(255), index=True, nullable=True) # Col N
    account_description = Column(String(255), index=True, nullable=True) # Col S
    narration = Column(Text, nullable=True) # Col AN
    created_by = Column(String(150), index=True, nullable=True) # Col AO
    approved_by = Column(String(150), index=True, nullable=True) # Col AQ

    # Additional audit & full data preservation
    created_date_raw = Column(String(100), nullable=True) # Col AP
    approved_date_raw = Column(String(100), nullable=True) # Col AR
    source_file = Column(String(255), nullable=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    raw_data_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("ImportBatch", back_populates="daybook_records")

    __table_args__ = (
        Index("idx_db_site_vno", "transaction_site", "voucher_number"),
        Index("idx_db_search", "voucher_number", "party_code", "party_description"),
    )


class APRecord(Base):
    __tablename__ = "ap_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("import_batches.id"), index=True, nullable=False)
    row_hash = Column(String(64), index=True, nullable=False)

    # Common & Main Columns
    accounting_site_code = Column(String(100), index=True, nullable=True) # Col A
    voucher_number = Column(String(150), index=True, nullable=True) # Col H
    voucher_type = Column(String(150), index=True, nullable=True) # Col N
    voucher_sub_type = Column(String(150), index=True, nullable=True) # Col P
    party_gst_tin = Column(String(100), index=True, nullable=True) # Col AR
    invoice_number = Column(String(150), index=True, nullable=True) # Col AZ
    invoice_date = Column(String(50), index=True, nullable=True) # Col BA
    due_date = Column(String(50), nullable=True) # Col BC
    item_service_description = Column(String(255), index=True, nullable=True) # Col BP
    item_service_expense_account_desc = Column(String(255), nullable=True) # Col BR
    booked_item_quantity = Column(Float, nullable=True) # Col BW
    item_service_rate = Column(Float, nullable=True) # Col CA
    item_service_detail_amount = Column(Float, nullable=True) # Col CB
    total_tax_amount = Column(Float, nullable=True) # Col CE
    total_voucher_amount = Column(Float, nullable=True) # Col CF
    total_tds = Column(Float, nullable=True) # Col CQ

    # Narration / Cross-link audit
    header_narration = Column(Text, nullable=True) # Col HB
    detail_narration = Column(Text, nullable=True) # Col HC
    source_file = Column(String(255), nullable=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    raw_data_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("ImportBatch", back_populates="ap_records")

    __table_args__ = (
        Index("idx_ap_site_vno", "accounting_site_code", "voucher_number"),
        Index("idx_ap_inv_vno", "invoice_number", "voucher_number"),
    )


class ARRecord(Base):
    __tablename__ = "ar_records"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("import_batches.id"), index=True, nullable=False)
    row_hash = Column(String(64), index=True, nullable=False)

    # Common & Main Columns
    accounting_site_code = Column(String(100), index=True, nullable=True) # Col A
    voucher_number = Column(String(150), index=True, nullable=True) # Col K
    voucher_type = Column(String(150), index=True, nullable=True) # Col F
    voucher_sub_type = Column(String(150), index=True, nullable=True) # Col G
    item_service_description = Column(String(255), index=True, nullable=True) # Col BM
    item_quantity = Column(Float, nullable=True) # Col BT
    item_service_rate = Column(Float, nullable=True) # Col BY
    item_service_amount = Column(Float, nullable=True) # Col CF
    item_service_charges = Column(Float, nullable=True) # Col CG
    item_amount_net_off_discount = Column(Float, nullable=True) # Col CI
    item_service_taxes = Column(Float, nullable=True) # Col CJ
    net_amount = Column(Float, nullable=True) # Col CL
    total_cgst = Column(Float, nullable=True) # Col DQ (Actual header: Total CGST)
    total_sgst = Column(Float, nullable=True) # Col EG (Actual header: Total SGST)
    total_igst = Column(Float, nullable=True) # Col EW (Actual header: Total IGST)

    # Narration / Audit
    narration_remarks = Column(Text, nullable=True) # Col FM
    source_file = Column(String(255), nullable=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    raw_data_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("ImportBatch", back_populates="ar_records")

    __table_args__ = (
        Index("idx_ar_site_vno", "accounting_site_code", "voucher_number"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_username = Column(String(100), index=True, nullable=False)
    user_role = Column(String(50), nullable=False)
    action = Column(String(100), index=True, nullable=False) # e.g. "User Login", "File Upload", "Import Completed"
    status = Column(String(50), default="Success") # Success, Warning, Failed
    details = Column(Text, nullable=True)
    ip_address = Column(String(100), nullable=True)
    batch_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
