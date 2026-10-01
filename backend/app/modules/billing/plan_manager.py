"""
QuantBet Engine - Billing & Subscription Plans Module
Manages subscription tiers:
- Abonnement Simple : 1 000 FCFA / mois
- Abonnement Premium : 2 000 FCFA / mois
"""

from typing import Dict, List, Any


AVAILABLE_PLANS: Dict[str, Dict[str, Any]] = {
    "SIMPLE": {
        "tier": "SIMPLE",
        "name": "Abonnement Simple",
        "badge": "L'Essentiel Sécurisé",
        "price_fcfa_month": 1000,
        "price_eur_month": 1.50,
        "description": "Idéal pour débuter et doubler sa bankroll au quotidien sans stress.",
        "features": [
            "Ticket Cote 2.00 Sécurisée du Jour (Le Duo Blindé)",
            "Accès aux Marchés les Plus Lisibles (Le Filtre Anti-Aléa)",
            "Mise à jour matinale quotidienne des pronostics",
            "Support client réactif"
        ],
        "has_cote2": True,
        "has_cote3": False,
        "has_cote5": False,
        "has_premium_weekly_matches": False
    },
    "PREMIUM": {
        "tier": "PREMIUM",
        "name": "Abonnement Premium VIP",
        "badge": "Le Pack Complet Recommandé",
        "price_fcfa_month": 2000,
        "price_eur_month": 3.00,
        "description": "L'expérience complète avec les cotes 2, 3, 5 et les grands chocs décryptés.",
        "features": [
            "Tout le contenu de l'Abonnement Simple",
            "Ticket Cote 3.00 Sécurisé (Trio Équilibré)",
            "Ticket Cote 5.00 Expert EV+ (Quatuor Rentabilité)",
            "Matchs du Jour & de la Semaine Très Bien Analysés (xG, choix blindés, value picks, pièges évités)",
            "Analyseur de Matchs Libre & Verdict Impartial Illimité",
            "Alertes prioritaires des opportunités à haute valeur"
        ],
        "has_cote2": True,
        "has_cote3": True,
        "has_cote5": True,
        "has_premium_weekly_matches": True
    }
}


def get_plans_catalog() -> Dict[str, Any]:
    return {
        "plans": list(AVAILABLE_PLANS.values())
    }


def calculate_mrr_projections(pro_subscribers: int = 1000, syndicate_subscribers: int = 100) -> Dict[str, Any]:
    """Helper for internal SaaS calculations based on Simple (1000 F) and Premium (2000 F)."""
    mrr_fcfa = (pro_subscribers * 1000) + (syndicate_subscribers * 2000)
    arr_fcfa = mrr_fcfa * 12
    return {
        "subscribers_simple": pro_subscribers,
        "subscribers_premium": syndicate_subscribers,
        "total_active_subscribers": pro_subscribers + syndicate_subscribers,
        "mrr_fcfa": mrr_fcfa,
        "arr_fcfa": arr_fcfa,
        "mrr_eur": round(mrr_fcfa / 655.957, 2),
        "arr_eur": round(arr_fcfa / 655.957, 2)
    }
