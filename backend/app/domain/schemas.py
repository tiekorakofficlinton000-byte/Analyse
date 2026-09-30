"""
QuantBet Engine - Pydantic Request & Response Schemas
Used for API validation, serialization, and OpenAPI documentation.
"""

from typing import Optional, List, Dict
from pydantic import BaseModel, Field, EmailStr
from app.domain.models import SubscriptionTier, MarketType, ValueBetSignal, PlanInfo


# --- Authentication Schemas ---
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password min 6 characters")
    initial_bankroll: Optional[float] = Field(1000.0, ge=50.0, description="Initial bankroll amount")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tier: SubscriptionTier
    email: str
    bankroll_eur: float


class UserResponse(BaseModel):
    id: str
    email: str
    tier: SubscriptionTier
    bankroll_eur: float
    created_at: str


# --- Quantitative Simulation Schemas ---
class MatchSimRequest(BaseModel):
    home_team: str = Field("Arsenal", description="Home team name")
    away_team: str = Field("Chelsea", description="Away team name")
    home_xg: float = Field(2.10, ge=0.1, le=8.0, description="Projected expected goals for Home")
    away_xg: float = Field(1.15, ge=0.1, le=8.0, description="Projected expected goals for Away")
    correlation_rho: float = Field(-0.11, ge=-0.5, le=0.5, description="Dixon-Coles bivariate low-score correlation")
    bookmaker_1: Optional[float] = Field(1.85, ge=1.01, description="Bookmaker odds for Home Win")
    bookmaker_x: Optional[float] = Field(3.80, ge=1.01, description="Bookmaker odds for Draw")
    bookmaker_2: Optional[float] = Field(4.50, ge=1.01, description="Bookmaker odds for Away Win")
    bookmaker_over_25: Optional[float] = Field(1.75, ge=1.01, description="Bookmaker odds for Over 2.5")
    bookmaker_under_25: Optional[float] = Field(2.15, ge=1.01, description="Bookmaker odds for Under 2.5")


class ProbabilityBreakdown(BaseModel):
    home_win_pct: float
    draw_pct: float
    away_win_pct: float
    over_25_pct: float
    under_25_pct: float
    btts_yes_pct: float
    btts_no_pct: float
    most_likely_score: str
    score_matrix: Dict[str, float]


class FairOddsBreakdown(BaseModel):
    fair_1: float
    fair_x: float
    fair_2: float
    fair_over_25: float
    fair_under_25: float


class ValueOpportunity(BaseModel):
    market: str
    selection: str
    bookmaker_odds: float
    fair_odds: float
    edge_ev_pct: float
    has_value: bool
    recommended_stake_pct: float
    recommendation: str


class MatchSimResponse(BaseModel):
    match_title: str
    home_xg: float
    away_xg: float
    probabilities: ProbabilityBreakdown
    fair_odds: FairOddsBreakdown
    value_analysis: List[ValueOpportunity]


# --- Billing Schemas ---
class UpgradePlanRequest(BaseModel):
    new_tier: SubscriptionTier


class BankrollUpdateRequest(BaseModel):
    bankroll_eur: float = Field(..., ge=10.0, description="Updated bankroll size")
