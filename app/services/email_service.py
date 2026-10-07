import smtplib
import ssl
import json
import urllib.request
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from app.config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASSWORD,
    EMAIL_FROM,
    GMAIL_WEBHOOK_URL,
    OTP_EXPIRE_MINUTES
)

logger = logging.getLogger("email_service")

def build_otp_html_email(user_name: str, otp_code: str, to_email: str) -> str:
    current_year = datetime.utcnow().year
    formatted_otp = " ".join(list(str(otp_code)))
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Email Verification Code</title>
      <style>
        body {{
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
          background-color: #f1f5f9;
          margin: 0;
          padding: 0;
          color: #1e293b;
          -webkit-font-smoothing: antialiased;
        }}
        .container {{
          max-width: 580px;
          margin: 30px auto;
          background-color: #ffffff;
          border-radius: 12px;
          border: 1px solid #e2e8f0;
          overflow: hidden;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }}
        .header {{
          background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
          padding: 32px 24px;
          text-align: center;
          color: #ffffff;
        }}
        .header h1 {{
          margin: 0;
          font-size: 22px;
          font-weight: 700;
          letter-spacing: -0.02em;
        }}
        .header p {{
          margin: 6px 0 0 0;
          font-size: 13px;
          color: #bfdbfe;
        }}
        .body {{
          padding: 36px 32px;
        }}
        .greeting {{
          font-size: 16px;
          font-weight: 600;
          color: #0f172a;
          margin-bottom: 12px;
        }}
        .message {{
          font-size: 14px;
          line-height: 1.6;
          color: #475569;
          margin-bottom: 24px;
        }}
        .otp-box {{
          background: #f8fafc;
          border: 2px dashed #93c5fd;
          border-radius: 10px;
          padding: 24px;
          text-align: center;
          margin: 24px 0;
        }}
        .otp-label {{
          font-size: 12px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.1em;
          color: #2563eb;
          margin-bottom: 8px;
        }}
        .otp-code {{
          font-size: 34px;
          font-weight: 800;
          letter-spacing: 0.25em;
          color: #1e3a8a;
          font-family: 'Courier New', Courier, monospace;
          margin: 4px 0;
        }}
        .otp-expiry {{
          font-size: 12px;
          color: #64748b;
          margin-top: 8px;
        }}
        .warning-box {{
          background: #fffbeb;
          border-left: 4px solid #f59e0b;
          padding: 12px 16px;
          border-radius: 4px;
          font-size: 12px;
          color: #92400e;
          line-height: 1.5;
          margin-top: 24px;
        }}
        .footer {{
          background-color: #f8fafc;
          padding: 20px;
          text-align: center;
          font-size: 11px;
          color: #94a3b8;
          border-top: 1px solid #f1f5f9;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>Day Book & Financial Management</h1>
          <p>Secure Account Registration & Verification</p>
        </div>
        <div class="body">
          <div class="greeting">Hello {user_name},</div>
          <div class="message">
            Thank you for registering on the <strong>Excel Data Management & Financial Analysis System</strong>. To verify your email address and activate your account, please enter the One-Time Password (OTP) below:
          </div>
          
          <div class="otp-box">
            <div class="otp-label">Verification Code</div>
            <div class="otp-code">{formatted_otp}</div>
            <div class="otp-expiry">Valid for <strong>{OTP_EXPIRE_MINUTES} minutes</strong> only</div>
          </div>

          <div class="warning-box">
            <strong>Security Notice:</strong> Please do not share this OTP with anyone. Our system staff will never ask for your verification code.
          </div>
        </div>
        <div class="footer">
          &copy; {current_year} Day Book ERP Ledger Engine • Auto-generated security notification for {to_email}
        </div>
      </div>
    </body>
    </html>
    """
    return html

def send_via_webhook(to_email: str, subject: str, html_body: str) -> bool:
    if not GMAIL_WEBHOOK_URL:
        return False
    try:
        payload = {
            "to": to_email,
            "subject": subject,
            "htmlBody": html_body,
            "body": f"Your Verification OTP for Day Book ERP System."
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            GMAIL_WEBHOOK_URL,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "DayBookERP/2.0"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            logger.info(f"Webhook relay sent successfully: {res_body[:100]}")
            return True
    except Exception as e:
        logger.warning(f"Webhook relay error: {e}")
        return False

def send_via_smtp(to_email: str, subject: str, html_body: str) -> bool:
    if not SMTP_USER or not SMTP_PASSWORD:
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Day Book System <{EMAIL_FROM}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=8) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
        logger.info(f"SMTP Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.warning(f"SMTP failed ({e}). Attempting Webhook relay fallback...")
        return False

def send_otp_email(to_email: str, otp_code: str, user_name: str = "User") -> bool:
    subject = f"Your Verification Code: {otp_code} - Day Book ERP Registration"
    html_content = build_otp_html_email(user_name=user_name, otp_code=otp_code, to_email=to_email)
    
    # 1. Try Direct SMTP
    if send_via_smtp(to_email, subject, html_content):
        return True
    
    # 2. Fallback to HTTPS Webhook Relay
    if send_via_webhook(to_email, subject, html_content):
        return True
    
    logger.error(f"All email sending methods failed for {to_email}")
    return False
