from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Payment, Account


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_payments_by_user_id(self, user_id: int) -> list[Payment]:
        result = await self.db.execute(
            select(Payment).where(Payment.user_id == user_id)
        )
        return result.scalars().all()

    async def create_payment(
        self, transaction_id: str, account_id: int, user_id: int, amount: float
    ) -> Payment:
        payment = Payment(
            transaction_id=transaction_id,
            account_id=account_id,
            user_id=user_id,
            amount=amount,
        )
        self.db.add(payment)
        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    async def update_account_balance(self, account_id: int, amount: float) -> Account:
        account = await self.db.execute(select(Account).where(Account.id == account_id))
        account = account.scalars().first()
        if account:
            account.balance += amount
            await self.db.commit()
            await self.db.refresh(account)
        return account
