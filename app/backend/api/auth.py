"""Authentication endpoints."""

import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr, field_validator
from jose import jwt

from app.backend.db.session import get_db
from app.backend.db.models import User, UserSession
from app.backend.core.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ── Schemas ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Utilities ─────────────────────────────────────────────────────────────────

def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def generate_refresh_token() -> str:
    """Generate a secure random refresh token."""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """Hash the refresh token before storing — never store the raw token."""
    return hashlib.sha256(token.encode()).hexdigest()


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    db.refresh(user)
    return UserResponse(
        id=str(user.id),
        email=user.email,
        role=user.role,
        is_active=user.is_active,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # 1. تحقق المستخدم موجود
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # 2. تحقق الباسورد صح
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # 3. تحقق الحساب مفعّل
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    # 4. اعمل refresh token واحفظه مهشش بالـ sessions table
    raw_refresh_token = generate_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    session = UserSession(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=expires_at,
    )
    db.add(session)
    db.commit()

    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=raw_refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    # 1.