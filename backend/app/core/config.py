"""
QuantBet Engine - Core Configuration
Pydantic v2 Settings for secure configuration management.
"""

from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "QuantBet Intelligence Engine"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "quantbet-production-grade-master-secret-key-3847291048"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Quant Settings
    DEFAULT_KELLY_FRACTION: float = 0.25  # Quarter Kelly
    MAX_STAKE_PCT: float = 3.0  # Max 3% of bankroll per single bet
    MIN_VALUE_BET_EV_PCT: float = 2.0  # Minimum EV to trigger signal
    SHARP_BENCHMARK: str = "Pinnacle"


settings = Settings()
