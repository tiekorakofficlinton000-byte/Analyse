"""
QuantBet Engine - Quantitative Analytics Endpoints
Runs Poisson/Dixon-Coles simulations, EV calculations, and Monte Carlo backtests.
"""

from fastapi import APIRouter
from app.domain.schemas import MatchSimRequest, MatchSimResponse, ProbabilityBreakdown, FairOddsBreakdown, ValueOpportunity
from app.modules.quant_engine.poisson_model import compute_match_probabilities
from app.modules.quant_engine.ev_calculator import calculate_expected_value, convert_prob_to_fair_odds
from app.modules.quant_engine.kelly_criterion import calculate_kelly_stake
import numpy as np

router = APIRouter(prefix="/quant", tags=["Quantitative Engine & Mathematics"])


@router.post("/simulate-match", response_model=MatchSimResponse)
async def simulate_match(req: MatchSimRequest):
    """
    Simulate fixture probabilities using Dixon-Coles corrected Poisson model.
    Evaluates EV and Kelly stake on all available bookmaker lines.
    """
    raw_probs = compute_match_probabilities(
        lambda_home=req.home_xg,
        mu_away=req.away_xg,
        rho=req.correlation_rho
    )

    fair_1 = convert_prob_to_fair_odds(raw_probs["p_home_win"])
    fair_x = convert_prob_to_fair_odds(raw_probs["p_draw"])
    fair_2 = convert_prob_to_fair_odds(raw_probs["p_away_win"])
    fair_ov = convert_prob_to_fair_odds(raw_probs["p_over_25"])
    fair_un = convert_prob_to_fair_odds(raw_probs["p_under_25"])

    # Analyze potential value opportunities
    opportunities = []

    # Market 1 (Home Win)
    if req.bookmaker_1:
        ev, has_val = calculate_expected_value(raw_probs["p_home_win"], req.bookmaker_1)
        kelly = calculate_kelly_stake(raw_probs["p_home_win"], req.bookmaker_1)
        opportunities.append(ValueOpportunity(
            market="1X2",
            selection=f"{req.home_team} (1)",
            bookmaker_odds=req.bookmaker_1,
            fair_odds=fair_1,
            edge_ev_pct=ev,
            has_value=has_val,
            recommended_stake_pct=kelly["recommended_stake_pct"],
            recommendation="Parier (Value Bet)" if has_val else "Pas de valeur (Éviter)"
        ))

    # Market X (Draw)
    if req.bookmaker_x:
        ev, has_val = calculate_expected_value(raw_probs["p_draw"], req.bookmaker_x)
        kelly = calculate_kelly_stake(raw_probs["p_draw"], req.bookmaker_x)
        opportunities.append(ValueOpportunity(
            market="1X2",
            selection="Match Nul (X)",
            bookmaker_odds=req.bookmaker_x,
            fair_odds=fair_x,
            edge_ev_pct=ev,
            has_value=has_val,
            recommended_stake_pct=kelly["recommended_stake_pct"],
            recommendation="Parier (Value Bet)" if has_val else "Pas de valeur (Éviter)"
        ))

    # Market 2 (Away Win)
    if req.bookmaker_2:
        ev, has_val = calculate_expected_value(raw_probs["p_away_win"], req.bookmaker_2)
        kelly = calculate_kelly_stake(raw_probs["p_away_win"], req.bookmaker_2)
        opportunities.append(ValueOpportunity(
            market="1X2",
            selection=f"{req.away_team} (2)",
            bookmaker_odds=req.bookmaker_2,
            fair_odds=fair_2,
            edge_ev_pct=ev,
            has_value=has_val,
            recommended_stake_pct=kelly["recommended_stake_pct"],
            recommendation="Parier (Value Bet)" if has_val else "Pas de valeur (Éviter)"
        ))

    # Market Over 2.5
    if req.bookmaker_over_25:
        ev, has_val = calculate_expected_value(raw_probs["p_over_25"], req.bookmaker_over_25)
        kelly = calculate_kelly_stake(raw_probs["p_over_25"], req.bookmaker_over_25)
        opportunities.append(ValueOpportunity(
            market="Total Buts",
            selection="Plus de 2.5 Buts",
            bookmaker_odds=req.bookmaker_over_25,
            fair_odds=fair_ov,
            edge_ev_pct=ev,
            has_value=has_val,
            recommended_stake_pct=kelly["recommended_stake_pct"],
            recommendation="Parier (Value Bet)" if has_val else "Pas de valeur (Éviter)"
        ))

    # Market Under 2.5
    if req.bookmaker_under_25:
        ev, has_val = calculate_expected_value(raw_probs["p_under_25"], req.bookmaker_under_25)
        kelly = calculate_kelly_stake(raw_probs["p_under_25"], req.bookmaker_under_25)
        opportunities.append(ValueOpportunity(
            market="Total Buts",
            selection="Moins de 2.5 Buts",
            bookmaker_odds=req.bookmaker_under_25,
            fair_odds=fair_un,
            edge_ev_pct=ev,
            has_value=has_val,
            recommended_stake_pct=kelly["recommended_stake_pct"],
            recommendation="Parier (Value Bet)" if has_val else "Pas de valeur (Éviter)"
        ))

    return MatchSimResponse(
        match_title=f"{req.home_team} vs {req.away_team}",
        home_xg=req.home_xg,
        away_xg=req.away_xg,
        probabilities=ProbabilityBreakdown(
            home_win_pct=round(raw_probs["p_home_win"] * 100, 1),
            draw_pct=round(raw_probs["p_draw"] * 100, 1),
            away_win_pct=round(raw_probs["p_away_win"] * 100, 1),
            over_25_pct=round(raw_probs["p_over_25"] * 100, 1),
            under_25_pct=round(raw_probs["p_under_25"] * 100, 1),
            btts_yes_pct=round(raw_probs["p_btts_yes"] * 100, 1),
            btts_no_pct=round(raw_probs["p_btts_no"] * 100, 1),
            most_likely_score=raw_probs["most_likely_score"],
            score_matrix=raw_probs["top_scores"]
        ),
        fair_odds=FairOddsBreakdown(
            fair_1=fair_1,
            fair_x=fair_x,
            fair_2=fair_2,
            fair_over_25=fair_ov,
            fair_under_25=fair_un
        ),
        value_analysis=opportunities
    )


@router.get("/monte-carlo-simulation")
async def run_monte_carlo(
    starting_bankroll: float = 1000.0,
    num_bets: int = 500,
    ev_edge_pct: float = 4.0,
    avg_odds: float = 2.05
):
    """
    Runs a deterministic seed Monte Carlo simulation demonstrating:
    1. Quant Value Bettor (+4% EV with Quarter-Kelly sizing)
    2. Flat Bettor (+4% EV with fixed 1.5% stake)
    3. Casual Bettor (-5% bookmaker margin vig loss)
    """
    np.random.seed(42)

    # True win probability to generate target EV
    # EV = p * b - 1  =>  p = (1 + EV) / b
    true_p = (1.0 + (ev_edge_pct / 100.0)) / avg_odds
    
    # Casual bettor win probability (negative EV due to -5% margin)
    casual_p = (1.0 - 0.05) / avg_odds

    kelly_curve = [starting_bankroll]
    flat_curve = [starting_bankroll]
    casual_curve = [starting_bankroll]

    current_kelly_bank = starting_bankroll
    current_flat_bank = starting_bankroll
    current_casual_bank = starting_bankroll

    # Quarter Kelly fraction
    raw_kelly_stake = ((true_p * avg_odds - 1.0) / (avg_odds - 1.0)) * 0.25
    clamped_kelly_stake = min(0.025, max(0.005, raw_kelly_stake))

    flat_stake_amount = starting_bankroll * 0.015

    step_interval = max(1, num_bets // 25)

    sampled_points = []
    sampled_points.append({
        "bet_index": 0,
        "kelly_equity": round(starting_bankroll, 2),
        "flat_equity": round(starting_bankroll, 2),
        "casual_equity": round(starting_bankroll, 2)
    })

    for i in range(1, num_bets + 1):
        # Simulate quant bet
        won_quant = np.random.rand() < true_p
        stake_k = current_kelly_bank * clamped_kelly_stake
        if won_quant:
            current_kelly_bank += stake_k * (avg_odds - 1.0)
            current_flat_bank += flat_stake_amount * (avg_odds - 1.0)
        else:
            current_kelly_bank -= stake_k
            current_flat_bank -= flat_stake_amount

        # Simulate casual bet
        won_casual = np.random.rand() < casual_p
        if won_casual:
            current_casual_bank += flat_stake_amount * (avg_odds - 1.0)
        else:
            current_casual_bank -= flat_stake_amount

        if i % step_interval == 0 or i == num_bets:
            sampled_points.append({
                "bet_index": i,
                "kelly_equity": round(max(0.0, current_kelly_bank), 2),
                "flat_equity": round(max(0.0, current_flat_bank), 2),
                "casual_equity": round(max(0.0, current_casual_bank), 2)
            })

    return {
        "starting_bankroll": starting_bankroll,
        "num_bets": num_bets,
        "edge_ev_pct": ev_edge_pct,
        "avg_odds": avg_odds,
        "final_kelly_bankroll": round(current_kelly_bank, 2),
        "final_flat_bankroll": round(current_flat_bank, 2),
        "final_casual_bankroll": round(current_casual_bank, 2),
        "growth_chart_data": sampled_points
    }
