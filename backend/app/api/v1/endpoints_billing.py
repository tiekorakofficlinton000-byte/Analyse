"""
QuantBet Engine - Billing & Subscription Endpoints
Manages SaaS subscription tiers, plan upgrades, and business MRR projections.
"""

from typing import Dict, List, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.domain.models import PlanInfo, SubscriptionTier
from app.domain.schemas import UpgradePlanRequest, UserResponse
from app.modules.billing.plan_manager import AVAILABLE_PLANS, calculate_mrr_projections
from app.modules.auth.auth_service import get_current_user_required
from app.core.database import db

router = APIRouter(prefix="/billing", tags=["Subscriptions & Monetization"])


@router.get("/plans", response_model=List[PlanInfo])
async def list_subscription_plans():
    """List all available public tiers and pricing."""
    return list(AVAILABLE_PLANS.values())


@router.post("/upgrade", response_model=UserResponse)
async def upgrade_subscription(
    payload: UpgradePlanRequest,
    current_user: dict = Depends(get_current_user_required)
):
    """
    Simulate subscription upgrade (Stripe / Mobile Money checkout completion).
    Immediately elevates user permissions and unlocks pro features.
    """
    updated_user = db.update_user_tier(current_user["email"], payload.new_tier)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable.")
    
    return UserResponse(
        id=updated_user["id"],
        email=updated_user["email"],
        tier=updated_user["tier"],
        bankroll_eur=updated_user["bankroll_eur"],
        created_at=updated_user["created_at"]
    )


@router.get("/mrr-projections")
async def get_mrr_projections(
    pro_users: int = Query(1000, ge=0, description="Target count of Pro subscribers"),
    syndicate_users: int = Query(120, ge=0, description="Target count of VIP Syndicate subscribers")
):
    """
    Calculate SaaS Monthly Recurring Revenue (MRR) and ARR metrics.
    Demonstrates the financial model behind the 1,000+ subscriber milestone.
    """
    return calculate_mrr_projections(pro_subscribers=pro_users, syndicate_subscribers=syndicate_users)
