from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import get_webhook_service
from app.services.webhook_service import WebhookService
from app.schemas import PaymentWebhook  # Import the Pydantic model

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


# Process payment webhook
@router.post(
    "/payment",
    responses={400: {"description": "Bad Request"}},
)
async def process_payment_webhook(
    webhook_data: PaymentWebhook,
    webhook_service: WebhookService = Depends(get_webhook_service),
):
    try:
        # Verify the signature using WebhookService
        response = await webhook_service.process_payment_webhook(webhook_data)
        return response
    except HTTPException as e:
        raise e
