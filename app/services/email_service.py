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
    clean_otp = str(otp_code).strip()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>KOGM 360° Verification Code</title>
      <style>
        body {{
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
          background-color: #0b1329;
          margin: 0;
          padding: 20px 10px;
          color: #1e293b;
          -webkit-font-smoothing: antialiased;
        }}
        .email-wrapper {{
          max-width: 580px;
          margin: 0 auto;
          background-color: #ffffff;
          border-radius: 16px;
          border: 1px solid #e2e8f0;
          overflow: hidden;
          box-shadow: 0 12px 36px rgba(0, 0, 0, 0.25);
        }}
        .header {{
          background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #2563eb 100%);
          padding: 36px 24px;
          text-align: center;
          color: #ffffff;
        }}
        .brand-badge {{
          display: inline-block;
          background: #ffffff;
          color: #1e3a8a;
          padding: 6px 16px;
          border-radius: 20px;
          font-size: 13px;
          font-weight: 800;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          margin-bottom: 12px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .header h1 {{
          margin: 0;
          font-size: 24px;
          font-weight: 800;
          letter-spacing: -0.02em;
        }}
        .header p {{
          margin: 6px 0 0 0;
          font-size: 13px;
          color: #93c5fd;
          font-weight: 500;
        }}
        .body {{
          padding: 36px 32px;
          background-color: #ffffff;
        }}
        .greeting {{
          font-size: 16px;
          font-weight: 700;
          color: #0f172a;
          margin-bottom: 12px;
        }}
        .message {{
          font-size: 14px;
          line-height: 1.6;
          color: #475569;
          margin-bottom: 20px;
        }}
        .otp-card {{
          background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%);
          border: 2px solid #38bdf8;
          border-radius: 12px;
          padding: 24px 16px;
          text-align: center;
          margin: 24px 0;
        }}
        .otp-label {{
          font-size: 11px;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: 0.15em;
          color: #0369a1;
          margin-bottom: 8px;
        }}
        .otp-code {{
          font-size: 38px;
          font-weight: 900;
          letter-spacing: 0.15em;
          color: #1e3a8a;
          font-family: 'Courier New', Courier, monospace;
          background: #ffffff;
          display: inline-block;
          padding: 8px 24px;
          border-radius: 8px;
          border: 1px solid #bae6fd;
          box-shadow: 0 2px 8px rgba(3, 105, 161, 0.08);
          user-select: all;
          -webkit-user-select: all;
          margin: 6px 0;
        }}
        .otp-instruction {{
          font-size: 12px;
          color: #0284c7;
          font-weight: 600;
          margin-top: 8px;
        }}
        .otp-expiry {{
          font-size: 12px;
          color: #64748b;
          margin-top: 4px;
        }}
        .warning-box {{
          background: #fffbeb;
          border-left: 4px solid #f59e0b;
          padding: 14px 18px;
          border-radius: 6px;
          font-size: 12px;
          color: #92400e;
          line-height: 1.5;
          margin-top: 24px;
        }}
        .footer {{
          background-color: #f8fafc;
          padding: 24px 20px;
          text-align: center;
          font-size: 11px;
          color: #94a3b8;
          border-top: 1px solid #f1f5f9;
        }}
      </style>
    </head>
    <body>
      <div class="email-wrapper">
        <div class="header">
          <div class="brand-badge">K-GM &bull; KOGM 360&deg;</div>
          <h1>Enterprise Financial ERP Suite</h1>
          <p>Multi-Register Accounting &bull; Day Book &bull; AP &bull; AR Ledger Audit</p>
        </div>
        <div class="body">
          <div class="greeting">Hello {user_name},</div>
          <div class="message">
            You are registering for an account on the <strong>KOGM 360° Financial ERP Suite</strong>. To verify your email address and activate your <strong>Admin Access</strong>, please use the 6-digit verification code below:
          </div>
          
          <div class="otp-card">
            <div class="otp-label">Your One-Time Password (OTP)</div>
            <div class="otp-code">{clean_otp}</div>
            <div class="otp-instruction">&bull; Double-click to copy &bull;</div>
            <div class="otp-expiry">Valid for <strong>{OTP_EXPIRE_MINUTES} minutes</strong> only</div>
          </div>

          <div class="warning-box">
            <strong>Security Notice:</strong> Do not share this code with anyone. System administrators will never ask for your password or verification code.
          </div>
        </div>
        <div class="footer">
          &copy; {current_year} KOGM 360° Enterprise Financial Suite &bull; Sent to {to_email}
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
