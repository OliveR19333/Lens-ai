"""JWT authentication (spec §4.1 — PyJWT, single user / small team).

Phase 1 ships a single bootstrap admin account from settings. Replace
``authenticate_user`` with a real user table for Phase 4 multi-user support
(spec §12 — "Devan Teaster access").
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from app.config import Settings, get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def authenticate_user(username: str, password: str, settings: Settings) -> bool:
    """Validate credentials against the bootstrap admin account."""
    if username != settings.admin_username:
        return False
    # Bootstrap account stores the password in settings; compare directly.
    # (When a user table is added, switch to verify_password against a hash.)
    return password == settings.admin_password


def create_access_token(subject: str, settings: Settings) -> str:
    expire = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
        minutes=settings.jwt_expire_minutes
    )
    payload = {"sub": subject, "exp": expire, "iat": dt.datetime.now(dt.timezone.utc)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    settings: Settings = Depends(get_settings),
) -> str:
    """FastAPI dependency: decode the bearer token, return the username."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        return subject
    except jwt.PyJWTError:
        raise credentials_exception
