from typing import List
from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_current_admin, get_user_service
from app.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserWithAccountsResponse,
)
from app.services.user_service import UserService

router = APIRouter(
    prefix="/admin", 
    tags=["admin"], 
    dependencies=[Depends(get_current_admin)],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"}
    }
)


# Get list of users
@router.get("/users", response_model=List[UserResponse], summary="Get list of all users")
async def get_users(
    user_service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
    """
    Get a list of all users.
    """
    users = await user_service.get_users()
    return users


# Create user
@router.post("/users", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="Create a new user"
)
async def create_user(
    user_data: UserCreate, user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """
    Create a new user.
    """
    user = await user_service.create_user(user_data)
    return user


# Get user by id with accounts
@router.get(
    "/users/{user_id}",
    response_model=UserWithAccountsResponse,
    summary="Get user by id with accounts"
)
async def get_user(
    user_id: int, user_service: UserService = Depends(get_user_service)
) -> UserWithAccountsResponse:
    """
    Get the user with the given id, along with all accounts.
    """
    user = await user_service.get_user_with_details(user_id)
    return user


# Update user
@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Update an existing user with the given user_id.
    """
    # Update the user with the provided data
    user = await user_service.update_user(user_id, user_data)
    return user


# Delete user
@router.delete("/users/{user_id}", summary="Delete a user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, user_service: UserService = Depends(get_user_service)
):
    """
    Delete the user with the given id.
    """
    # Delete the user with the given id
    await user_service.delete_user(user_id)
    return {"message": "User deleted successfully"}
