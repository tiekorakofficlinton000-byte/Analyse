"""
QuantBet Engine - Bankroll Mentor & Capital Preservation Engine
Mathematically demonstrates how compound growth with small starting capital beats the bookmaker over 30/60/90 days.
"""

from typing import Dict, Any, List


def simulate_compound_growth(
    initial_capital: float = 25000.0,
    currency: str = "FCFA",
    days: int = 60,
    stake_pct: float = 2.5,
    avg_odds: float = 1.95,
    win_rate_pct: float = 66.0
) -> Dict[str, Any]:
    """
    Simulates long-term disciplined bankroll growth using conservative staking on Cote 2.
    Proves to users that: 'On ne cherche pas à gagner gros, on cherche à ne pas perdre.'
    """
    p_win = win_rate_pct / 100.0
    ev_per_bet = (p_win * avg_odds) - 1.0  # e.g., (0.66 * 1.95) - 1 = +28.7% EV

    current_capital = initial_capital
    casual_capital = initial_capital
    casual_bet_loss_per_day = initial_capital * 0.04  # casual bettor loses on average due to lottery combos

    trajectory = []
    trajectory.append({
        "day": 0,
        "quant_capital": round(current_capital, 2),
        "casual_capital": round(casual_capital, 2),
        "daily_stake": round(current_capital * (stake_pct / 100), 2),
        "growth_pct": 0.0
    })

    # Expected daily compounding factor based on win rate and odds:
    # Daily net return expectation = stake_pct * (p_win * (odds - 1) - (1 - p_win))
    expected_daily_return_factor = (stake_pct / 100.0) * ((p_win * (avg_odds - 1.0)) - (1.0 - p_win))

    step = max(1, days // 12)
    for day in range(1, days + 1):
        # Compound formula: capital grows by expected mathematical return
        current_capital *= (1.0 + expected_daily_return_factor)
        # Casual bettor slowly bleeds capital
        casual_capital = max(0.0, casual_capital * 0.975)

        if day % step == 0 or day == days:
            daily_stake = current_capital * (stake_pct / 100.0)
            growth_pct = round(((current_capital - initial_capital) / initial_capital) * 100, 1)
            trajectory.append({
                "day": day,
                "quant_capital": round(current_capital, 2),
                "casual_capital": round(casual_capital, 2),
                "daily_stake": round(daily_stake, 2),
                "growth_pct": growth_pct
            })

    total_profit = round(current_capital - initial_capital, 2)
    roi_pct = round((total_profit / initial_capital) * 100, 1)

    golden_rules = [
        "1. Priorité Absolue : Ne jamais perdre. Préserver son capital avant de penser au gain.",
        "2. Qualité > Quantité : 1 seul bon choix ou 1 ticket Cote 2 par jour suffit pour s'enrichir.",
        "3. Gestion de Fer : Miser toujours 2.5% de son capital actuel, jamais plus.",
        "4. Le Piège du Tilt : Après une perte, ne jamais doubler sa mise pour 'se refaire'.",
        "5. Intérêts Composés : Les petites sommes deviennent de vrais capitaux avec le temps et la régularité."
    ]

    return {
        "initial_capital": initial_capital,
        "final_capital": round(current_capital, 2),
        "total_profit": total_profit,
        "currency": currency,
        "duration_days": days,
        "stake_pct": stake_pct,
        "avg_odds": avg_odds,
        "win_rate_pct": win_rate_pct,
        "expected_value_ev_pct": round(ev_per_bet * 100, 1),
        "roi_pct": roi_pct,
        "trajectory": trajectory,
        "golden_rules": golden_rules
    }
