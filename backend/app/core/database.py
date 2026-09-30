"""
QuantBet Engine - Data Store & Persistence Layer
Provides lightweight thread-safe storage with seeded quantitative fixture data and user profiles.
"""

from typing import Dict, Optional, List
from datetime import datetime, timezone
import uuid
from app.domain.models import UserProfile, SubscriptionTier
from app.core.security import hash_password


class DatabaseRepository:
    def __init__(self):
        self._users: Dict[str, Dict] = {}
        self._init_seed_data()

    def _init_seed_data(self):
        # Demo Free User
        free_id = "usr-free-001"
        self._users["demo@free.com"] = {
            "id": free_id,
            "email": "demo@free.com",
            "hashed_password": hash_password("freepass123"),
            "tier": SubscriptionTier.FREE,
            "bankroll_eur": 500.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        }

        # Demo Pro Trader User
        pro_id = "usr-pro-002"
        self._users["trader@quant.com"] = {
            "id": pro_id,
            "email": "trader@quant.com",
            "hashed_password": hash_password("propass123"),
            "tier": SubscriptionTier.PRO,
            "bankroll_eur": 2500.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        }

        # Demo Syndicate Whale
        whale_id = "usr-whale-003"
        self._users["vip@syndicate.com"] = {
            "id": whale_id,
            "email": "vip@syndicate.com",
            "hashed_password": hash_password("syndicate123"),
            "tier": SubscriptionTier.SYNDICATE,
            "bankroll_eur": 25000.0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        }

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        return self._users.get(email.lower())

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        for u in self._users.values():
            if u["id"] == user_id:
                return u
        return None

    def create_user(self, email: str, raw_password: str, initial_bankroll: float = 1000.0) -> Dict:
        user_id = f"usr-{uuid.uuid4().hex[:8]}"
        user_record = {
            "id": user_id,
            "email": email.lower(),
            "hashed_password": hash_password(raw_password),
            "tier": SubscriptionTier.FREE,
            "bankroll_eur": initial_bankroll,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True
        }
        self._users[email.lower()] = user_record
        return user_record

    def update_user_tier(self, email: str, new_tier: SubscriptionTier) -> Optional[Dict]:
        user = self.get_user_by_email(email)
        if user:
            user["tier"] = new_tier
            return user
        return None

    def update_user_bankroll(self, email: str, new_bankroll: float) -> Optional[Dict]:
        user = self.get_user_by_email(email)
        if user:
            user["bankroll_eur"] = new_bankroll
            return user
        return None


db = DatabaseRepository()
