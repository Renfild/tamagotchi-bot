"""
Quests API routes.
"""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from models.quest import Quest, UserQuest, QuestFrequency
from api.routes.auth import get_current_user

router = APIRouter()


@router.get("")
async def get_quests(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get user's quests."""
    return [uq.to_dict() for uq in current_user.quests]


@router.get("/available")
async def get_available_quests(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get available quests."""
    result = await session.execute(
        select(Quest).where(Quest.is_active == True)
    )
    quests = result.scalars().all()
    
    return [q.to_dict() for q in quests if q.is_available]


@router.post("/{quest_id}/accept")
async def accept_quest(
    quest_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Accept a quest."""
    result = await session.execute(select(Quest).where(Quest.id == quest_id))
    quest = result.scalar_one_or_none()
    
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Check if already accepted
    result = await session.execute(
        select(UserQuest)
        .where(UserQuest.user_id == current_user.id)
        .where(UserQuest.quest_id == quest_id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Quest already accepted")
    
    # Calculate expiration
    if quest.frequency == QuestFrequency.DAILY:
        expires = datetime.utcnow() + timedelta(days=1)
    elif quest.frequency == QuestFrequency.WEEKLY:
        expires = datetime.utcnow() + timedelta(weeks=1)
    else:
        expires = datetime.utcnow() + timedelta(days=30)
    
    user_quest = UserQuest(
        user_id=current_user.id,
        quest_id=quest_id,
        expires_at=expires,
    )
    session.add(user_quest)
    await session.commit()
    
    return {"success": True, "quest": user_quest.to_dict()}


@router.post("/{quest_id}/claim")
async def claim_quest_reward(
    quest_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Claim quest reward."""
    result = await session.execute(
        select(UserQuest)
        .where(UserQuest.user_id == current_user.id)
        .where(UserQuest.quest_id == quest_id)
    )
    user_quest = result.scalar_one_or_none()
    
    if not user_quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    rewards = user_quest.claim()
    
    if not rewards:
        raise HTTPException(status_code=400, detail="Cannot claim reward")
    
    # Apply rewards
    current_user.coins += rewards.get("coins", 0)
    current_user.crystals += rewards.get("crystals", 0)
    current_user.quests_completed += 1
    
    await session.commit()
    
    return {
        "success": True,
        "rewards": rewards,
    }
