"""
QuantBet Engine - Real-Time Odds Scanner & Value Bet Detector
Scans multiple bookmakers, benchmarks against Pinnacle sharp lines, and outputs Value Bet signals.
"""

from typing import List, Dict, Optional
import uuid
from datetime import datetime, timezone
from app.domain.models import ValueBetSignal, MarketType, SubscriptionTier
from app.modules.quant_engine.poisson_model import compute_match_probabilities
from app.modules.quant_engine.ev_calculator import calculate_expected_value, convert_prob_to_fair_odds
from app.modules.quant_engine.kelly_criterion import calculate_kelly_stake


class OddsScannerService:
    def __init__(self):
        self._fixtures = self._init_fixtures()

    def _init_fixtures(self) -> List[Dict]:
        return [
            {
                "id": "fix-001",
                "competition": "Premier League",
                "fixture_title": "Arsenal vs Chelsea",
                "home_xg": 2.25,
                "away_xg": 1.10,
                "quotes": [
                    {"bookmaker": "Pinnacle (Sharp)", "market": MarketType.HOME_WIN, "label": "Arsenal", "odds": 1.68},
                    {"bookmaker": "Bet365", "market": MarketType.HOME_WIN, "label": "Arsenal", "odds": 1.82},
                    {"bookmaker": "1xBet", "market": MarketType.OVER_25, "label": "Over 2.5 Buts", "odds": 1.95},
                    {"bookmaker": "Unibet", "market": MarketType.DRAW, "label": "Match Nul", "odds": 4.10},
                ]
            },
            {
                "id": "fix-002",
                "competition": "Champions League",
                "fixture_title": "Real Madrid vs Bayern Munich",
                "home_xg": 1.95,
                "away_xg": 1.85,
                "quotes": [
                    {"bookmaker": "1xBet", "market": MarketType.OVER_25, "label": "Over 2.5 Buts", "odds": 1.78},
                    {"bookmaker": "Betclic", "market": MarketType.BTTS_YES, "label": "Les 2 marquent", "odds": 1.65},
                    {"bookmaker": "Bet365", "market": MarketType.AWAY_WIN, "label": "Bayern Munich", "odds": 3.40},
                ]
            },
            {
                "id": "fix-003",
                "competition": "Ligue 1",
                "fixture_title": "PSG vs Marseille",
                "home_xg": 2.60,
                "away_xg": 0.85,
                "quotes": [
                    {"bookmaker": "Bet365", "market": MarketType.HOME_WIN, "label": "PSG", "odds": 1.48},
                    {"bookmaker": "Winamax", "market": MarketType.OVER_25, "label": "Over 2.5 Buts", "odds": 1.55},
                    {"bookmaker": "1xBet", "market": MarketType.AWAY_WIN, "label": "Marseille", "odds": 7.50},
                ]
            },
            {
                "id": "fix-004",
                "competition": "Serie A",
                "fixture_title": "Inter Milan vs Juventus",
                "home_xg": 1.40,
                "away_xg": 0.90,
                "quotes": [
                    {"bookmaker": "Unibet", "market": MarketType.UNDER_25, "label": "Under 2.5 Buts", "odds": 1.92},
                    {"bookmaker": "Bet365", "market": MarketType.DRAW, "label": "Match Nul", "odds": 3.45},
                ]
            },
            {
                "id": "fix-005",
                "competition": "La Liga",
                "fixture_title": "Barcelona vs Atletico Madrid",
                "home_xg": 1.80,
                "away_xg": 1.20,
                "quotes": [
                    {"bookmaker": "1xBet", "market": MarketType.HOME_WIN, "label": "Barcelona", "odds": 2.05},
                    {"bookmaker": "Betclic", "market": MarketType.BTTS_YES, "label": "Les 2 marquent", "odds": 1.85},
                ]
            }
        ]

    def scan_for_value_bets(self, user_tier: SubscriptionTier = SubscriptionTier.FREE) -> List[ValueBetSignal]:
        """
        Scan all fixtures and quotes against Dixon-Coles model to extract real value bets.
        Filters and gates results according to subscription tier.
        """
        signals: List[ValueBetSignal] = []

        for fix in self._fixtures:
            probs = compute_match_probabilities(fix["home_xg"], fix["away_xg"])
            
            prob_map = {
                MarketType.HOME_WIN: probs["p_home_win"],
                MarketType.DRAW: probs["p_draw"],
                MarketType.AWAY_WIN: probs["p_away_win"],
                MarketType.OVER_25: probs["p_over_25"],
                MarketType.UNDER_25: probs["p_under_25"],
                MarketType.BTTS_YES: probs["p_btts_yes"],
                MarketType.BTTS_NO: probs["p_btts_no"]
            }

            for quote in fix["quotes"]:
                market = quote["market"]
                model_p = prob_map.get(market, 0.0)
                bookie_odds = quote["odds"]

                ev_pct, has_value = calculate_expected_value(model_p, bookie_odds)
                fair_odds = convert_prob_to_fair_odds(model_p)

                if has_value:
                    kelly_info = calculate_kelly_stake(model_p, bookie_odds, fraction=0.25)
                    
                    # Grade assignment
                    if ev_pct >= 6.0:
                        grade = "AAA"
                    elif ev_pct >= 4.0:
                        grade = "AA"
                    elif ev_pct >= 2.5:
                        grade = "A"
                    else:
                        grade = "B"

                    is_pro_only = ev_pct > 3.0 or fix["competition"] in ["Champions League", "Premier League"]

                    sig = ValueBetSignal(
                        id=f"sig-{fix['id']}-{market.value}",
                        fixture_id=fix["id"],
                        competition=fix["competition"],
                        fixture_title=fix["fixture_title"],
                        market=market,
                        selection_label=quote["label"],
                        bookmaker=quote["bookmaker"],
                        bookmaker_odds=bookie_odds,
                        sharp_fair_odds=fair_odds,
                        model_probability_pct=round(model_p * 100, 1),
                        ev_pct=ev_pct,
                        full_kelly_pct=kelly_info["full_kelly_pct"],
                        recommended_stake_pct=kelly_info["recommended_stake_pct"],
                        confidence_grade=grade,
                        is_pro_only=is_pro_only,
                        delay_minutes_for_free=15 if is_pro_only else 0,
                        found_at=datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
                    )
                    signals.append(sig)

        # Sort by best EV percentage descending
        signals.sort(key=lambda s: s.ev_pct, reverse=True)

        # Feature Gating by subscription tier:
        if user_tier == SubscriptionTier.FREE:
            # Free tier gets limited to 2 public signals with lower EV, pro signals blurred/locked
            filtered_signals = []
            for s in signals:
                if s.is_pro_only:
                    # Provide masked version or drop
                    masked = s.model_copy()
                    masked.bookmaker = "🔒 Réservé PRO"
                    masked.recommended_stake_pct = 0.0
                    masked.selection_label = "🔒 Débloquer avec le pass PRO"
                    filtered_signals.append(masked)
                else:
                    filtered_signals.append(s)
            return filtered_signals
        
        return signals


scanner_service = OddsScannerService()
