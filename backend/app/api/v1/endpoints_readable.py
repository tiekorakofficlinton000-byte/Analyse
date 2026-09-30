"""
QuantBet Engine - Readable Markets Endpoints
Classifies and ranks markets by their statistical readability and quality.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.modules.quant_engine.readable_picks_engine import evaluate_market_readability

router = APIRouter(prefix="/readable", tags=["Marchés Lisibles & Choix Optimaux"])


class MarketReadabilityRequest(BaseModel):
    home_team: str = Field(..., description="Équipe à domicile")
    away_team: str = Field(..., description="Équipe à l'extérieur")


@router.post("/rank-markets")
async def rank_markets(req: MarketReadabilityRequest):
    """
    Retourne la hiérarchie complète des marchés pour un match, classés du plus lisible au plus risqué :
    - 💎 Choix Diamant (Anti-variance, >80% de réussite)
    - 🟢 Bons Choix
    - 🟡 Choix Moyens
    - ⛔ Marchés Pièges à Fuir
    """
    return evaluate_market_readability(req.home_team, req.away_team)
