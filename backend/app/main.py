"""
DuoSecur Pro Engine - Quantitative Sports Analytics Platform
Main Application Server (FastAPI + Async Python)
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title="DuoSecur Pro — Intelligence Engine",
    version=settings.VERSION,
    description="Moteur d'Aide à la Décision 100% Python Pur : Duo Cote 2.00 Sécurisée, Algorithme Dixon-Coles, Analyse à la Demande et Passerelle Mobile Money.",
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

# Static files mount
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def serve_preview_dashboard():
    """Serves the live interactive dashboard for browser preview."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "project": "DuoSecur Pro Intelligence Engine",
        "version": settings.VERSION,
        "status": "online"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "DuoSecur Pro Engine",
        "engine": "Dixon-Coles & Poisson Bivarié",
        "language": "Python 3.13"
    }
