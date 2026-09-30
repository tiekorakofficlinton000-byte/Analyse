"""
QuantBet Engine - Billing & Subscription Plans Module
Manages SaaS tiers, access gating, and MRR growth projection modeling.
"""

from typing import Dict, List, Any
from app.domain.models import SubscriptionTier, PlanInfo


AVAILABLE_PLANS: Dict[SubscriptionTier, PlanInfo] = {
    SubscriptionTier.FREE: PlanInfo(
        tier=SubscriptionTier.FREE,
        name="Free Starter",
        price_eur_month=0.0,
        price_fcfa_month=0,
        features=[
            "2 Value Bets par jour (EV limitée < 3%)",
            "Délai d'alerte de 15 minutes",
            "Simulateur xG de base",
            "Support communautaire Discord"
        ],
        access_ev_threshold=3.0,
        realtime_enabled=False,
        kelly_calculator_enabled=False,
        api_access=False
    ),
    SubscriptionTier.PRO: PlanInfo(
        tier=SubscriptionTier.PRO,
        name="Pro Quant Trader",
        price_eur_month=29.0,
        price_fcfa_month=19000,
        features=[
            "Signaux Value Bets temps réel illimités (EV jusqu'à +15%)",
            "Calculateur de mise Quarter-Kelly automatique",
            "Suivi de 12 bookmakers (Pinnacle, Bet365, 1xBet, etc.)",
            "Alertes instantanées en direct par notification",
            "Gestionnaire de bankroll & simulateur Monte Carlo"
        ],
        access_ev_threshold=15.0,
        realtime_enabled=True,
        kelly_calculator_enabled=True,
        api_access=False
    ),
    SubscriptionTier.SYNDICATE: PlanInfo(
        tier=SubscriptionTier.SYNDICATE,
        name="Syndicate Whale & VIP",
        price_eur_month=99.0,
        price_fcfa_month=65000,
        features=[
            "Tout le pack PRO inclus",
            "Radar Dropping Odds & détection de mouvements de cotes sharp",
            "Accès API REST + Webhooks direct trading",
            "Cercle privé des parieurs institutionnels",
            "Accompagnement et sizing personnalisé de bankroll"
        ],
        access_ev_threshold=99.0,
        realtime_enabled=True,
        kelly_calculator_enabled=True,
        api_access=True
    )
}


def calculate_mrr_projections(pro_subscribers: int, syndicate_subscribers: int = 150) -> Dict[str, Any]:
    """
    Financial model projecting SaaS revenue based on subscriber count.
    Answers the user's dream: 'plus de 1000 personnes vont utiliser la plateforme'.
    """
    pro_price_eur = AVAILABLE_PLANS[SubscriptionTier.PRO].price_eur_month
    pro_price_fcfa = AVAILABLE_PLANS[SubscriptionTier.PRO].price_fcfa_month
    synd_price_eur = AVAILABLE_PLANS[SubscriptionTier.SYNDICATE].price_eur_month
    synd_price_fcfa = AVAILABLE_PLANS[SubscriptionTier.SYNDICATE].price_fcfa_month

    mrr_eur = (pro_subscribers * pro_price_eur) + (syndicate_subscribers * synd_price_eur)
    mrr_fcfa = (pro_subscribers * pro_price_fcfa) + (syndicate_subscribers * synd_price_fcfa)
    arr_eur = mrr_eur * 12
    arr_fcfa = mrr_fcfa * 12

    # Estimated server infrastructure & odds API costs
    infra_cost_eur = 350.0  # Hosting, scraping proxies, rapid API feeds
    net_profit_eur = max(0.0, mrr_eur - infra_cost_eur)
    margin_pct = (net_profit_eur / mrr_eur * 100) if mrr_eur > 0 else 0

    return {
        "subscribers_pro": pro_subscribers,
        "subscribers_syndicate": syndicate_subscribers,
        "total_active_subscribers": pro_subscribers + syndicate_subscribers,
        "mrr_eur": round(mrr_eur, 2),
        "mrr_fcfa": int(mrr_fcfa),
        "arr_eur": round(arr_eur, 2),
        "arr_fcfa": int(arr_fcfa),
        "estimated_infra_cost_eur": infra_cost_eur,
        "net_monthly_profit_eur": round(net_profit_eur, 2),
        "profit_margin_pct": round(margin_pct, 1)
    }
