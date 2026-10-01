"""
QuantBet Engine - Multi-Odds Tickets & Premium Matches Endpoints
Provides tickets (Cote 2.00, Cote 3.00, Cote 5.00) and deep match analyses of the week.
"""

from fastapi import APIRouter
from app.modules.quant_engine.cote2_builder import generate_daily_cote_2, get_all_combos_and_premium

router = APIRouter(prefix="/cote2", tags=["Tickets Multi-Cotes & Sélection Premium"])


@router.get("/daily-ticket")
async def get_daily_cote_2():
    """
    Retourne la sélection complète :
    - Tickets Cote 2.00, Cote 3.00 et Cote 5.00
    - Matchs Premium de la semaine très bien analysés
    """
    return generate_daily_cote_2()


@router.get("/tickets")
async def get_all_tickets():
    """
    Retourne les 3 formules de tickets combinés :
    - Cote 2.00 (Duo Blindé)
    - Cote 3.00 (Trio Équilibré)
    - Cote 5.00 (Quatuor Expert EV+)
    """
    data = get_all_combos_and_premium()
    return data["tickets"]


@router.get("/premium-matches")
async def get_premium_matches():
    """
    Retourne la sélection des matchs de la semaine décortiqués avec :
    xG, indice de lisibilité, analyse tactique, choix blindé, choix value et piège évité.
    """
    data = get_all_combos_and_premium()
    return data["premium_week_matches"]
