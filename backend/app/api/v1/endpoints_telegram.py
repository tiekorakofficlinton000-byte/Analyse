"""
QuantBet Engine - Telegram VIP Broadcast Endpoints
"""

from fastapi import APIRouter
from app.modules.notifications.telegram_bot import format_telegram_cote2_alert

router = APIRouter(prefix="/telegram", tags=["Canal VIP Telegram"])


@router.get("/preview-daily-alert")
async def preview_daily_alert():
    """Génère l'alerte Telegram prête à être diffusée aux abonnés VIP."""
    return format_telegram_cote2_alert()
