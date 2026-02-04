"""
Achievements API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from models.achievement import Achievement
from api.routes.auth import get_current_user

router = APIRouter()


@router.get("")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get user's achievements."""
    return [ua.to_dict() for ua in current_user.achievements]


@router.get("/all")
async def get_all_achievements(
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get all achievements."""
    result = await session.execute(select(Achievement).order_by(Achievement.display_order))
    achievements = result.scalars().all()
    
    return [a.to_dict() for a in achievements]


@router.post("/{achievement_id}/claim")
async def claim_achievement_reward(
    achievement_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Claim achievement reward."""
    result = await session.execute(
        select(UserAchievement)
        .where(UserAchievement.user_id == current_user.id)
        .where(UserAchievement.achievement_id == achievement_id)
    )
    user_achievement = result.scalar_one_or_none()
    
    if not user_achievement:
        raise HTTPException(status_code=404, detail="Achievement not found")
    
    rewards = user_achievement.claim_reward()
    
    if not rewards:
        raise HTTPException(status_code=400, detail="Cannot claim reward")
    
    # Apply rewards
    current_user.coins += rewards.get("coins", 0)
    current_user.crystals += rewards.get("crystals", 0)
    
    await session.commit()
    
    return {
        "success": True,
        "rewards": rewards,
    }
