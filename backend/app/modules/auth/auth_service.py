"""
QuantBet Engine - Authentication & User Session Service
Handles JWT authentication, token decoding, and authorization guards.
"""

from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import verify_password, create_access_token, decode_access_token
from app.core.database import db
from app.domain.models import SubscriptionTier


security_bearer = HTTPBearer(auto_error=False)


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    user = db.get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


async def get_current_user_optional(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Optional[Dict]:
    """Extract user if bearer token is present, otherwise return None (for anonymous / demo mode)."""
    if not auth or not auth.credentials:
        return None
    payload = decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        return None
    user = db.get_user_by_email(payload["sub"])
    return user


async def get_current_user_required(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer)
) -> Dict:
    """Enforce authentication for protected routes."""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expirée ou jeton d'authentification manquant."
        )
    payload = decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Jeton d'authentification invalide."
        )
    user = db.get_user_by_email(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur introuvable."
        )
    return user


def require_tier(minimum_tier: SubscriptionTier):
    """Decorator / dependency factory to restrict routes based on subscription level."""
    async def tier_checker(user: Dict = Depends(get_current_user_required)) -> Dict:
        tier_levels = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.PRO: 1,
            SubscriptionTier.SYNDICATE: 2
        }
        user_tier_level = tier_levels.get(user["tier"], 0)
        min_tier_level = tier_levels.get(minimum_tier, 0)

        if user_tier_level < min_tier_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cette ressource requiert le niveau d'abonnement {minimum_tier.value}. Veuillez mettre à niveau votre plan."
            )
        return user
    return tier_checker
