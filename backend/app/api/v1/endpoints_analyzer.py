"""
QuantBet Engine - Match Analyzer Endpoints
Provides on-demand analysis, verdict, safe picks, and bookmaker trap detection.
"""

from typing import Optional, List, Dict
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.modules.quant_engine.match_analyzer import analyze_match_on_demand, TEAMS_DATABASE

router = APIRouter(prefix="/analyzer", tags=["Analyseur de Matchs & Verdict à la Demande"])


class MatchVerdictRequest(BaseModel):
    home_team: str = Field(..., description="Équipe à domicile")
    away_team: str = Field(..., description="Équipe à l'extérieur")
    home_odds: Optional[float] = Field(None, description="Cote 1 bookmaker")
    draw_odds: Optional[float] = Field(None, description="Cote X bookmaker")
    away_odds: Optional[float] = Field(None, description="Cote 2 bookmaker")


@router.post("/evaluate-match")
async def evaluate_match(req: MatchVerdictRequest):
    """
    Évalue un match donné par l'utilisateur et rend un verdict mathématique clair :
    - Indice de Lisibilité (0-100)
    - Choix Blindé / Sécurisé (haute probabilité)
    - Choix Équilibré / Value
    - Piège Bookmaker à Éviter
    """
    result = analyze_match_on_demand(
        home_team=req.home_team,
        away_team=req.away_team,
        home_odds=req.home_odds,
        draw_odds=req.draw_odds,
        away_odds=req.away_odds
    )
    return result


@router.get("/available-teams")
async def list_available_teams():
    """Retourne la liste des équipes majeures pré-calibrées avec leurs ligues."""
    teams = []
    for name, data in TEAMS_DATABASE.items():
        teams.append({
            "name": name,
            "league": data.get("league", "Autre"),
            "style": data.get("tempo", "medium")
        })
    return {"teams": teams}
