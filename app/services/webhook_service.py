import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select
from app.core.config import settings
from app.db.models import Account, Payment
from app.schemas import PaymentWebhook
import logging


class WebhookService:
    def __init__(self, db: AsyncSession):
        self.secret_key = settings.SECRET_KEY
        self.db = db

    # Process payment webhook

    async def process_payment_webhook(self, webhook_data: PaymentWebhook):
        if not self.verify_signature(webhook_data):
            raise HTTPException(status_code=400, detail="Invalid signature")

        logging.info(f"Processing webhook: {webhook_data}")

        # Check if account exists, else create it
        stmt = select(Account).filter(Account.id == webhook_data.account_id).limit(1)
        result = await self.db.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            logging.warning(
                f"Account {webhook_data.account_id} not found. Creating new account."
            )
            account = Account(
                id=webhook_data.account_id,
                user_id=webhook_data.user_id,
                balance=webhook_data.amount,
            )
            self.db.add(account)
        else:
            account.balance += webhook_data.amount
            logging.info(f"Updated balance: {account.balance}")

        # Check if transaction exists
        stmt = (
            select(Payment)
            .filter(Payment.transaction_id == webhook_data.transaction_id)
            .limit(1)
        )
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Transaction already processed")

        # Save payment
        payment = Payment(
            transaction_id=webhook_data.transaction_id,
            user_id=webhook_data.user_id,
            account_id=webhook_data.account_id,
            amount=webhook_data.amount,
        )

        self.db.add(payment)
        await self.db.commit()

        logging.info(f"Payment {webhook_data.transaction_id} committed successfully.")
        return {"message": "Payment processed successfully"}

    def verify_signature(self, webhook_data: PaymentWebhook) -> bool:
        """
        Проверяет корректность подписи webhook-уведомления.
        """
        secret_key = settings.SECRET_KEY  # Получаем секретный ключ из конфигурации

        # Формируем строку для подписи (ключи идут в алфавитном порядке)
        sign_data = f"{webhook_data.account_id}{webhook_data.amount}{webhook_data.transaction_id}{webhook_data.user_id}{secret_key}"

        # Вычисляем SHA256 хеш
        calculated_signature = hashlib.sha256(sign_data.encode("utf-8")).hexdigest()

        # Сравниваем подписи
        return calculated_signature == webhook_data.signature
