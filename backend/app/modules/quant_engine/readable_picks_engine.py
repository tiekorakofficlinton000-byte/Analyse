"""
QuantBet Engine - Readability & Quality Selection Algorithm
Classifies and ranks betting markets by their statistical readability, risk resilience, and long-term quality.
"""

from typing import Dict, Any, List
import math
from app.modules.quant_engine.match_analyzer import _estimate_team_strength
from app.modules.quant_engine.poisson_model import compute_match_probabilities


def evaluate_market_readability(home_team: str, away_team: str) -> Dict[str, Any]:
    """
    Evaluates ALL possible markets for a given match and classifies them:
    - 💎 CHOIX DIAMANT (Ultra-Lisible, taux de réussite > 80%, idéal pour Cote 2)
    - 🟢 TRÈS BON CHOIX (Lisible & Régulier)
    - 🟡 CHOIX MOYEN (Sensible aux faits de jeu)
    - ⛔ MARCHÉ PIÈGE (Illisible, loterie bookmaker à fuir)
    """
    h_stat = _estimate_team_strength(home_team, is_home=True)
    a_stat = _estimate_team_strength(away_team, is_home=False)

    lambda_home = round(max(0.5, (h_stat["attack"] * a_stat["defense"] / 1.35) + h_stat.get("home_boost", 0.30)), 2)
    mu_away = round(max(0.3, (a_stat["attack"] * h_stat["defense"] / 1.40)), 2)

    probs = compute_match_probabilities(lambda_home, mu_away, rho=-0.11)
    p_home = probs["p_home_win"]
    p_draw = probs["p_draw"]
    p_away = probs["p_away_win"]
    p_1x = round(p_home + p_draw, 3)
    p_x2 = round(p_away + p_draw, 3)

    total_xg = lambda_home + mu_away
    p_over_05_ht = round(min(0.92, max(0.68, 1.0 - math.exp(-total_xg * 0.45))), 2)
    p_over_15 = round(min(0.95, max(0.65, 1.0 - (math.exp(-total_xg) * (1 + total_xg)))), 2)
    p_over_25 = round(probs["p_over_25"], 2)
    p_under_35 = round(min(0.94, max(0.50, 1.0 - (p_over_25 * 0.45))), 2)
    p_home_score = round(min(0.96, max(0.70, 1.0 - math.exp(-lambda_home))), 2)
    p_away_score = round(min(0.90, max(0.50, 1.0 - math.exp(-mu_away))), 2)
    p_btts = round(probs["p_btts_yes"], 2)

    # Catalog of evaluated markets with their intrinsic nature
    markets_raw = [
        {
            "name": f"Double Chance : {home_team} ou Nul (1X)",
            "market_type": "Double Chance",
            "odds": round(max(1.18, min(1.48, 1.0 / p_1x * 1.04)), 2),
            "win_prob_pct": round(p_1x * 100, 1),
            "variance_resilience": 95,
            "why_readable": f"Couvre 2 des 3 issues possibles du match. Même en cas de match nul accroché (0-0, 1-1), le pari est gagné.",
            "pitfall": "Cote un peu basse si prise seule, mais parfaite pour combiner et faire une Cote 2.00 solide."
        },
        {
            "name": "Plus de 1.5 Buts dans le match",
            "market_type": "Total Buts Sécurisé",
            "odds": round(max(1.20, min(1.45, 1.0 / p_over_15 * 1.03)), 2),
            "win_prob_pct": round(p_over_15 * 100, 1),
            "variance_resilience": 92,
            "why_readable": f"Ne dépend pas de qui gagne. Dès que 2 buts sont marqués (1-1, 2-0, 0-2), le pari est validé dès la 60e minute.",
            "pitfall": "Attention aux matchs de reprise ou météo extrême qui peuvent fermer le jeu."
        },
        {
            "name": f"{home_team} marque au moins 1 but (Over 0.5)",
            "market_type": "Buts Équipe",
            "odds": round(max(1.15, min(1.38, 1.0 / p_home_score * 1.03)), 2),
            "win_prob_pct": round(p_home_score * 100, 1),
            "variance_resilience": 94,
            "why_readable": f"{home_team} à domicile bénéficie du soutien de son public et génère {lambda_home} buts attendus.",
            "pitfall": "Cote parfois faible en solo (1.20 à 1.30)."
        },
        {
            "name": "Plus de 0.5 But en 1ère Mi-Temps",
            "market_type": "Mi-Temps Buts",
            "odds": round(max(1.25, min(1.50, 1.0 / p_over_05_ht * 1.04)), 2),
            "win_prob_pct": round(p_over_05_ht * 100, 1),
            "variance_resilience": 86,
            "why_readable": "Un seul but avant la pause suffit pour encaisser le gain.",
            "pitfall": "Les équipes frileuses qui s'observent 45 minutes."
        },
        {
            "name": "Moins de 3.5 Buts dans le match",
            "market_type": "Total Buts Sécurisé",
            "odds": round(max(1.22, min(1.42, 1.0 / p_under_35 * 1.04)), 2),
            "win_prob_pct": round(p_under_35 * 100, 1),
            "variance_resilience": 88,
            "why_readable": "Couvre une large palette de scores (0-0, 1-0, 2-0, 1-1, 2-1, 3-0).",
            "pitfall": "Un carton rouge précoce qui déséquilibre totalement le match."
        },
        {
            "name": f"Victoire Sèche de {home_team} (1)",
            "market_type": "1X2 Sèche",
            "odds": round(max(1.50, min(2.50, 1.0 / p_home)), 2),
            "win_prob_pct": round(p_home * 100, 1),
            "variance_resilience": 68,
            "why_readable": f"Bonne rentabilité si {home_team} est supérieur, mais vulnérable à un but égalisateur à la 92e minute.",
            "pitfall": "Ne couvre pas le match nul. Risque de perte sèche."
        },
        {
            "name": "Les Deux Équipes Marquent (BTTS - Oui)",
            "market_type": "Les Deux Marquent",
            "odds": round(max(1.65, min(2.20, 1.0 / p_btts)), 2),
            "win_prob_pct": round(p_btts * 100, 1),
            "variance_resilience": 70,
            "why_readable": "Intéressant si les deux défenses sont poreuses.",
            "pitfall": "Si le favori domine 3-0 sans laisser une occasion à l'adversaire, le pari est perdu."
        },
        {
            "name": "Score Exact ou Mi-Temps/Fin de Match",
            "market_type": "Loterie / Exotique",
            "odds": 6.50,
            "win_prob_pct": 14.5,
            "variance_resilience": 15,
            "why_readable": "ILLISIBLE. Trop de facteurs aléatoires.",
            "pitfall": "C'est sur ce marché que les bookmakers prennent leur plus grosse marge (12% à 18%). À FUIR ABSOLUMENT."
        }
    ]

    # Calculate global readability score for each market:
    # Readability Score = (Win Probability * 0.65) + (Variance Resilience * 0.35)
    ranked_markets = []
    for m in markets_raw:
        readability_score = int((m["win_prob_pct"] * 0.60) + (m["variance_resilience"] * 0.40))
        
        if readability_score >= 85:
            tier_badge = "💎 CHOIX DIAMANT (Ultra-Lisible)"
            badge_class = "diamond"
            recommended_role = "Idéal pour ticket Cote 2.00 sécurisée"
        elif readability_score >= 75:
            tier_badge = "🟢 TRÈS BON CHOIX (Sécurisé)"
            badge_class = "gold"
            recommended_role = "Excellent en solo ou combinaison"
        elif readability_score >= 60:
            tier_badge = "🟡 CHOIX ÉQUILIBRÉ (Moyen)"
            badge_class = "silver"
            recommended_role = "À jouer avec modération (cote plus haute)"
        else:
            tier_badge = "⛔ MARCHÉ PIÈGE (À Éviter)"
            badge_class = "danger"
            recommended_role = "Loterie bookmaker qui détruit la bankroll"

        ranked_markets.append({
            "name": m["name"],
            "market_type": m["market_type"],
            "odds": m["odds"],
            "win_prob_pct": m["win_prob_pct"],
            "readability_score": readability_score,
            "tier_badge": tier_badge,
            "badge_class": badge_class,
            "recommended_role": recommended_role,
            "why_readable": m["why_readable"],
            "pitfall": m["pitfall"]
        })

    # Sort descending by readability score
    ranked_markets.sort(key=lambda x: x["readability_score"], reverse=True)

    return {
        "match": f"{home_team} vs {away_team}",
        "home_team": home_team,
        "away_team": away_team,
        "best_diamond_pick": ranked_markets[0],
        "top_readable_picks": [m for m in ranked_markets if m["readability_score"] >= 80],
        "all_ranked_markets": ranked_markets,
        "rule_of_thumb": "Pour faire une Cote 2.00 solide, combinez 2 Choix Diamant (ex: 1.42 x 1.44 = 2.04). Ne touchez JAMAIS aux marchés pièges."
    }
