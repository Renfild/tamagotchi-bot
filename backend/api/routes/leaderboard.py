"""
Leaderboard API routes.
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User

router = APIRouter()


@router.get("/battles")
async def get_battle_leaderboard(
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get battle wins leaderboard."""
    result = await session.execute(
        select(User)
        .order_by(desc(User.battles_won))
        .limit(limit)
    )
    users = result.scalars().all()
    
    return [
        {
            "id": u.id,
            "username": u.username,
            "first_name": u.first_name,
            "battles_won": u.battles_won,
            "battles_lost": u.battles_lost,
            "win_rate": u.win_rate,
        }
        for u in users
    ]


@router.get("/quests")
async def get_quest_leaderboard(
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get quests completed leaderboard."""
    result = await session.execute(
        select(User)
        .order_by(desc(User.quests_completed))
        .limit(limit)
    )
    users = result.scalars().all()
    
    return [
        {
            "id": u.id,
            "username": u.username,
            "first_name": u.first_name,
            "quests_completed": u.quests_completed,
        }
        for u in users
    ]


@router.get("/richest")
async def get_richest_leaderboard(
    limit: int = 10,
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get richest users leaderboard."""
    result = await session.execute(
        select(User)
        .order_by(desc(User.coins))
        .limit(limit)
    )
    users = result.scalars().all()
    
    return [
        {
            "id": u.id,
            "username": u.username,
            "first_name": u.first_name,
            "coins": u.coins,
            "crystals": u.crystals,
        }
        for u in users
    ]
