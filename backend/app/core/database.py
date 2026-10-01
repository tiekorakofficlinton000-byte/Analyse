"""
QuantBet Engine - Data Store & Persistence Layer
Provides storage for user accounts, trial tracking, daily quotas, and subscription statuses.
"""

from typing import Dict, Optional, List, Any
from datetime import datetime, timezone
import uuid
from app.domain.models import SubscriptionTier
from app.core.security import hash_password


class DatabaseRepository:
    def __init__(self):
        self._users: Dict[str, Dict] = {}
        self._init_seed_data()

    def _init_seed_data(self):
        # Demo user in Free Trial (3 days free)
        self.create_user(
            email="visiteur@demo.com",
            raw_password="demo123password",
            tier=SubscriptionTier.FREE_TRIAL,
            trial_days_remaining=3
        )

        # Demo subscriber Simple (1 000 F / mois)
        self.create_user(
            email="simple@demo.com",
            raw_password="simple123password",
            tier=SubscriptionTier.SIMPLE,
            trial_days_remaining=0
        )

        # Demo subscriber Pro VIP (2 000 F / mois)
        self.create_user(
            email="pro@demo.com",
            raw_password="pro123password",
            tier=SubscriptionTier.PREMIUM,
            trial_days_remaining=0
        )

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        return self._users.get(email.lower())

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        for u in self._users.values():
            if u["id"] == user_id:
                return u
        return None

    def create_user(
        self,
        email: str,
        raw_password: str,
        tier: SubscriptionTier = SubscriptionTier.FREE_TRIAL,
        trial_days_remaining: int = 3
    ) -> Dict:
        user_id = f"usr-{uuid.uuid4().hex[:8]}"
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        user_record = {
            "id": user_id,
            "email": email.lower(),
            "hashed_password": hash_password(raw_password),
            "tier": tier,
            "trial_days_remaining": trial_days_remaining,
            "daily_analysis_count": 0,
            "last_analysis_date": today_str,
            "bankroll_eur": 1000.0,
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

    def get_user_quota(self, email: Optional[str]) -> Dict[str, Any]:
        """Calculates permissions and remaining analyses based on user tier."""
        if not email:
            return {
                "tier": "ANONYMOUS",
                "is_logged_in": False,
                "trial_days_remaining": 0,
                "daily_analysis_count": 0,
                "max_analyses": 5,
                "analyses_remaining": 5,
                "max_alternatives": 1,
                "has_cote2": True,
                "has_cote3": False,
                "has_cote5": False,
            }

        user = self.get_user_by_email(email)
        if not user:
            return {
                "tier": "ANONYMOUS",
                "is_logged_in": False,
                "trial_days_remaining": 0,
                "daily_analysis_count": 0,
                "max_analyses": 5,
                "analyses_remaining": 5,
                "max_alternatives": 1,
                "has_cote2": True,
                "has_cote3": False,
                "has_cote5": False,
            }

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if user.get("last_analysis_date") != today_str:
            user["daily_analysis_count"] = 0
            user["last_analysis_date"] = today_str

        tier = user.get("tier", SubscriptionTier.FREE_TRIAL)
        is_pro = tier in [SubscriptionTier.PREMIUM, SubscriptionTier.PRO]
        max_analyses = 9999 if is_pro else 5
        used = user.get("daily_analysis_count", 0)
        remaining = 9999 if is_pro else max(0, 5 - used)

        return {
            "id": user["id"],
            "email": user["email"],
            "tier": tier,
            "is_logged_in": True,
            "trial_days_remaining": user.get("trial_days_remaining", 3),
            "daily_analysis_count": used,
            "max_analyses": max_analyses,
            "analyses_remaining": remaining,
            "max_alternatives": 5 if is_pro else 1,
            "has_cote2": True,
            "has_cote3": is_pro,
            "has_cote5": is_pro,
            "created_at": user.get("created_at", "")
        }

    def record_analysis_run(self, email: Optional[str]) -> Dict[str, Any]:
        """Validates and increments daily quota for manual team analyses."""
        quota = self.get_user_quota(email)
        if quota.get("tier") in [SubscriptionTier.PREMIUM, SubscriptionTier.PRO]:
            return {
                "allowed": True,
                "is_unlimited": True,
                "remaining": 9999,
                "tier": quota.get("tier")
            }

        user = self.get_user_by_email(email) if email else None
        if not user:
            # For anonymous visitors, allow up to 5 per session/day
            return {
                "allowed": True,
                "is_unlimited": False,
                "remaining": 4,
                "tier": "ANONYMOUS"
            }

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if user.get("last_analysis_date") != today_str:
            user["daily_analysis_count"] = 0
            user["last_analysis_date"] = today_str

        used = user.get("daily_analysis_count", 0)
        if used >= 5:
            return {
                "allowed": False,
                "is_unlimited": False,
                "remaining": 0,
                "error": "Quota journalier atteint (5/5 analyses). Passez au pack Pro (2 000 F / mois) pour des analyses illimitées !",
                "tier": user["tier"]
            }

        user["daily_analysis_count"] = used + 1
        remaining = max(0, 5 - user["daily_analysis_count"])
        return {
            "allowed": True,
            "is_unlimited": False,
            "remaining": remaining,
            "count": user["daily_analysis_count"],
            "tier": user["tier"]
        }


db = DatabaseRepository()
