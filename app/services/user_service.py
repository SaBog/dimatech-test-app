from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models import User, Account, Payment
from app.schemas import UserCreate, UserUpdate
from app.core.security import get_password_hash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Add this method to get a user by email
    async def get_user_by_email(self, email: str) -> User:
        stmt = select(User).filter(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()  # Returns the user or None if not found

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    # Method to get payments associated with a specific user
    async def get_user_payments(self, user_id: int):
        # Query to select all payments where user_id matches the provided user_id
        stmt = select(Payment).filter(Payment.user_id == user_id)
        result = await self.db.execute(stmt)

        # Fetch all the payment records associated with the user
        payments = result.scalars().all()

        # Return an empty list if no payments are found
        return payments

    # Method to get accounts associated with a specific user
    async def get_user_accounts(self, user_id: int):
        # Query to select all accounts where user_id matches the provided user_id
        stmt = select(Account).filter(Account.user_id == user_id)
        result = await self.db.execute(stmt)

        # Fetch all the account records associated with the user
        accounts = result.scalars().all()

        # Return an empty list if no accounts are found
        return accounts

    # Create user
    async def create_user(self, user_data: UserCreate) -> User:
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            is_admin=user_data.is_admin,
            password_hash=get_password_hash(user_data.password),
        )
        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        except IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e):
                raise HTTPException(status_code=400, detail="Email already exists")
            else:
                raise e
        return user

    # Update user
    async def update_user(self, user_id: int, user_data: UserUpdate):
        stmt = select(User).filter(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user_data.password:
            user.password_hash = get_password_hash(user_data.password)
        user.full_name = user_data.full_name or user.full_name
        user.is_admin = user_data.is_admin

        await self.db.commit()
        await self.db.refresh(user)
        return user

    # Delete user
    async def delete_user(self, user_id: int):
        stmt = select(User).filter(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await self.db.delete(user)
        await self.db.commit()
        return {"message": "User deleted successfully"}

    # Get users list
    async def get_users(self):
        query = select(User)
        result = await self.db.execute(query)
        return result.scalars().all()

    # Get a user by id with their accounts and payments
    async def get_user_with_details(self, user_id: int):
        query = (
            select(User).options(selectinload(User.accounts)).filter(User.id == user_id)
        )

        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user
