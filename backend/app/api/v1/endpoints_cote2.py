"""
QuantBet Engine - Cote 2.00 Sécurisée Endpoints
Provides the institutional daily double ticket designed to double bankroll safely.
"""

from fastapi import APIRouter
from app.modules.quant_engine.cote2_builder import generate_daily_cote_2

router = APIRouter(prefix="/cote2", tags=["Générateur Cote 2.00 Sécurisée"])


@router.get("/daily-ticket")
async def get_daily_cote_2():
    """
    Retourne le ticket Cote 2.00 Sécurisée du jour :
    2 sélections ultra-lisibles combinées pour atteindre ~2.00 avec probabilité > 70%.
    """
    return generate_daily_cote_2()
