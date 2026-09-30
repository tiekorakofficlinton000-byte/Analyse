"""
QuantBet Engine - VIP Telegram Bot & Broadcast Dispatcher
Generates and broadcasts institutional alerts for the Cote 2.00 Sécurisée and Match Verdicts.
"""

from typing import Dict, Any
from datetime import datetime, timezone
from app.modules.quant_engine.cote2_builder import generate_daily_cote_2


def format_telegram_cote2_alert() -> Dict[str, Any]:
    """
    Formats the daily Cote 2.00 into a high-converting Telegram VIP broadcast message.
    """
    ticket = generate_daily_cote_2()
    now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y")

    lines = [
        "🔥 **QUANTBET VIP — LE TICKET COTE 2.00 DU JOUR** 🔥",
        f"📅 Date : {now_str}",
        "━━━━━━━━━━━━━━━━━━━━━━",
        "🎯 **PHILOSOPHIE :** « Ne pas chercher à gagner gros, chercher à ne pas perdre. »",
        "━━━━━━━━━━━━━━━━━━━━━━\n"
    ]

    for i, leg in enumerate(ticket["legs"], 1):
        lines.append(f"⚽ **SÉLECTION #{i} :** {leg['match']}")
        lines.append(f"🏆 {leg['competition']} ({leg['time']})")
        lines.append(f"👉 **Choix :** `{leg['selection']}`")
        lines.append(f"📈 **Cote :** `{leg['odds']:.2f}` (Fiabilité : {leg['individual_win_prob_pct']}%)")
        lines.append(f"💡 **Pourquoi :** {leg['why_this_pick']}")
        lines.append(f"🚫 **Piège Évité :** {leg['trap_avoided']}\n")

    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append(f"📊 **COTE COMBINÉE TOTALE :** `{ticket['combined_odds']:.2f}`")
    lines.append(f"🛡️ **PROBABILITÉ CONJOINTE :** `{ticket['joint_probability_pct']}%`")
    lines.append(f"⚖️ **GESTION DE CAPITAL STRICTE :** Misez exactement 2.5% de votre bankroll.")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("⚠️ *Rappel : Aucun combiné de 10 matchs. La discipline quotidienne bat le bookmaker.*")

    message_text = "\n".join(lines)

    return {
        "channel": "@QuantBet_VIP_Club",
        "subscribers_reached": 1024,
        "raw_message": message_text,
        "combined_odds": ticket["combined_odds"],
        "joint_probability": ticket["joint_probability_pct"],
        "status": "READY_TO_DISPATCH"
    }
