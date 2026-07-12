"""Authentication endpoints: register, login, refresh, logout.

Refresh tokens are delivered as an httpOnly cookie so they're never
reachable from browser JS (and therefore not stealable via XSS). Every
endpoint also accepts the token in the request body as a fallback, for
clients that don't carry cookies (mobile apps, CLI tools, server-to-server
callers).
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from core.config import settings
from core.security import (
    clear_refresh_cookie,
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expiry,
    set_refresh_cookie,
    verify_password,
)
from db.models import User, UserSession
from db.session import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_session(db: Session, user: User) -> str:
    """Create a new refresh-token session row and return the raw (unhashed) token."""
    raw_token = generate_refresh_token()
    db.add(
        UserSession(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_token),
            expires_at=refresh_token_expiry(),
        )
    )
    db.commit()
    return raw_token


def _extract_refresh_token(request: Request, body_token: str | None) -> str | None:
    """Prefer the httpOnly cookie; fall back to the request body for clients
    that don't send cookies."""
    return request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME) or body_token


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
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    refresh_token = _issue_session(db, user)
    set_refresh_cookie(response, refresh_token)
    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    request: Request,
    response: Response,
    payload: RefreshRequest = RefreshRequest(),
    db: Session = Depends(get_db),
):
    token = _extract_refresh_token(request, payload.refresh_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided.",
        )

    token_hash = hash_refresh_token(token)
    user_session = db.query(UserSession).filter(
        UserSession.token_hash == token_hash
    ).first()

    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if user_session.expires_at < datetime.now(timezone.utc):
        db.delete(user_session)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired.",
        )

    user = db.query(User).filter(User.id == user_session.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive.",
        )

    # Rotate on every use: the old token stops working even if it leaked.
    new_refresh_token = generate_refresh_token()
    user_session.token_hash = hash_refresh_token(new_refresh_token)
    user_session.expires_at = refresh_token_expiry()
    db.commit()

    set_refresh_cookie(response, new_refresh_token)
    return TokenResponse(
        access_token=create_access_token(user),
        refresh_token=new_refresh_token,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: Request,
    response: Response,
    payload: RefreshRequest = RefreshRequest(),
    db: Session = Depends(get_db),
) -> Response:
    """Invalidate the current refresh token and clear its cookie."""
    token = _extract_refresh_token(request, payload.refresh_token)
    if token:
        token_hash = hash_refresh_token(token)
        db.query(UserSession).filter(UserSession.token_hash == token_hash).delete()
        db.commit()

    clear_refresh_cookie(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)