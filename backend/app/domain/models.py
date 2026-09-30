"""
QuantBet Engine - Domain Models & Entities
Defines the core data structures and business representations.
"""

from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class SubscriptionTier(str, Enum):
    FREE = "FREE"
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


class OddsQuote(BaseModel):
    bookmaker: str
    odds_1: float
    odds_x: float
    odds_2: float
    odds_over_25: Optional[float] = None
    odds_under_25: Optional[float] = None
    odds_btts_yes: Optional[float] = None
    odds_btts_no: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MatchFixture(BaseModel):
    id: str
    competition: str
    home_team: str
    away_team: str
    match_date: str
    home_xg_projected: float
    away_xg_projected: float
    odds_quotes: List[OddsQuote] = []


class ValueBetSignal(BaseModel):
    id: str
    fixture_id: str
    competition: str
    fixture_title: str
    market: MarketType
    selection_label: str
    bookmaker: str
    bookmaker_odds: float
    sharp_fair_odds: float
    model_probability_pct: float
    ev_pct: float  # Expected Value in %
    full_kelly_pct: float
    recommended_stake_pct: float  # Fractional Kelly stake
    confidence_grade: str  # AAA, AA, A, B
    is_pro_only: bool = True
    delay_minutes_for_free: int = 15
    found_at: str


class PlanInfo(BaseModel):
    tier: SubscriptionTier
    name: str
    price_eur_month: float
    price_fcfa_month: int
    features: List[str]
    access_ev_threshold: float
    realtime_enabled: bool
    kelly_calculator_enabled: bool
    api_access: bool


class UserProfile(BaseModel):
    id: str
    email: str
    tier: SubscriptionTier = SubscriptionTier.FREE
    bankroll_eur: float = 1000.0
    created_at: str
    is_active: bool = True
