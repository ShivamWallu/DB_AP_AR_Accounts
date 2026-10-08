from datetime import datetime, timedelta
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, OTPVerification
from app.schemas import (
    Token, LoginRequest, UserResponse,
    SendOTPRequest, RegisterRequest, OTPResponse
)
from app.auth import (
    verify_password, get_password_hash,
    create_access_token, get_current_user, require_admin
)
from app.services.audit_service import log_activity
from app.services.email_service import send_otp_email
from app.config import OTP_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(request_data: LoginRequest, req: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request_data.username).first()
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
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

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
        raise HTTPException(
            status_code=400,
            detail="An account is already registered with this email address. Please sign in."
        )
    
    if data.username:
        u_name = data.username.strip()
        existing_username = db.query(User).filter(User.username == u_name).first()
        if existing_username:
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
    # Ensure default is Admin as requested so all users get full access
    if not role or role == "Employee":
        role = "Admin"

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long.")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    # Check for existing email or username
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail=f"Username '{username}' is already taken.")
    if db.query(User).filter(User.email == email).first():
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
    return db.query(User).all()

