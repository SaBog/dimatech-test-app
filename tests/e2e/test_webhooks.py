import pytest
from fastapi import status, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import select
from app.core.session import get_db
from app.db.models import Payment
from app.services.webhook_service import WebhookService

# Constants for test data
SECRET_KEY = "gfdmhghif38yrf9ew0jkf32"
VALID_WEBHOOK_DATA = {
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
}
INVALID_SIGNATURE_WEBHOOK_DATA = {
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
    "account_id": 1,
    "amount": 100,
    "signature": "invalid_signature",
}
MISSING_FIELD_WEBHOOK_DATA = {
    "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
    "user_id": 1,
    "amount": 100,
    "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8",
}


@pytest.mark.asyncio
async def test_process_payment_webhook_valid(client: TestClient):
    """Test processing a valid payment webhook."""
    response = client.post("/webhooks/payment", json=VALID_WEBHOOK_DATA)

    print("Response:", response.json())  # Debugging

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Payment processed successfully"}

    # Fetch the transaction from DB correctly
    async for db in client.app.dependency_overrides[get_db]():
        stmt = select(Payment).filter(
            Payment.transaction_id == VALID_WEBHOOK_DATA["transaction_id"]
        )
        result = await db.execute(stmt)
        transaction = result.scalar_one_or_none()

        print(f"Transaction fetched from DB: {transaction}")  # Debugging

        assert transaction is not None  # This should now pass
        assert transaction.amount == VALID_WEBHOOK_DATA["amount"]
        break  # Exit after first iteration


@pytest.mark.asyncio
async def test_process_payment_webhook_invalid_signature(client: TestClient):
    """Test processing a payment webhook with an invalid signature."""
    # Make the request
    response = client.post("/webhooks/payment", json=INVALID_SIGNATURE_WEBHOOK_DATA)

    # Assert the response
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid signature" in response.json().get("detail", "")


@pytest.mark.asyncio
async def test_process_payment_webhook_missing_field(client: TestClient):
    """Test processing a payment webhook with a missing required field."""
    # Make the request
    response = client.post("/webhooks/payment", json=MISSING_FIELD_WEBHOOK_DATA)

    # Assert the response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Field required" in response.json().get("detail", "")[0].get("msg", "")


@pytest.mark.asyncio
async def test_process_payment_webhook_database_error(client: TestClient, monkeypatch):
    """Test processing a payment webhook when a database error occurs."""

    # Mock the WebhookService to raise an HTTPException for database error
    async def mock_process_payment_webhook(*args, **kwargs):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error"
        )

    # Apply the mock
    monkeypatch.setattr(
        WebhookService, "process_payment_webhook", mock_process_payment_webhook
    )

    # Make the request
    response = client.post("/webhooks/payment", json=VALID_WEBHOOK_DATA)

    # Assert the response
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Database error" in response.json().get("detail", "")
