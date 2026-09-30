"""
DuoSecur Pro Engine - Quantitative Sports Betting Intelligence Platform
100% PURE PYTHON HEADLESS REST API (ZERO HTML)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title="DuoSecur Pro — Headless Intelligence Engine",
    version=settings.VERSION,
    description="Moteur d'Aide à la Décision 100% Python Pur : Duo Cote 2.00 Sécurisée, Algorithme Dixon-Coles, Bot VIP Telegram et Passerelle Mobile Money.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all v1 API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", response_class=JSONResponse)
async def root_status():
    """Root endpoint returning platform status in pure JSON format (Zero HTML)."""
    return {
        "project": "DuoSecur Pro Intelligence Engine",
        "version": settings.VERSION,
        "status": "active",
        "stack": "100% Pure Python (FastAPI Async + Dixon-Coles Bivariate)",
        "ui_mode": "Zero HTML — Console CLI & Bot Telegram & JSON API",
        "endpoints": {
            "daily_cote_2": f"{settings.API_V1_PREFIX}/cote2/daily-ticket",
            "on_demand_match_verdict": f"{settings.API_V1_PREFIX}/analyzer/evaluate-match",
            "readable_markets_ranking": f"{settings.API_V1_PREFIX}/readable/rank-markets",
            "bankroll_mentor_compound": f"{settings.API_V1_PREFIX}/mentor/compound-simulation",
            "telegram_vip_alert": f"{settings.API_V1_PREFIX}/telegram/preview-daily-alert",
            "mobile_money_payments": f"{settings.API_V1_PREFIX}/payments/checkout",
            "interactive_api_docs": "/docs"
        }
    }


@app.get("/health", response_class=JSONResponse)
async def health_check():
    return {
        "status": "healthy",
        "service": "DuoSecur Pro Engine",
        "engine": "Dixon-Coles & Poisson Bivarié",
        "language": "Python 3.13"
    }
