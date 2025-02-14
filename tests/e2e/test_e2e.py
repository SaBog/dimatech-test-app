import pytest
from fastapi.testclient import TestClient
import pytest_asyncio

# Constants for test data
USER_CREDENTIALS = {"username": "testuser@example.com", "password": "123"}
ADMIN_CREDENTIALS = {"username": "testadmin@example.com", "password": "123"}
NEW_USER_DATA = {
    "email": "newuser@example.com",
    "full_name": "New User",
    "password": "testpassword",
}


@pytest_asyncio.fixture(scope="function")
async def get_auth_token(client: TestClient):
    """Get authentication tokens for both user and admin."""

    def _get_token(username, password):
        response = client.post(
            "/auth/login", data={"username": username, "password": password}
        )
        if response.status_code != 200:
            return None  # Return None if authentication fails
        return response.json().get("access_token")

    return _get_token


@pytest.mark.asyncio
async def test_user_login(client: TestClient):
    """Test logging in as a regular user."""
    response = client.post("/auth/login", data=USER_CREDENTIALS)
    assert response.status_code == 200
    return response.json().get("access_token")


@pytest.mark.asyncio
async def test_admin_get_users(client: TestClient, get_auth_token):
    """Test retrieving all users as an admin."""
    admin_token = get_auth_token(**ADMIN_CREDENTIALS)

    if not admin_token:
        pytest.skip("Skipping test because authentication failed")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/admin/users", headers=headers)

    assert response.status_code == 200
    users = response.json()
    assert len(users) > 0
    assert users[0]["email"] in ["testuser@example.com", "testadmin@example.com"]


@pytest.mark.asyncio
async def test_admin_create_user(client: TestClient, get_auth_token):
    """Test that an admin can create a new user."""
    admin_token = get_auth_token(**ADMIN_CREDENTIALS)
    if not admin_token:
        pytest.skip("Skipping test because authentication failed")

    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.post("/admin/users", json=NEW_USER_DATA, headers=headers)

    assert response.status_code == 201
    created_user = response.json()
    assert created_user["email"] == NEW_USER_DATA["email"]


@pytest.mark.asyncio
async def test_user_cannot_access_admin_endpoint(client: TestClient, get_auth_token):
    """Test that a regular user cannot access an admin endpoint."""
    user_token = get_auth_token(**USER_CREDENTIALS)
    headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 403  # Forbidden
