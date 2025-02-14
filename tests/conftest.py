import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from fastapi.testclient import TestClient
from app.core.dependencies import get_db
from app.db.models import Base
from app.main import app
from app.db.init_data import init_data

# Use an in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create a new async engine for testing
engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the dependency to use the test DB
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    """Create tables, initialize test data, and clean up after tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        await init_data(session)  # Ensure this is awaited

    yield  # Run the test

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Cleanup after test


@pytest_asyncio.fixture
async def client():
    """Return a FastAPI test client."""
    # Apply the override
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
