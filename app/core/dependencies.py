from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.core.session import get_db
from app.db import models
from app.core.config import settings
from app.schemas import TokenData
from app.services.user_service import UserService
from app.services.webhook_service import WebhookService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


def get_webhook_service(db: AsyncSession = Depends(get_db)) -> WebhookService:
    return WebhookService(db)


# Decode JWT and get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except Exception:
        raise credentials_exception

    user = await db.get(models.User, token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


# Check if user is admin
async def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user
