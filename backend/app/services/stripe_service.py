import stripe
from typing import Optional
from app.config import settings


class StripeService:
    """Service for Stripe payment processing"""
    
    def __init__(self):
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def create_payment_intent(self, amount: float, currency: str = "bgn", 
                            customer_email: Optional[str] = None,
                            metadata: Optional[dict] = None) -> dict:
        """
        Create a Stripe payment intent
        amount: amount in smallest currency unit (stotinki for BGN)
        """
        try:
            # Convert to smallest currency unit (stotinki)
            amount_in_stotinki = int(amount * 100)
            
            intent = stripe.PaymentIntent.create(
                amount=amount_in_stotinki,
                currency=currency,
                receipt_email=customer_email,
                metadata=metadata or {}
            )
            
            return {
                "success": True,
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def confirm_payment(self, payment_intent_id: str) -> dict:
        """Confirm a payment intent"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "success": True,
                "status": intent.status,
                "amount": intent.amount / 100  # Convert back to leva
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def refund_payment(self, payment_intent_id: str, amount: Optional[float] = None) -> dict:
        """Refund a payment"""
        try:
            refund_params = {"payment_intent": payment_intent_id}
            if amount:
                refund_params["amount"] = int(amount * 100)
            
            refund = stripe.Refund.create(**refund_params)
            
            return {
                "success": True,
                "refund_id": refund.id,
                "status": refund.status
            }
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e)
            }


def get_stripe_service() -> StripeService:
    """Dependency to get Stripe service instance"""
    return StripeService()
