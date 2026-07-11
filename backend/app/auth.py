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

from app.config import Settings, get_settings
from app.services.auth_logic import decide_auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def _pw_bytes(plain: str) -> bytes:
    # bcrypt only uses the first 72 bytes; truncate explicitly (newer bcrypt
    # raises instead of silently truncating).
    return plain.encode("utf-8")[:72]


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash (direct bcrypt — no passlib).

    passlib 1.7 is incompatible with bcrypt >= 4.1 (it can't read the version
    and crashes on a long internal test string), so we call bcrypt directly.
    """
    import bcrypt

    try:
        return bcrypt.checkpw(_pw_bytes(plain), hashed.encode("utf-8"))
    except Exception:
        return False


def hash_password(plain: str) -> str:
    import bcrypt

    return bcrypt.hashpw(_pw_bytes(plain), bcrypt.gensalt()).decode("utf-8")


def authenticate_user(username: str, password: str, settings: Settings, db=None) -> bool:
    """Validate credentials against DB users, falling back to the bootstrap admin.

    spec §12: real multi-user accounts live in the ``users`` table; the
    settings-based admin remains as a bootstrap so a fresh install can log in.
    """
    user = None
    if db is not None:
        from app.models import User

        user = db.query(User).filter(User.username == username).first()
    return decide_auth(
        username,
        password,
        user,
        admin_username=settings.admin_username,
        admin_password=settings.admin_password,
        verify=verify_password,
    )


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
