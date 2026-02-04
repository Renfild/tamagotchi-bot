"""
Authentication routes.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from core.config import settings
from core.database import get_db
from models.user import User

router = APIRouter()


class TelegramAuthData(BaseModel):
    """Telegram WebApp auth data."""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    auth_date: int
    hash: str


class AuthResponse(BaseModel):
    """Auth response."""
    token: str
    user: dict


def verify_telegram_auth(data: TelegramAuthData) -> bool:
    """Verify Telegram WebApp authentication."""
    # In production, implement proper Telegram hash verification
    # For now, accept all
    return True


def create_access_token(user_id: int) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


async def get_current_user(
    authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Get current user from JWT token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid auth scheme")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.post("/telegram", response_model=AuthResponse)
async def auth_telegram(
    auth_data: TelegramAuthData,
    session: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Authenticate via Telegram WebApp."""
    # Verify Telegram auth
    if not verify_telegram_auth(auth_data):
        raise HTTPException(status_code=401, detail="Invalid auth data")
    
    # Get or create user
    result = await session.execute(select(User).where(User.id == auth_data.id))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user
        user = User(
            id=auth_data.id,
            first_name=auth_data.first_name,
            last_name=auth_data.last_name,
            username=auth_data.username,
            language_code=auth_data.language_code,
        )
        session.add(user)
        await session.commit()
    else:
        # Update user info
        user.first_name = auth_data.first_name
        user.last_name = auth_data.last_name
        user.username = auth_data.username
        user.last_activity_at = datetime.utcnow()
        await session.commit()
    
    # Create token
    token = create_access_token(user.id)
    
    return AuthResponse(
        token=token,
        user={
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "coins": user.coins,
            "crystals": user.crystals,
            "is_premium": user.is_premium,
        },
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)) -> dict:
    """Get current user info."""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "coins": current_user.coins,
        "crystals": current_user.crystals,
        "arena_tokens": current_user.arena_tokens,
        "is_premium": current_user.is_premium,
        "language": current_user.language.value,
        "notifications": current_user.notifications.value,
        "privacy": current_user.privacy.value,
        "stats": {
            "battles_won": current_user.battles_won,
            "battles_lost": current_user.battles_lost,
            "quests_completed": current_user.quests_completed,
            "pets_created": current_user.pets_created,
            "total_playtime": current_user.total_playtime_minutes,
        },
    }
