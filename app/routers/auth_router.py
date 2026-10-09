import re
from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models import User, OTPVerification, PasswordResetToken
from app.schemas import (
    Token, LoginRequest, UserResponse,
    SendOTPRequest, RegisterRequest, OTPResponse,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.auth import (
    verify_password, get_password_hash,
    create_access_token, get_current_user, require_admin
)
from app.services.audit_service import log_activity
from app.services.email_service import send_otp_email, send_password_reset_email
from app.config import OTP_EXPIRE_MINUTES

def validate_password_strength(password: str) -> None:
    """
    Enforce enterprise password security:
    - Minimum 8 characters
    - At least 1 uppercase letter (A-Z)
    - At least 1 lowercase letter (a-z)
    - At least 1 digit (0-9)
    - At least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
    """
    if not password or len(password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long."
        )
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one uppercase letter (A-Z)."
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one lowercase letter (a-z)."
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one number (0-9)."
        )
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?/~\`]", password):
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least one special character (!@#$%^&*...)."
        )

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(request_data: LoginRequest, req: Request, db: Session = Depends(get_db)):
    identifier = request_data.username.strip()
    clean_identifier = identifier.lstrip("@").strip()
    
    # Query by username, handle without @, or email address
    user = db.query(User).filter(
        or_(
            User.username == identifier,
            User.username == clean_identifier,
            User.email == identifier.lower()
        )
    ).first()

    if not user or not verify_password(request_data.password, user.hashed_password):
        log_activity(
            db=db,
            username=request_data.username,
            role="Unknown",
            action="User Login Failed",
            status="Failed",
            details="Invalid username or password attempt",
            ip_address=req.client.host if req.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        log_activity(
            db=db,
            username=user.username,
            role=user.role,
            action="Blocked User Login Attempt",
            status="Denied",
            details=f"Blocked/Suspended user '{user.username}' attempted to log in",
            ip_address=req.client.host if req.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="🚫 Your account has been blocked/suspended by administrator. You are not permitted to log in."
        )

    token = create_access_token(data={"sub": user.username, "role": user.role})
    
    log_activity(
        db=db,
        username=user.username,
        role=user.role,
        action="User Login",
        status="Success",
        details=f"Successful login for role {user.role}",
        ip_address=req.client.host if req.client else None
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email
    }

@router.post("/send-registration-otp", response_model=OTPResponse)
def send_registration_otp(data: SendOTPRequest, req: Request, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Please provide a valid email address.")
    
    # Check if user already exists with this email
    existing_user_email = db.query(User).filter(User.email == email).first()
    if existing_user_email:
        if not existing_user_email.is_active:
            log_activity(
                db=db,
                username=email,
                role="Guest",
                action="Blocked Account Registration Attempt",
                status="Denied",
                details=f"Blocked email '{email}' attempted to request registration OTP",
                ip_address=req.client.host if req.client else None
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"🚫 This email '{email}' has been blocked/suspended by administrator. Registration or recovery is not allowed."
            )
        raise HTTPException(
            status_code=400,
            detail="An account is already registered with this email address. Please sign in."
        )
    
    if data.username:
        u_name = data.username.strip()
        existing_username = db.query(User).filter(User.username == u_name).first()
        if existing_username:
            if not existing_username.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"🚫 The username '{u_name}' belongs to a blocked account."
                )
            raise HTTPException(
                status_code=400,
                detail=f"Username '{u_name}' is already taken. Please choose another username."
            )

    # Generate secure 6-digit random OTP
    otp_code = f"{secrets.randbelow(900000) + 100000:06d}"
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)

    # Invalidate previous unused registration OTPs for this email
    db.query(OTPVerification).filter(
        OTPVerification.email == email,
        OTPVerification.purpose == "registration",
        OTPVerification.is_used == False
    ).update({"is_used": True})

    otp_record = OTPVerification(
        email=email,
        otp_code=otp_code,
        purpose="registration",
        expires_at=expires_at,
        is_used=False
    )
    db.add(otp_record)
    db.commit()

    # Send OTP Email
    full_name = data.full_name.strip() if data.full_name else (data.username or "User")
    email_success = send_otp_email(to_email=email, otp_code=otp_code, user_name=full_name)

    log_activity(
        db=db,
        username=data.username or email,
        role="Guest",
        action="Registration OTP Request",
        status="Success" if email_success else "Warning",
        details=f"OTP generated and sent to {email} (Method status: {email_success})",
        ip_address=req.client.host if req.client else None
    )

    if not email_success:
        raise HTTPException(
            status_code=500,
            detail="Failed to dispatch verification email. Please verify SMTP/Relay connectivity."
        )

    return {
        "status": "success",
        "message": f"6-digit verification OTP has been sent to {email}",
        "email": email,
        "expires_in_seconds": OTP_EXPIRE_MINUTES * 60
    }

@router.post("/register-with-otp", response_model=Token)
def register_with_otp(data: RegisterRequest, req: Request, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    username = data.username.strip()
    full_name = data.full_name.strip()
    otp_code = data.otp.strip()
    role = data.role.strip() if data.role in ["Admin", "Employee"] else "Admin"
    if not role or role == "Employee":
        role = "Admin"

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long.")
    
    validate_password_strength(data.password)

    # Check for existing email or username
    existing_u = db.query(User).filter(User.username == username).first()
    if existing_u:
        if not existing_u.is_active:
            raise HTTPException(status_code=403, detail=f"🚫 Username '{username}' has been blocked by administrator.")
        raise HTTPException(status_code=400, detail=f"Username '{username}' is already taken.")

    existing_e = db.query(User).filter(User.email == email).first()
    if existing_e:
        if not existing_e.is_active:
            raise HTTPException(status_code=403, detail=f"🚫 Email '{email}' has been blocked by administrator.")
        raise HTTPException(status_code=400, detail=f"Email '{email}' is already registered.")

    # Validate OTP
    now = datetime.utcnow()
    valid_otp = db.query(OTPVerification).filter(
        OTPVerification.email == email,
        OTPVerification.otp_code == otp_code,
        OTPVerification.purpose == "registration",
        OTPVerification.is_used == False,
        OTPVerification.expires_at >= now
    ).first()

    if not valid_otp:
        log_activity(
            db=db,
            username=username,
            role="Guest",
            action="User Registration Failed",
            status="Failed",
            details=f"Invalid or expired OTP '{otp_code}' for email {email}",
            ip_address=req.client.host if req.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP. Please check your email or request a new OTP."
        )

    # Mark OTP as consumed
    valid_otp.is_used = True

    # Create new User
    new_user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=get_password_hash(data.password),
        role=role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_activity(
        db=db,
        username=new_user.username,
        role=new_user.role,
        action="User Registered",
        status="Success",
        details=f"New user registered successfully via Email OTP ({email})",
        ip_address=req.client.host if req.client else None
    )

    # Generate access token
    token = create_access_token(data={"sub": new_user.username, "role": new_user.role})

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": new_user.role,
        "username": new_user.username,
        "full_name": new_user.full_name,
        "email": new_user.email
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    return db.query(User).order_by(User.id.asc()).all()

@router.put("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    status_data: dict,
    req: Request,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User account not found.")
    
    # Prevent self lockout
    if target_user.id == admin_user.id or target_user.username == admin_user.username:
        raise HTTPException(
            status_code=400,
            detail="Security restriction: You cannot block or deactivate your own administrator account."
        )
    
    new_is_active = bool(status_data.get("is_active", not target_user.is_active))
    target_user.is_active = new_is_active
    db.commit()
    db.refresh(target_user)

    action_label = "User Account Activated" if target_user.is_active else "User Account Blocked"
    status_str = "Active" if target_user.is_active else "Blocked / Suspended"

    log_activity(
        db=db,
        username=admin_user.username,
        role=admin_user.role,
        action=action_label,
        status="Success",
        details=f"Admin '{admin_user.username}' changed user '{target_user.username}' ({target_user.full_name or 'N/A'}) status to '{status_str}'",
        ip_address=req.client.host if req.client else None
    )

    return target_user


# ==============================================================================
# FORGOT & RESET PASSWORD WORKFLOW (10-MINUTE EXPIRING SECURE LINK)
# ==============================================================================

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, req: Request, db: Session = Depends(get_db)):
    ident = data.identifier.strip()
    clean_ident = ident.lstrip("@").strip()

    # Find user by username or email
    user = db.query(User).filter(
        or_(
            User.username == ident,
            User.username == clean_ident,
            User.email == ident.lower()
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="No registered account found with that email or username. Please verify your details."
        )

    if not user.is_active:
        log_activity(
            db=db,
            username=user.username,
            role=user.role,
            action="Blocked User Password Reset Attempt",
            status="Denied",
            details=f"Blocked user '{user.username}' attempted password reset",
            ip_address=req.client.host if req.client else None
        )
        raise HTTPException(
            status_code=403,
            detail="🚫 This account is blocked/suspended by administrator. Password reset is disabled."
        )

    if not user.email or "@" not in user.email:
        raise HTTPException(
            status_code=400,
            detail="This account does not have a verified email address on file. Please contact your system administrator."
        )

    # Invalidate previous unused reset tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False
    ).update({"is_used": True})

    # Generate secure 48-character token
    token = secrets.token_urlsafe(36)
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    reset_record = PasswordResetToken(
        user_id=user.id,
        email=user.email,
        token=token,
        expires_at=expires_at,
        is_used=False
    )
    db.add(reset_record)
    db.commit()

    # Determine Base URL
    base_url = str(req.base_url).rstrip("/")
    reset_url = f"{base_url}/?reset_token={token}"

    user_display = user.full_name or user.username
    email_sent = send_password_reset_email(to_email=user.email, reset_url=reset_url, user_name=user_display)

    log_activity(
        db=db,
        username=user.username,
        role=user.role,
        action="Password Reset Requested",
        status="Success" if email_sent else "Warning",
        details=f"Password reset link generated for '{user.email}' (Valid 10 mins). Dispatch status: {email_sent}",
        ip_address=req.client.host if req.client else None
    )

    if not email_sent:
        raise HTTPException(
            status_code=500,
            detail="Failed to send password reset email. Please verify SMTP/Email relay configuration."
        )

    # Mask email for privacy (e.g. it***@gmail.com)
    email_parts = user.email.split("@")
    if len(email_parts[0]) > 2:
        masked_user = email_parts[0][:2] + "***"
    else:
        masked_user = email_parts[0][:1] + "***"
    masked_email = f"{masked_user}@{email_parts[1]}"

    return {
        "status": "success",
        "message": f"Password reset link has been dispatched to {masked_email}. Please check your inbox and click the link within 10 minutes.",
        "email": masked_email,
        "expires_in_seconds": 600
    }


@router.get("/verify-reset-token")
def verify_reset_token(token: str, db: Session = Depends(get_db)):
    if not token or not token.strip():
        raise HTTPException(status_code=400, detail="Missing reset token.")

    token_rec = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token.strip(),
        PasswordResetToken.is_used == False
    ).first()

    now = datetime.utcnow()
    if not token_rec:
        raise HTTPException(
            status_code=400,
            detail="This password reset link is invalid or has already been used. Please request a fresh reset link."
        )

    if token_rec.expires_at < now:
        raise HTTPException(
            status_code=400,
            detail="⚠️ This password reset link has expired (10-minute validity window elapsed). Please request a new link."
        )

    user = db.query(User).filter(User.id == token_rec.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="The account associated with this reset link is inactive or suspended."
        )

    remaining_seconds = int((token_rec.expires_at - now).total_seconds())

    return {
        "valid": True,
        "username": user.username,
        "full_name": user.full_name or user.username,
        "email": user.email,
        "remaining_seconds": max(remaining_seconds, 0)
    }


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, req: Request, db: Session = Depends(get_db)):
    token = data.token.strip()
    new_password = data.new_password

    if not token:
        raise HTTPException(status_code=400, detail="Missing password reset token.")

    validate_password_strength(new_password)

    token_rec = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.is_used == False
    ).first()

    now = datetime.utcnow()
    if not token_rec or token_rec.expires_at < now:
        raise HTTPException(
            status_code=400,
            detail="⚠️ This password reset link has expired or is invalid. Please request a fresh reset link."
        )

    user = db.query(User).filter(User.id == token_rec.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="🚫 This account is blocked by administrator.")

    # Update Password
    user.hashed_password = get_password_hash(new_password)
    token_rec.is_used = True
    db.commit()

    log_activity(
        db=db,
        username=user.username,
        role=user.role,
        action="Password Reset Completed",
        status="Success",
        details=f"User '{user.username}' successfully reset their password via secure email token.",
        ip_address=req.client.host if req.client else None
    )

    return {
        "status": "success",
        "message": "🎉 Password has been reset successfully! You can now sign in with your new password.",
        "username": user.username
    }

