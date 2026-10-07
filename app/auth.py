import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import (
    SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,
    ADMIN_DEFAULT_USER, ADMIN_DEFAULT_PASSWORD,
    EMPLOYEE_DEFAULT_USER, EMPLOYEE_DEFAULT_PASSWORD
)
from app.database import get_db
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def init_default_users(db: Session):
    """Seed initial default users if database is fresh"""
    # Check Admin
    admin_user = db.query(User).filter(User.username == ADMIN_DEFAULT_USER).first()
    if not admin_user:
        admin_user = User(
            username=ADMIN_DEFAULT_USER,
            email="admin@company.com",
            hashed_password=get_password_hash(ADMIN_DEFAULT_PASSWORD),
            role="Admin",
            full_name="System Administrator",
            is_active=True
        )
        db.add(admin_user)
        db.commit()

    # Check Employee (Akhtar)
    emp_user = db.query(User).filter(User.username == EMPLOYEE_DEFAULT_USER).first()
    if not emp_user:
        emp_user = User(
            username=EMPLOYEE_DEFAULT_USER,
            email="akhtar@company.com",
            hashed_password=get_password_hash(EMPLOYEE_DEFAULT_PASSWORD),
            role="Employee",
            full_name="Akhtar",
            is_active=True
        )
        db.add(emp_user)
        db.commit()
    else:
        # Ensure correct password and name
        emp_user.hashed_password = get_password_hash(EMPLOYEE_DEFAULT_PASSWORD)
        emp_user.full_name = "Akhtar"
        db.commit()

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admin role required for this action."
        )
    return current_user
