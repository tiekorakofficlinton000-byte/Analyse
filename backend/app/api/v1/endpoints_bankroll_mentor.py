"""
QuantBet Engine - Bankroll Mentor & Mathematical Management Endpoints
Simulates disciplined long-term capital preservation and compound interest.
"""

from typing import Optional
from fastapi import APIRouter, Query
from app.modules.quant_engine.bankroll_mentor import simulate_compound_growth

router = APIRouter(prefix="/mentor", tags=["Conseils Mathématiques & Gestion de Capital"])


@router.get("/compound-simulation")
async def get_compound_simulation(
    initial_capital: float = Query(25000.0, ge=1000.0, description="Capital de départ (FCFA ou EUR)"),
    currency: str = Query("FCFA", description="Devise: FCFA ou EUR"),
    days: int = Query(60, ge=15, le=180, description="Durée de projection en jours"),
    stake_pct: float = Query(2.5, ge=1.0, le=5.0, description="Pourcentage de mise par pari (recommandé 2.5%)"),
    win_rate_pct: float = Query(66.0, ge=50.0, le=85.0, description="Taux de réussite estimé")
):
    """
    Démontre mathématiquement comment sortir gagnant avec une petite somme :
    'On ne cherche pas à gagner gros, on cherche à ne pas perdre.'
    """
    return simulate_compound_growth(
        initial_capital=initial_capital,
        currency=currency,
        days=days,
        stake_pct=stake_pct,
        avg_odds=1.95,
        win_rate_pct=win_rate_pct
    )
