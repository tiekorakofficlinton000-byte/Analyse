"""
QuantBet Engine - Unit Tests for On-Demand Analyzer, Cote 2 Builder, and Bankroll Mentor
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../lib")))

from app.modules.quant_engine.match_analyzer import analyze_match_on_demand
from app.modules.quant_engine.cote2_builder import generate_daily_cote_2
from app.modules.quant_engine.bankroll_mentor import simulate_compound_growth


def test_on_demand_match_analyzer():
    res = analyze_match_on_demand(
        home_team="Manchester City",
        away_team="Chelsea",
        home_odds=1.45,
        draw_odds=4.75,
        away_odds=7.00
    )
    assert res["home_team"] == "Manchester City"
    assert "readability_score" in res
    assert 0 <= res["readability_score"] <= 100
    assert "safe_pick" in res
    assert "value_pick" in res
    assert "trap_warning" in res
    assert res["safe_pick"]["win_probability_pct"] >= 70.0


def test_cote2_builder_target_range():
    ticket = generate_daily_cote_2()
    assert 1.90 <= ticket["combined_odds"] <= 2.20
    assert ticket["legs_count"] == 2
    assert ticket["joint_probability_pct"] >= 65.0
    for leg in ticket["legs"]:
        assert leg["odds"] > 1.0
        assert "why_this_pick" in leg


def test_bankroll_mentor_compound_preservation():
    # Simulate starting with 20,000 FCFA over 60 days with 66% win rate
    sim = simulate_compound_growth(initial_capital=20000.0, days=60, stake_pct=2.5, win_rate_pct=66.0)
    assert sim["final_capital"] > sim["initial_capital"]
    assert sim["roi_pct"] > 0
    assert len(sim["golden_rules"]) >= 5
    assert len(sim["trajectory"]) > 1
