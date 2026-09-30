"""
QuantBet Engine - Mobile Money & Card Payment Endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.modules.billing.payment_gateway import SUPPORTED_PROVIDERS, initiate_subscription_payment, confirm_subscription_payment

router = APIRouter(prefix="/payments", tags=["Paiements Abonnements (Mobile Money & Stripe)"])


class PaymentIntentRequest(BaseModel):
    customer_phone_or_email: str = Field(..., description="Numéro de téléphone ou email")
    provider_id: str = Field("wave", description="Fournisseur: wave, orange_money, mtn_momo, stripe, crypto_usdt")
    currency: str = Field("FCFA", description="Devise: FCFA ou EUR")


@router.get("/providers")
async def list_providers():
    """Liste tous les moyens de paiement acceptés (Wave, Orange Money, MTN, Moov, Stripe, Crypto)."""
    return {"providers": SUPPORTED_PROVIDERS}


@router.post("/checkout")
async def checkout(req: PaymentIntentRequest):
    """Crée une intention de paiement d'abonnement."""
    return initiate_subscription_payment(
        customer_phone_or_email=req.customer_phone_or_email,
        provider_id=req.provider_id,
        currency=req.currency
    )


@router.post("/simulate-webhook/{transaction_id}")
async def simulate_webhook(transaction_id: str):
    """Simule la validation automatique par l'opérateur et l'activation de l'accès VIP."""
    return confirm_subscription_payment(transaction_id)
