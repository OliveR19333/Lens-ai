"""Authentication endpoints (spec §4.2)."""
from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import authenticate_user, create_access_token
from app.config import Settings, get_settings
from app.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, settings: Settings = Depends(get_settings)):
    """`POST /auth/login` → returns JWT token (no auth required)."""
    if not authenticate_user(body.username, body.password, settings):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(body.username, settings)
    return TokenResponse(access_token=token)
