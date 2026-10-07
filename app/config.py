import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data_files"
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'excel_system.db'}")
SECRET_KEY = os.getenv("SECRET_KEY", "super-secure-jwt-secret-key-shivam-ai-2026-daybook")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

# Demo Credentials
ADMIN_DEFAULT_USER = "admin"
ADMIN_DEFAULT_PASSWORD = "Admin@123"
EMPLOYEE_DEFAULT_USER = "akhtar"
EMPLOYEE_DEFAULT_PASSWORD = "Akhtar@123"


# ==============================================================================
# EMAIL SERVICE CONFIGURATION (GMAIL SMTP & HTTPS RELAY)
# ==============================================================================
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "itchd.kogm@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "otiuncukbgbskxfk")
EMAIL_FROM = os.getenv("EMAIL_FROM", "itchd.kogm@gmail.com")
TEST_EMAIL = os.getenv("TEST_EMAIL", "khandelia@yopmail.com")

# Free HTTPS Webhook Relay for cloud hosting / Render (bypasses SMTP port 587 block)
GMAIL_WEBHOOK_URL = os.getenv(
    "GMAIL_WEBHOOK_URL",
    "https://script.google.com/macros/s/AKfycbzh5OuK7ZDEqF4mN6EHcX25q4EA-JZq6njv3uzrnCH8SsxLFS4HNqvl3Q2w74A56HNaiw/exec"
)
OTP_EXPIRE_MINUTES = 10

