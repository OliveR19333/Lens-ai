"""Pure authentication decision logic (spec §12 — multi-user).

Kept free of passlib/jwt imports so it's unit-testable in the lightweight CI.
The real password hashing/verification is injected by ``auth.py``.
"""
from __future__ import annotations

from typing import Callable, Optional, Protocol


class UserRecord(Protocol):
    username: str
    password_hash: str
    is_active: bool


def decide_auth(
    username: str,
    password: str,
    user: Optional[UserRecord],
    *,
    admin_username: str,
    admin_password: str,
    verify: Callable[[str, str], bool],
) -> bool:
    """Decide whether credentials are valid.

    Order of precedence:
      1. A real DB user (must be active) → verify password against its hash.
      2. Otherwise, the bootstrap admin from settings (plaintext compare) — only
         when no DB user shadows that username.
    """
    if user is not None:
        if not getattr(user, "is_active", True):
            return False
        return verify(password, user.password_hash)
    return bool(username == admin_username and password == admin_password)
