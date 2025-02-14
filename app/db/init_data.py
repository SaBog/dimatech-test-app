import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.security import get_password_hash
from app.core.session import get_db
from app.db.models import User, Account

# Assuming User and Account are already imported from app.db.models


async def init_data(session: AsyncSession):
    # Check if test data already exists
    result = await session.execute(select(User))
    users = result.scalars().all()

    if users:
        print("Data already initialized.")
        return

    try:
        test_user_password = "123"
        test_admin_password = "123"

        # Create test user
        test_user = User(
            email="testuser@example.com",
            full_name="Test User",
            is_admin=False,
            password_hash=get_password_hash(test_user_password),
        )

        # Create test admin
        test_admin = User(
            email="testadmin@example.com",
            full_name="Test Admin",
            is_admin=True,
            password_hash=get_password_hash(test_admin_password),
        )

        # Add test user and test admin to the session
        session.add_all([test_user, test_admin])
        await session.commit()  # Commit to ensure IDs are assigned

        # Refresh to ensure IDs are populated
        await session.refresh(test_user)
        await session.refresh(test_admin)

        # Now, their IDs should be available
        test_user_account = Account(user_id=test_user.id, balance=100.0)
        test_admin_account = Account(user_id=test_admin.id, balance=500.0)

        # Add accounts to the session
        session.add_all([test_user_account, test_admin_account])
        await session.commit()

        print("Test data initialized.")
    except Exception as e:
        print(f"Error initializing data: {e}")
        raise


async def main():
    async for session in get_db():
        await init_data(session)


if __name__ == "__main__":
    asyncio.run(main())
