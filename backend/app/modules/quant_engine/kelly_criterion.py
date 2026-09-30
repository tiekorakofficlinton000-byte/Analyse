"""
QuantBet Engine - Kelly Criterion & Bankroll Risk Management
Calculates optimal bet sizing to maximize logarithmic wealth growth while capping drawdown.
"""

from typing import Dict, Any


def calculate_kelly_stake(
    probability: float,
    decimal_odds: float,
    fraction: float = 0.25,
    max_stake_cap_pct: float = 3.0
) -> Dict[str, float]:
    """
    Calculate Full Kelly and Fractional Kelly stake percentages.
    
    Formula:
    f* = (p * b - 1) / (b - 1)
    where:
    - p = true probability (0 to 1)
    - b = decimal odds
    - b - 1 = net fractional odds (net payout per unit staked)
    
    Returns:
    - full_kelly_pct: raw Kelly percentage
    - fractional_kelly_pct: scaled stake percentage (e.g. Quarter Kelly)
    - recommended_stake_pct: clamped to risk management guardrails (max_stake_cap_pct)
    """
    if decimal_odds <= 1.0 or probability <= 0.0:
        return {
            "full_kelly_pct": 0.0,
            "fractional_kelly_pct": 0.0,
            "recommended_stake_pct": 0.0
        }

    b_minus_1 = decimal_odds - 1.0
    ev = (probability * decimal_odds) - 1.0

    if ev <= 0.0:
        return {
            "full_kelly_pct": 0.0,
            "fractional_kelly_pct": 0.0,
            "recommended_stake_pct": 0.0
        }

    # Raw full kelly
    full_k = ev / b_minus_1
    full_k_pct = round(full_k * 100.0, 2)

    # Fractional kelly (default Quarter-Kelly = 0.25)
    frac_k_pct = round(full_k_pct * fraction, 2)

    # Risk safety guardrail clamp
    recommended_pct = min(frac_k_pct, max_stake_cap_pct)
    recommended_pct = max(0.0, recommended_pct)

    return {
        "full_kelly_pct": full_k_pct,
        "fractional_kelly_pct": frac_k_pct,
        "recommended_stake_pct": round(recommended_pct, 2)
    }
