"""
QuantBet Engine - Expected Value (EV) & Margin/Vig Stripper
Calculates mathematical Edge and Expected Value for any betting market.
"""

from typing import Dict, List, Optional, Tuple


def calculate_bookmaker_margin(odds_list: List[float]) -> float:
    """
    Calculate the total overround / vig margin of a bookmaker market.
    Example: 1X2 market with odds [1.90, 3.50, 4.20]
    Margin = (1/1.90 + 1/3.50 + 1/4.20) - 1.0
    """
    valid_odds = [o for o in odds_list if o and o > 1.0]
    if not valid_odds:
        return 0.0
    implied_sum = sum(1.0 / o for o in valid_odds)
    return max(0.0, implied_sum - 1.0)


def strip_vig_multiplicative(odds_list: List[float]) -> List[float]:
    """
    Remove bookmaker vig using multiplicative normalization.
    Returns fair odds without the bookmaker's cut.
    """
    valid = [o for o in odds_list if o and o > 1.0]
    if not valid:
        return odds_list
    raw_probs = [1.0 / o for o in valid]
    total_raw_prob = sum(raw_probs)
    fair_probs = [p / total_raw_prob for p in raw_probs]
    return [round(1.0 / p, 3) for p in fair_probs]


def calculate_expected_value(model_probability: float, decimal_odds: float) -> Tuple[float, bool]:
    """
    Calculate Expected Value (EV):
    EV = (Model_Probability * Decimal_Odds) - 1.0
    EV_pct = EV * 100
    
    A positive EV indicates a mathematically profitable long-term edge.
    """
    if decimal_odds <= 1.0 or model_probability <= 0.0:
        return 0.0, False

    ev = (model_probability * decimal_odds) - 1.0
    ev_pct = round(ev * 100.0, 2)
    has_value = ev_pct >= 2.0  # 2% minimum threshold
    return ev_pct, has_value


def convert_prob_to_fair_odds(probability: float) -> float:
    """Convert true probability into 100% fair decimal odds."""
    if probability <= 0.0001:
        return 999.0
    return round(1.0 / probability, 2)
