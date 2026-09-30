"""
QuantBet Engine - Unit Tests for Cryptography, Security & Subscriptions
Validates PBKDF2 hashing, JWT access tokens, and feature gating.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.core.database import db
from app.domain.models import SubscriptionTier
from app.modules.odds_scanner.scanner_service import scanner_service
from app.modules.billing.plan_manager import calculate_mrr_projections


def test_password_hashing_and_verification():
    password = "VibeCodingSecurePass2026!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert "$" in hashed
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword123", hashed) is False


def test_jwt_token_creation_and_payload():
    payload = {"sub": "trader@quant.com", "tier": "PRO"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    
    assert decoded is not None
    assert decoded["sub"] == "trader@quant.com"
    assert decoded["tier"] == "PRO"
    assert "exp" in decoded


def test_subscription_scanner_gating():
    # Free tier should receive blurred/masked pro signals
    free_signals = scanner_service.scan_for_value_bets(user_tier=SubscriptionTier.FREE)
    assert len(free_signals) > 0
    # Check that at least some signals are masked for free users
    has_locked = any("🔒" in s.selection_label for s in free_signals)
    assert has_locked is True

    # Pro tier receives all unlocked signals
    pro_signals = scanner_service.scan_for_value_bets(user_tier=SubscriptionTier.PRO)
    for s in pro_signals:
        assert "🔒" not in s.selection_label


def test_mrr_projections_for_1000_subscribers():
    # 1000 Pro subscribers + 150 Syndicate Whales
    metrics = calculate_mrr_projections(pro_subscribers=1000, syndicate_subscribers=150)
    
    # 1000 * 29 = 29,000 + 150 * 99 = 14,850 => Total 43,850 EUR / month
    assert metrics["mrr_eur"] == 43850.0
    assert metrics["mrr_fcfa"] > 25000000  # More than 25M FCFA / month
    assert metrics["net_monthly_profit_eur"] > 40000.0
