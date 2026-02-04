"""
Games API routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from api.routes.auth import get_current_user

router = APIRouter()


class GameResultRequest(BaseModel):
    """Game result request."""
    game_type: str
    score: int
    pet_id: int


@router.post("/result")
async def submit_game_result(
    request: GameResultRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Submit game result and get rewards."""
    # Calculate rewards based on score
    coins = request.score // 10
    exp = request.score // 5
    
    # Add rewards
    current_user.coins += coins
    
    # Add exp to pet
    from sqlalchemy import select
    from models.pet import Pet
    
    result = await session.execute(
        select(Pet).where(Pet.id == request.pet_id, Pet.owner_id == current_user.id)
    )
    pet = result.scalar_one_or_none()
    
    if pet:
        pet.add_experience(exp)
    
    await session.commit()
    
    return {
        "success": True,
        "coins_earned": coins,
        "exp_earned": exp,
        "new_balance": current_user.coins,
    }


@router.get("/leaderboard/{game_type}")
async def get_game_leaderboard(
    game_type: str,
    limit: int = 10,
) -> list:
    """Get game leaderboard."""
    # Placeholder - implement actual leaderboard
    return []
