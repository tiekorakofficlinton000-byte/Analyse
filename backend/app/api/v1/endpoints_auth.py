"""
QuantBet Engine - Authentication Endpoints
Handles registration, login, and user account management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.domain.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse, BankrollUpdateRequest
from app.core.database import db
from app.core.security import create_access_token
from app.modules.auth.auth_service import authenticate_user, get_current_user_required

router = APIRouter(prefix="/auth", tags=["Authentication & User Security"])


@router.post("/register", response_model=TokenResponse)
async def register(request: UserRegisterRequest):
    existing = db.get_user_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà."
        )
    user = db.create_user(request.email, request.password, request.initial_bankroll)
    token = create_access_token({"sub": user["email"], "tier": user["tier"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        tier=user["tier"],
        email=user["email"],
        bankroll_eur=user["bankroll_eur"]
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect."
        )
    token = create_access_token({"sub": user["email"], "tier": user["tier"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        tier=user["tier"],
        email=user["email"],
        bankroll_eur=user["bankroll_eur"]
    )


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: dict = Depends(get_current_user_required)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        tier=current_user["tier"],
        bankroll_eur=current_user["bankroll_eur"],
        created_at=current_user["created_at"]
    )


@router.post("/update-bankroll", response_model=UserResponse)
async def update_bankroll(
    payload: BankrollUpdateRequest,
    current_user: dict = Depends(get_current_user_required)
):
    updated = db.update_user_bankroll(current_user["email"], payload.bankroll_eur)
    return UserResponse(
        id=updated["id"],
        email=updated["email"],
        tier=updated["tier"],
        bankroll_eur=updated["bankroll_eur"],
        created_at=updated["created_at"]
    )
