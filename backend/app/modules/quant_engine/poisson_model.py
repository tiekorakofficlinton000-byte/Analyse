"""
QuantBet Engine - Dixon-Coles & Poisson Bivariate Model
Calculates exact score probabilities, 1X2 market outcomes, Over/Under, and BTTS.
"""

import math
from typing import Dict, Tuple, Any
import numpy as np
from scipy.stats import poisson


def tau_dixon_coles(x: int, y: int, lambda_home: float, mu_away: float, rho: float) -> float:
    """
    Dixon-Coles (1997) low-score adjustment factor to correct independence assumption in Poisson:
    - 0-0: 1 - lambda * mu * rho
    - 0-1: 1 + lambda * rho
    - 1-0: 1 + mu * rho
    - 1-1: 1 - rho
    - other: 1.0
    """
    if x == 0 and y == 0:
        return max(0.0001, 1.0 - (lambda_home * mu_away * rho))
    elif x == 0 and y == 1:
        return max(0.0001, 1.0 + (lambda_home * rho))
    elif x == 1 and y == 0:
        return max(0.0001, 1.0 + (mu_away * rho))
    elif x == 1 and y == 1:
        return max(0.0001, 1.0 - rho)
    else:
        return 1.0


def compute_match_probabilities(
    lambda_home: float,
    mu_away: float,
    rho: float = -0.11,
    max_goals: int = 7
) -> Dict[str, Any]:
    """
    Generate complete probability matrix using bivariate Poisson with Dixon-Coles adjustment.
    Returns:
    - 1X2 probabilities (home, draw, away)
    - Over / Under 2.5
    - BTTS (Both Teams To Score)
    - Full scoreline matrix
    - Most likely score
    """
    score_matrix = np.zeros((max_goals + 1, max_goals + 1))
    
    # Calculate unnormalized joint probabilities
    for x in range(max_goals + 1):
        p_home = poisson.pmf(x, lambda_home)
        for y in range(max_goals + 1):
            p_away = poisson.pmf(y, mu_away)
            tau = tau_dixon_coles(x, y, lambda_home, mu_away, rho)
            score_matrix[x, y] = p_home * p_away * tau

    # Normalize to ensure sum = 1.0
    total_prob = np.sum(score_matrix)
    if total_prob > 0:
        score_matrix = score_matrix / total_prob

    # Aggregate markets
    p_home_win = float(np.sum(np.tril(score_matrix, -1)))  # x > y
    p_draw = float(np.sum(np.diag(score_matrix)))          # x == y
    p_away_win = float(np.sum(np.triu(score_matrix, 1)))   # x < y

    # Over / Under 2.5
    p_under_25 = 0.0
    for x in range(max_goals + 1):
        for y in range(max_goals + 1):
            if x + y < 2.5:
                p_under_25 += float(score_matrix[x, y])
    p_over_25 = float(1.0 - p_under_25)

    # BTTS
    p_btts_yes = float(np.sum(score_matrix[1:, 1:]))
    p_btts_no = float(1.0 - p_btts_yes)

    # Most likely scoreline
    max_idx = np.unravel_index(np.argmax(score_matrix), score_matrix.shape)
    most_likely_score = f"{max_idx[0]}-{max_idx[1]}"

    # Top 5 most likely scores for display
    flat_scores = []
    for x in range(min(5, max_goals + 1)):
        for y in range(min(5, max_goals + 1)):
            flat_scores.append((f"{x}-{y}", float(score_matrix[x, y])))
    flat_scores.sort(key=lambda s: s[1], reverse=True)
    top_scores = {k: round(v * 100, 2) for k, v in flat_scores[:8]}

    return {
        "p_home_win": p_home_win,
        "p_draw": p_draw,
        "p_away_win": p_away_win,
        "p_over_25": p_over_25,
        "p_under_25": p_under_25,
        "p_btts_yes": p_btts_yes,
        "p_btts_no": p_btts_no,
        "most_likely_score": most_likely_score,
        "top_scores": top_scores
    }
