from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class SendOTPRequest(BaseModel):
    email: str
    username: Optional[str] = None
    full_name: Optional[str] = None

class RegisterRequest(BaseModel):
    full_name: str
    username: str
    email: str
    password: str
    role: Optional[str] = "Employee"
    otp: str

class OTPResponse(BaseModel):
    status: str
    message: str
    email: Optional[str] = None
    expires_in_seconds: Optional[int] = 600

class ForgotPasswordRequest(BaseModel):
    identifier: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    role: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Batch & File Schemas
class ImportFileResponse(BaseModel):
    id: int
    file_type: str
    original_filename: str
    file_size_bytes: int
    total_rows: int
    valid_rows: int
    duplicate_rows: int
    rejected_rows: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ImportBatchResponse(BaseModel):
    id: int
    batch_code: str
    upload_timestamp: datetime
    upload_date_str: str
    upload_time_str: str
    daybook_filename: Optional[str] = None
    ap_filename: Optional[str] = None
    ar_filename: Optional[str] = None
    voucher_date_range: Optional[str] = None
    total_rows: int
    daybook_rows: int
    ap_rows: int
    ar_rows: int
    new_records: int
    duplicate_records: int
    rejected_records: int
    status: str
    error_summary: Optional[str] = None
    created_by_user: str
    files: Optional[List[ImportFileResponse]] = None
    model_config = ConfigDict(from_attributes=True)

# Validation Response
class ValidationDetail(BaseModel):
    file_type: str
    filename: str
    file_size_bytes: int
    detected_header_row: int
    total_rows_detected: int
    valid_data_rows: int
    columns_matched: int
    columns_missing: List[str]
    unexpected_columns: List[str]
    status: str # "Valid", "Warning", "Failed"
    message: str

class PreUploadValidationResponse(BaseModel):
    is_valid: bool
    status: str # "Ready for Import", "Validation Failed"
    files_validation: List[ValidationDetail]
    message: str

# Data Record Schemas
class DayBookRecordResponse(BaseModel):
    id: int
    batch_id: int
    transaction_site: Optional[str] = None
    voucher_number: Optional[str] = None
    voucher_date: Optional[str] = None
    voucher_type: Optional[str] = None
    voucher_status: Optional[str] = None
    party_code: Optional[str] = None
    party_description: Optional[str] = None
    account_description: Optional[str] = None
    narration: Optional[str] = None
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    source_file: Optional[str] = None
    upload_timestamp: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class APRecordResponse(BaseModel):
    id: int
    batch_id: int
    accounting_site_code: Optional[str] = None
    voucher_number: Optional[str] = None
    voucher_type: Optional[str] = None
    voucher_sub_type: Optional[str] = None
    party_gst_tin: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    item_service_description: Optional[str] = None
    item_service_expense_account_desc: Optional[str] = None
    booked_item_quantity: Optional[float] = None
    item_service_rate: Optional[float] = None
    item_service_detail_amount: Optional[float] = None
    total_tax_amount: Optional[float] = None
    total_voucher_amount: Optional[float] = None
    total_tds: Optional[float] = None
    # Audit trail (direct or linked from Day Book)
    narration: Optional[str] = None
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    source_file: Optional[str] = None
    upload_timestamp: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class ARRecordResponse(BaseModel):
    id: int
    batch_id: int
    accounting_site_code: Optional[str] = None
    voucher_number: Optional[str] = None
    voucher_type: Optional[str] = None
    voucher_sub_type: Optional[str] = None
    item_service_description: Optional[str] = None
    item_quantity: Optional[float] = None
    item_service_rate: Optional[float] = None
    item_service_amount: Optional[float] = None
    item_service_charges: Optional[float] = None
    item_amount_net_off_discount: Optional[float] = None
    item_service_taxes: Optional[float] = None
    net_amount: Optional[float] = None
    total_cgst: Optional[float] = None
    total_sgst: Optional[float] = None
    total_igst: Optional[float] = None
    # Audit trail (direct or linked from Day Book)
    narration: Optional[str] = None
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    source_file: Optional[str] = None
    upload_timestamp: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

# Paginated Response Wrapper
class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[Any]

# Filter Options Response
class FilterOptionsResponse(BaseModel):
    sites: List[str]
    voucher_types: List[str]
    voucher_subtypes: List[str]
    approvers: Optional[List[str]] = []
    batches: List[Dict[str, Any]]

# Dashboard Stats Response
class DashboardStatsResponse(BaseModel):
    total_daybook_records: int
    total_ap_records: int
    total_ar_records: int
    total_historical_records: int
    today_imported_records: int
    last_upload_date: Optional[str] = None
    last_upload_time: Optional[str] = None
    last_batch_status: Optional[str] = None
    last_batch_code: Optional[str] = None
    total_batches: int
    
    # Financial metrics
    ap_total_amount: float
    ar_total_amount: float
    total_tax_collected_or_paid: float
    
    # Distributions
    site_distribution: List[Dict[str, Any]]
    voucher_type_distribution: List[Dict[str, Any]]
    voucher_subtype_distribution: List[Dict[str, Any]]

# Audit Log Schema
class AuditLogResponse(BaseModel):
    id: int
    user_username: str
    user_role: str
    action: str
    status: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    batch_id: Optional[int] = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


# Verification Schemas
class ToggleVerificationRequest(BaseModel):
    dataset_type: str
    record_id: Optional[int] = None
    voucher_number: Optional[str] = None

class VerificationItem(BaseModel):
    id: Optional[int] = None
    dataset_type: str
    identifier_key: str
    voucher_number: Optional[str] = None
    record_id: Optional[int] = None
    verified_by: str
    user_role: Optional[str] = None
    timestamp: Optional[str] = None
    date: Optional[str] = None
    created_at: Optional[datetime] = None

class VerificationListResponse(BaseModel):
    verifications: Dict[str, Dict[str, Any]]
    total: int

