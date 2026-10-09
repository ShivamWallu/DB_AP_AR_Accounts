import os
import re
import base64
import smtplib
import ssl
import json
import urllib.request
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
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

def get_logo_base64() -> str:
    try:
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static", "images", "KOGM_LOgo.jpg"))
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        logger.warning(f"Could not load logo image for email: {e}")
    return ""

def build_otp_html_email(user_name: str, otp_code: str, to_email: str) -> str:
    current_year = datetime.utcnow().year
    clean_otp = str(otp_code).strip()
    logo_b64 = get_logo_base64()
    
    logo_html = ""
    if logo_b64:
        logo_html = f"""
        <div style="background: #ffffff; display: inline-block; padding: 12px 24px; border-radius: 14px; box-shadow: 0 8px 24px rgba(0,0,0,0.18); margin-bottom: 16px;">
          <img src="data:image/jpeg;base64,{logo_b64}" alt="K-GM Khandelia Oil & General Mills Pvt. Ltd." width="160" style="width: 160px; max-width: 100%; height: auto; display: block; border-radius: 6px; margin: 0 auto;" />
        </div>
        """
    else:
        logo_html = """
        <div style="background: #ffffff; color: #1e3a8a; display: inline-block; padding: 8px 22px; border-radius: 20px; font-size: 15px; font-weight: 800; margin-bottom: 14px; letter-spacing: 0.05em;">
          K-GM &bull; KOGM 360&deg;
        </div>
        """
    
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
          padding: 24px 10px;
          color: #1e293b;
          -webkit-font-smoothing: antialiased;
        }}
        .email-wrapper {{
          max-width: 580px;
          margin: 0 auto;
          background-color: #ffffff;
          border-radius: 18px;
          border: 1px solid #e2e8f0;
          overflow: hidden;
          box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
        }}
        .header {{
          background: linear-gradient(135deg, #0b1329 0%, #1e3a8a 55%, #2563eb 100%);
          padding: 36px 24px 30px 24px;
          text-align: center;
          color: #ffffff;
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
          font-size: 40px;
          font-weight: 900;
          letter-spacing: 0.15em;
          color: #1e3a8a;
          font-family: 'Courier New', Courier, monospace;
          background: #ffffff;
          display: inline-block;
          padding: 8px 26px;
          border-radius: 8px;
          border: 1.5px solid #bae6fd;
          box-shadow: 0 4px 12px rgba(3, 105, 161, 0.10);
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
          color: #64748b;
          border-top: 1px solid #f1f5f9;
          line-height: 1.6;
        }}
        .footer-creator {{
          color: #1e40af;
          font-weight: 700;
          font-size: 12px;
          margin-top: 6px;
        }}
      </style>
    </head>
    <body>
      <div class="email-wrapper">
        <div class="header">
          {logo_html}
          <h1>Finance Day Book</h1>
          <p>KOGM Enterprise Financial ERP &bull; Day Book &bull; AP &bull; AR Audit Suite</p>
        </div>
        <div class="body">
          <div class="greeting">Hello {user_name},</div>
          <div class="message">
            You are registering for an account on <strong>Finance Day Book</strong> (KOGM Financial ERP Suite). To verify your email address and activate your <strong>Admin Access</strong>, please use the 6-digit verification code below:
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
          <div>&copy; {current_year} Finance Day Book &bull; KOGM Enterprise Financial Suite &bull; Sent to {to_email}</div>
          <div class="footer-creator">Created by Er.Shivam Wallu</div>
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
        msg_root = MIMEMultipart("related")
        msg_root["Subject"] = subject
        msg_root["From"] = f"Day Book System <{EMAIL_FROM}>"
        msg_root["To"] = to_email

        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "static", "images", "KOGM_LOgo.jpg"))
        smtp_html = html_body
        has_logo = False
        img_data = b""

        if os.path.exists(logo_path):
            try:
                with open(logo_path, "rb") as f:
                    img_data = f.read()
                if "data:image/jpeg;base64," in smtp_html:
                    smtp_html = re.sub(r'src="data:image\/[^"]+"', 'src="cid:kogm_logo_img"', smtp_html)
                    has_logo = True
            except Exception as e:
                logger.warning(f"Could not read logo image for CID attachment: {e}")

        msg_alternative = MIMEMultipart("alternative")
        msg_root.attach(msg_alternative)
        msg_alternative.attach(MIMEText(smtp_html, "html"))

        if has_logo and img_data:
            img = MIMEImage(img_data)
            img.add_header("Content-ID", "<kogm_logo_img>")
            img.add_header("Content-Disposition", "inline", filename="kogm_logo.jpg")
            msg_root.attach(img)

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=8) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(EMAIL_FROM, to_email, msg_root.as_string())
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

def build_password_reset_html_email(user_name: str, reset_url: str, to_email: str, expires_minutes: int = 10) -> str:
    current_year = datetime.utcnow().year
    logo_b64 = get_logo_base64()
    
    logo_html = ""
    if logo_b64:
        logo_html = f"""
        <div style="background: #ffffff; display: inline-block; padding: 12px 24px; border-radius: 14px; box-shadow: 0 8px 24px rgba(0,0,0,0.18); margin-bottom: 16px;">
          <img src="data:image/jpeg;base64,{logo_b64}" alt="K-GM Khandelia Oil & General Mills Pvt. Ltd." width="160" style="width: 160px; max-width: 100%; height: auto; display: block; border-radius: 6px; margin: 0 auto;" />
        </div>
        """
    else:
        logo_html = """
        <div style="background: #ffffff; color: #1e3a8a; display: inline-block; padding: 8px 22px; border-radius: 20px; font-size: 15px; font-weight: 800; margin-bottom: 14px; letter-spacing: 0.05em;">
          K-GM &bull; KOGM 360&deg;
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Reset Your Password - KOGM 360°</title>
      <style>
        body {{
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
          background-color: #0b1329;
          margin: 0;
          padding: 24px 10px;
          color: #1e293b;
          -webkit-font-smoothing: antialiased;
        }}
        .email-wrapper {{
          max-width: 580px;
          margin: 0 auto;
          background-color: #ffffff;
          border-radius: 18px;
          border: 1px solid #e2e8f0;
          overflow: hidden;
          box-shadow: 0 16px 40px rgba(0, 0, 0, 0.28);
        }}
        .header {{
          background: linear-gradient(135deg, #0b1329 0%, #1e3a8a 55%, #2563eb 100%);
          padding: 36px 24px 30px 24px;
          text-align: center;
          color: #ffffff;
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
          margin-bottom: 24px;
        }}
        .cta-container {{
          text-align: center;
          margin: 28px 0;
        }}
        .btn-reset {{
          background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
          color: #ffffff !important;
          text-decoration: none;
          font-size: 15px;
          font-weight: 700;
          padding: 14px 36px;
          border-radius: 10px;
          display: inline-block;
          box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35);
          letter-spacing: 0.02em;
        }}
        .btn-reset:hover {{
          background: #1d4ed8;
        }}
        .link-fallback-box {{
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          padding: 12px 16px;
          font-size: 11px;
          color: #64748b;
          word-break: break-all;
          margin: 20px 0;
        }}
        .link-fallback-box a {{
          color: #2563eb;
          text-decoration: underline;
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
          color: #64748b;
          border-top: 1px solid #f1f5f9;
          line-height: 1.6;
        }}
        .footer-creator {{
          color: #1e40af;
          font-weight: 700;
          font-size: 12px;
          margin-top: 6px;
        }}
      </style>
    </head>
    <body>
      <div class="email-wrapper">
        <div class="header">
          {logo_html}
          <h1>Finance Day Book</h1>
          <p>Password Reset &bull; KOGM Financial Security Center</p>
        </div>
        <div class="body">
          <div class="greeting">Hello {user_name},</div>
          <div class="message">
            We received a request to reset your password for your <strong>Finance Day Book</strong> account. Click the secure link below to set a new password:
          </div>
          
          <div class="cta-container">
            <a href="{reset_url}" class="btn-reset" target="_blank">🔒 Reset Account Password</a>
          </div>

          <div class="link-fallback-box">
            <div>If the button above does not work, copy and paste this link into your browser:</div>
            <div style="margin-top: 6px;"><a href="{reset_url}" target="_blank">{reset_url}</a></div>
          </div>

          <div class="warning-box">
            <strong>Security Notice:</strong> This reset link is valid for <strong>{expires_minutes} minutes</strong> only and can be used once. If you did not request a password reset, you can safely ignore this email — your account remains secure.
          </div>
        </div>
        <div class="footer">
          <div>&copy; {current_year} Finance Day Book &bull; KOGM Enterprise Financial Suite &bull; Sent to {to_email}</div>
          <div class="footer-creator">Created by Er.Shivam Wallu</div>
        </div>
      </div>
    </body>
    </html>
    """
    return html

def send_password_reset_email(to_email: str, reset_url: str, user_name: str = "User") -> bool:
    subject = "Reset Your Password - Finance Day Book (KOGM ERP)"
    html_content = build_password_reset_html_email(user_name=user_name, reset_url=reset_url, to_email=to_email, expires_minutes=10)
    
    # 1. Try Direct SMTP
    if send_via_smtp(to_email, subject, html_content):
        return True
    
    # 2. Fallback to HTTPS Webhook Relay
    if send_via_webhook(to_email, subject, html_content):
        return True
    
    logger.error(f"All email sending methods failed for password reset email to {to_email}")
    return False
