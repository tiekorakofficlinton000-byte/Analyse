"""
QuantBet Engine - Unit Tests for Mathematical & Quantitative Models
Validates Poisson/Dixon-Coles probability matrices, EV formulas, and Kelly Criterion sizing.
"""

import pytest
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.modules.quant_engine.poisson_model import compute_match_probabilities, tau_dixon_coles
from app.modules.quant_engine.ev_calculator import calculate_expected_value, convert_prob_to_fair_odds, calculate_bookmaker_margin
from app.modules.quant_engine.kelly_criterion import calculate_kelly_stake


def test_dixon_coles_probability_conservation():
    """Ensure sum of all joint probabilities equals exactly 1.0 (100%)."""
    res = compute_match_probabilities(lambda_home=1.85, mu_away=1.20, rho=-0.11)
    
    p_1x2_sum = res["p_home_win"] + res["p_draw"] + res["p_away_win"]
    assert pytest.approx(p_1x2_sum, abs=1e-4) == 1.0

    p_ou_sum = res["p_over_25"] + res["p_under_25"]
    assert pytest.approx(p_ou_sum, abs=1e-4) == 1.0

    p_btts_sum = res["p_btts_yes"] + res["p_btts_no"]
    assert pytest.approx(p_btts_sum, abs=1e-4) == 1.0


def test_expected_value_calculation():
    """Verify EV formula: EV = (p * b) - 1."""
    # Test case: 55% true win probability, bookmaker gives odds 2.00
    # EV = (0.55 * 2.00) - 1 = 1.10 - 1 = +0.10 (+10.0%)
    ev_pct, has_val = calculate_expected_value(model_probability=0.55, decimal_odds=2.00)
    assert ev_pct == 10.0
    assert has_val is True

    # Test negative EV: 40% probability, odds 2.20 -> (0.40 * 2.20) - 1 = 0.88 - 1 = -12.0%
    ev_neg, has_val_neg = calculate_expected_value(model_probability=0.40, decimal_odds=2.20)
    assert ev_neg == -12.0
    assert has_val_neg is False


def test_kelly_criterion_quarter_scaling():
    """Verify Quarter Kelly properly protects bankroll."""
    # Probability = 0.60, Odds = 2.00
    # EV = (0.60 * 2.0) - 1 = +0.20
    # Full Kelly f* = 0.20 / (2.0 - 1) = 0.20 = 20.0%
    # Quarter Kelly = 20.0% * 0.25 = 5.0%
    # Risk Guardrail clamp (max 3.0%) should cap it at 3.0%
    res = calculate_kelly_stake(probability=0.60, decimal_odds=2.00, fraction=0.25, max_stake_cap_pct=3.0)
    assert res["full_kelly_pct"] == 20.0
    assert res["fractional_kelly_pct"] == 5.0
    assert res["recommended_stake_pct"] == 3.0


def test_fair_odds_conversion():
    """Verify fair odds = 1 / p."""
    assert convert_prob_to_fair_odds(0.50) == 2.00
    assert convert_prob_to_fair_odds(0.25) == 4.00
