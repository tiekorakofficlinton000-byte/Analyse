"""
QuantBet Engine - Mobile Money & Card Payment Endpoints
Supports subscription plans:
- Simple : 1 000 FCFA / mois (après 3 jours gratuits)
- Pro VIP : 2 000 FCFA / mois
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional
from app.modules.billing.payment_gateway import SUPPORTED_PROVIDERS, initiate_subscription_payment, confirm_subscription_payment
from app.modules.billing.plan_manager import get_plans_catalog
from app.domain.models import SubscriptionTier
from app.core.database import db

router = APIRouter(prefix="/payments", tags=["Paiements Abonnements (Mobile Money & Stripe)"])


class PaymentIntentRequest(BaseModel):
    customer_phone_or_email: str = Field(..., description="Numéro Mobile Money (Wave, Orange, MTN) ou email")
    provider_id: str = Field("wave", description="Fournisseur: wave, orange_money, mtn_momo, stripe, crypto_usdt")
    plan_tier: str = Field("PREMIUM", description="Formule: SIMPLE (1 000 FCFA) ou PREMIUM (2 000 FCFA)")
    user_email: Optional[str] = Field(None, description="Email du compte connecté")
    currency: str = Field("FCFA", description="Devise: FCFA ou EUR")


@router.get("/plans")
async def list_subscription_plans():
    """Retourne la grille des deux abonnements (Simple 1 000 FCFA / Premium 2 000 FCFA)."""
    return get_plans_catalog()


@router.get("/providers")
async def list_providers():
    """Liste tous les moyens de paiement acceptés (Wave, Orange Money, MTN, Stripe, Crypto)."""
    return {"providers": SUPPORTED_PROVIDERS}


@router.post("/checkout")
async def checkout(req: PaymentIntentRequest):
    """Crée une intention de paiement pour l'Abonnement Simple (1 000 FCFA) ou Premium (2 000 FCFA)."""
    return initiate_subscription_payment(
        customer_phone_or_email=req.customer_phone_or_email,
        provider_id=req.provider_id,
        plan_tier=req.plan_tier,
        currency=req.currency
    )


@router.post("/simulate-webhook/{transaction_id}")
async def simulate_webhook(transaction_id: str, plan_tier: str = "PREMIUM", user_email: Optional[str] = None):
    """Simule la validation automatique par l'opérateur et met à jour le statut du compte."""
    res = confirm_subscription_payment(transaction_id, plan_tier=plan_tier)
    
    # If an email is provided, upgrade user tier in database
    target_email = user_email
    if target_email:
        new_tier = SubscriptionTier.PREMIUM if plan_tier.upper() in ["PREMIUM", "PRO"] else SubscriptionTier.SIMPLE
        db.update_user_tier(target_email, new_tier)
        res["updated_quota"] = db.get_user_quota(target_email)

    return res
