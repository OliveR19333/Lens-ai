"""Authentication + user management endpoints (spec §4.2, §12)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import authenticate_user, create_access_token, get_current_user, hash_password
from app.config import Settings, get_settings
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserCreateRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """`POST /auth/login` → returns JWT token (no auth required).

    Checks the ``users`` table first, then the bootstrap admin (spec §12).
    """
    if not authenticate_user(body.username, body.password, settings, db=db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(body.username, settings)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=dict)
def me(username: str = Depends(get_current_user)):
    """`GET /auth/me` → the current user's username."""
    return {"username": username}


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreateRequest,
    db: Session = Depends(get_db),
    _user: str = Depends(get_current_user),
):
    """`POST /auth/users` → create a team member (spec §12). Auth required.

    Small-team model: any authenticated user can add another (e.g. granting
    Devan Teaster access).
    """
    if db.query(User).filter(User.username == body.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        display_name=body.display_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)
