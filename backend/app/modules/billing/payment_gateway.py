"""
QuantBet Engine - Multi-Provider Payment Gateway
Supports Mobile Money (Wave, Orange Money, MTN, Moov), Stripe/Cards, and Crypto.
"""

from typing import Dict, Any, List
import uuid
from datetime import datetime, timezone


SUPPORTED_PROVIDERS: List[Dict[str, Any]] = [
    {
        "id": "wave",
        "name": "Wave Mobile Money",
        "region": "Côte d'Ivoire, Sénégal, UEMOA",
        "currency": "FCFA",
        "fee_pct": 1.0,
        "is_instant": True
    },
    {
        "id": "orange_money",
        "name": "Orange Money",
        "region": "Afrique de l'Ouest & Centrale",
        "currency": "FCFA",
        "fee_pct": 1.5,
        "is_instant": True
    },
    {
        "id": "mtn_momo",
        "name": "MTN MoMo",
        "region": "Côte d'Ivoire, Bénin, Cameroun, Ghana",
        "currency": "FCFA",
        "fee_pct": 1.5,
        "is_instant": True
    },
    {
        "id": "stripe",
        "name": "Carte Bancaire (Visa / Mastercard)",
        "region": "International / Europe / Amérique",
        "currency": "EUR",
        "fee_pct": 2.9,
        "is_instant": True
    },
    {
        "id": "crypto_usdt",
        "name": "USDT (TRC-20 / Arbitrum)",
        "region": "Global / Anonyme",
        "currency": "USDT",
        "fee_pct": 0.5,
        "is_instant": True
    }
]


def initiate_subscription_payment(
    customer_phone_or_email: str,
    provider_id: str,
    plan_tier: str = "PRO",
    currency: str = "FCFA"
) -> Dict[str, Any]:
    """
    Creates a payment checkout intent for the subscription.
    """
    provider = next((p for p in SUPPORTED_PROVIDERS if p["id"] == provider_id), SUPPORTED_PROVIDERS[0])
    
    amount = 15000 if currency == "FCFA" else 22.90
    tx_id = f"tx-{uuid.uuid4().hex[:10]}"

    return {
        "transaction_id": tx_id,
        "status": "PENDING_CONFIRMATION",
        "customer": customer_phone_or_email,
        "provider": provider["name"],
        "plan_tier": plan_tier,
        "amount": amount,
        "currency": currency,
        "instructions": f"Veuillez valider le débit de {amount:,} {currency} sur votre compte {provider['name']} pour débloquer votre accès VIP.",
        "created_at": datetime.now(timezone.utc).isoformat()
    }


def confirm_subscription_payment(transaction_id: str) -> Dict[str, Any]:
    """
    Simulates webhook callback from Wave / Orange Money / Stripe activating the subscriber.
    """
    return {
        "transaction_id": transaction_id,
        "status": "SUCCESS_ACTIVATED",
        "activated_tier": "PRO",
        "validity_days": 30,
        "telegram_vip_link": "https://t.me/+QuantBet_VIP_Private_Invitelink",
        "confirmed_at": datetime.now(timezone.utc).isoformat()
    }
