"""
QuantBet Engine - Core Domain Models & Entities
Mathematical structures for Dixon-Coles simulation, probability distributions,
and subscription tiers.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class SubscriptionTier(str, Enum):
    FREE = "FREE"
    FREE_TRIAL = "FREE_TRIAL"
    SIMPLE = "SIMPLE"
    PREMIUM = "PREMIUM"
    PRO = "PRO"
    SYNDICATE = "SYNDICATE"


class MarketType(str, Enum):
    HOME_WIN = "1"
    DRAW = "X"
    AWAY_WIN = "2"
    OVER_25 = "OVER_2.5"
    UNDER_25 = "UNDER_2.5"
    BTTS_YES = "BTTS_YES"
    BTTS_NO = "BTTS_NO"
    DOUBLE_CHANCE_1X = "1X"
    DOUBLE_CHANCE_X2 = "X2"
    DOUBLE_CHANCE_12 = "12"


class ValueBetSignal(BaseModel):
    id: str
    match_id: str
    home_team: str
    away_team: str
    league: str
    match_date: str
    market: MarketType
    bookmaker: str
    bookmaker_odds: float
    model_fair_odds: float
    model_probability: float
    expected_value_pct: float
    kelly_stake_pct: float
    liquidity_score: float
    created_at: str


class PlanInfo(BaseModel):
    tier: SubscriptionTier
    name: str
    price_eur_month: float
    price_fcfa_month: int
    features: List[str]
    access_ev_threshold: float = 15.0
    realtime_enabled: bool = True
    kelly_calculator_enabled: bool = True
    api_access: bool = False


class UserProfile(BaseModel):
    id: str
    email: str
    tier: SubscriptionTier = SubscriptionTier.FREE_TRIAL
    trial_days_remaining: int = 3
    daily_analysis_count: int = 0
    max_analyses: int = 5
    max_alternatives: int = 1
    has_cote2: bool = True
    has_cote3: bool = False
    has_cote5: bool = False
    created_at: str
