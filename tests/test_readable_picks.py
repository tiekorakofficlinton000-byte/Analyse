"""
QuantBet Engine - Unit Tests for Readable Picks Engine
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../lib")))

from app.modules.quant_engine.readable_picks_engine import evaluate_market_readability


def test_readable_market_ranking():
    res = evaluate_market_readability("Real Madrid", "Villarreal")
    assert "best_diamond_pick" in res
    assert "all_ranked_markets" in res
    assert len(res["all_ranked_markets"]) >= 6

    # Verify descending sort order by readability score
    scores = [m["readability_score"] for m in res["all_ranked_markets"]]
    assert scores == sorted(scores, reverse=True)

    # Ensure best pick has high win prob
    assert res["best_diamond_pick"]["win_prob_pct"] >= 70.0
    assert res["best_diamond_pick"]["readability_score"] >= 80
