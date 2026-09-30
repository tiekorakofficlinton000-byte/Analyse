"""
QuantBet Engine - V1 Master Router
Aggregates all API v1 domain sub-routers.
"""

from fastapi import APIRouter
from app.api.v1.endpoints_auth import router as auth_router
from app.api.v1.endpoints_quant import router as quant_router
from app.api.v1.endpoints_signals import router as signals_router
from app.api.v1.endpoints_billing import router as billing_router
from app.api.v1.endpoints_analyzer import router as analyzer_router
from app.api.v1.endpoints_cote2 import router as cote2_router
from app.api.v1.endpoints_bankroll_mentor import router as mentor_router
from app.api.v1.endpoints_telegram import router as telegram_router
from app.api.v1.endpoints_payments import router as payments_router
from app.api.v1.endpoints_readable import router as readable_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(quant_router)
api_router.include_router(signals_router)
api_router.include_router(billing_router)
api_router.include_router(analyzer_router)
api_router.include_router(cote2_router)
api_router.include_router(mentor_router)
api_router.include_router(telegram_router)
api_router.include_router(payments_router)
api_router.include_router(readable_router)
