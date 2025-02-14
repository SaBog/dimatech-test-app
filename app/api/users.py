from typing import List
from fastapi import APIRouter, Depends
from app.schemas import UserResponse, AccountResponse, PaymentResponse
from app.services.user_service import UserService
from app.core.dependencies import get_current_user, get_user_service
from app.db import models

router = APIRouter(
    prefix="/users", 
    tags=["user"],
    responses={
        401: {"description": "Unauthorized"},
    }
)


# Get current user data
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    return current_user


# Get list of accounts for the current user
@router.get("/accounts", response_model=List[AccountResponse])
async def get_user_accounts(
    current_user: models.User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):

    return await user_service.get_user_accounts(current_user.id)


# Get list of payments for the current user
@router.get("/payments", response_model=List[PaymentResponse])
async def get_user_payments(
    current_user: models.User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):

    return await user_service.get_user_payments(current_user.id)
