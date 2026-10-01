"""
QuantBet Engine - Match Analyzer Endpoints
Provides on-demand analysis, verdict, safe picks, bookmaker trap detection,
and enforces the 5 analyses/day quota for Simple plan & unlimited for Pro.
"""

from typing import Optional, List, Dict
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.modules.quant_engine.match_analyzer import analyze_match_on_demand, TEAMS_DATABASE
from app.core.database import db

router = APIRouter(prefix="/analyzer", tags=["Analyseur de Matchs & Verdict à la Demande"])


class MatchVerdictRequest(BaseModel):
    home_team: str = Field(..., description="Équipe à domicile")
    away_team: str = Field(..., description="Équipe à l'extérieur")
    user_email: Optional[str] = Field(None, description="Email utilisateur pour le suivi du quota")
    home_odds: Optional[float] = Field(None, description="Cote 1 bookmaker")
    draw_odds: Optional[float] = Field(None, description="Cote X bookmaker")
    away_odds: Optional[float] = Field(None, description="Cote 2 bookmaker")


@router.post("/evaluate-match")
async def evaluate_match(req: MatchVerdictRequest):
    """
    Évalue un match donné par l'utilisateur et rend un verdict mathématique clair.
    Enforce la règle : 5 analyses/jour pour la Formule Simple, analyses illimitées pour Pro.
    """
    # Check and record quota
    quota_check = db.record_analysis_run(req.user_email)
    if not quota_check["allowed"]:
        return {
            "quota_exceeded": True,
            "error_message": quota_check.get("error", "Quota de 5 analyses atteint aujourd'hui."),
            "analyses_remaining": 0,
            "upgrade_required": True
        }

    result = analyze_match_on_demand(
        home_team=req.home_team,
        away_team=req.away_team,
        home_odds=req.home_odds,
        draw_odds=req.draw_odds,
        away_odds=req.away_odds
    )
    result["quota_exceeded"] = False
    result["analyses_remaining"] = quota_check.get("remaining", 0)
    result["is_unlimited"] = quota_check.get("is_unlimited", False)
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
