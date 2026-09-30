"""
QuantBet Engine - Value Bet Scanner Signals Endpoints
Provides real-time odds discrepancy signals with feature gating per tier.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.domain.models import ValueBetSignal, SubscriptionTier
from app.modules.odds_scanner.scanner_service import scanner_service
from app.modules.auth.auth_service import get_current_user_optional

router = APIRouter(prefix="/signals", tags=["Value Bets & Radar Feed"])


@router.get("/radar", response_model=List[ValueBetSignal])
async def get_live_value_bets(
    current_user: Optional[dict] = Depends(get_current_user_optional),
    min_ev: float = Query(2.0, ge=0.0, description="Minimum EV percentage filter")
):
    """
    Returns live value bet signals detected across bookmakers.
    Users with FREE plan see blurred/locked high-EV bets and delayed quotes.
    PRO and SYNDICATE subscribers get unlocked real-time data with Quarter-Kelly sizing.
    """
    tier = current_user["tier"] if current_user else SubscriptionTier.FREE
    signals = scanner_service.scan_for_value_bets(user_tier=tier)

    # Filter by user requested min EV
    filtered = [s for s in signals if s.ev_pct >= min_ev]
    return filtered
