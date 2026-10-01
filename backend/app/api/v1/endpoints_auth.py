"""
QuantBet Engine - Authentication Endpoints
Handles registration (email + password with 3 days free trial), login, and user profile quotas.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.domain.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from app.domain.models import SubscriptionTier
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
            detail="Un compte avec cet email existe déjà. Veuillez vous connecter."
        )
    # Default newly registered users to 3 days free trial
    user = db.create_user(
        email=request.email,
        raw_password=request.password,
        tier=SubscriptionTier.FREE_TRIAL,
        trial_days_remaining=3
    )
    quota = db.get_user_quota(user["email"])
    token = create_access_token({"sub": user["email"], "tier": user["tier"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        tier=user["tier"],
        email=user["email"],
        trial_days_remaining=quota["trial_days_remaining"],
        daily_analysis_count=quota["daily_analysis_count"],
        max_analyses=quota["max_analyses"],
        analyses_remaining=quota["analyses_remaining"],
        max_alternatives=quota["max_alternatives"],
        has_cote2=quota["has_cote2"],
        has_cote3=quota["has_cote3"],
        has_cote5=quota["has_cote5"]
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    user = authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect."
        )
    quota = db.get_user_quota(user["email"])
    token = create_access_token({"sub": user["email"], "tier": user["tier"]})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        tier=user["tier"],
        email=user["email"],
        trial_days_remaining=quota["trial_days_remaining"],
        daily_analysis_count=quota["daily_analysis_count"],
        max_analyses=quota["max_analyses"],
        analyses_remaining=quota["analyses_remaining"],
        max_alternatives=quota["max_alternatives"],
        has_cote2=quota["has_cote2"],
        has_cote3=quota["has_cote3"],
        has_cote5=quota["has_cote5"]
    )


@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user_required)):
    quota = db.get_user_quota(current_user["email"])
    return quota


@router.get("/quota")
async def get_quota_by_email(email: str = ""):
    """Returns permissions and quota for a given email or guest."""
    return db.get_user_quota(email)
