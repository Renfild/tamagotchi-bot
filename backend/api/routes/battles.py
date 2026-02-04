"""
Battles API routes.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from models.battle import Battle, BattleMove, BattleStatus, BattleType, BattleMoveType
from models.pet import Pet
from api.routes.auth import get_current_user

router = APIRouter()


class CreateBattleRequest(BaseModel):
    """Create battle request."""
    opponent_id: int
    pet_id: int
    battle_type: BattleType = BattleType.FRIENDLY
    bet_amount: int = 0


class BattleMoveRequest(BaseModel):
    """Battle move request."""
    move_type: BattleMoveType


@router.get("")
async def get_battles(
    status: BattleStatus = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get user's battles."""
    battles = []
    
    for battle in current_user.battles_as_player1:
        if not status or battle.status == status:
            battles.append(battle.to_dict())
    
    for battle in current_user.battles_as_player2:
        if not status or battle.status == status:
            battles.append(battle.to_dict())
    
    return battles


@router.post("")
async def create_battle(
    request: CreateBattleRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Create a new battle."""
    # Get opponent's active pet
    result = await session.execute(
        select(Pet).where(Pet.owner_id == request.opponent_id, Pet.status != "deceased")
    )
    opponent_pets = result.scalars().all()
    
    if not opponent_pets:
        raise HTTPException(status_code=400, detail="Opponent has no active pets")
    
    opponent_pet = opponent_pets[0]
    
    # Verify user's pet
    result = await session.execute(
        select(Pet).where(Pet.id == request.pet_id, Pet.owner_id == current_user.id)
    )
    user_pet = result.scalar_one_or_none()
    
    if not user_pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    # Create battle
    battle = Battle(
        battle_type=request.battle_type,
        player1_id=current_user.id,
        pet1_id=request.pet_id,
        player2_id=request.opponent_id,
        pet2_id=opponent_pet.id,
        bet_amount=request.bet_amount,
    )
    
    session.add(battle)
    await session.commit()
    
    return battle.to_dict()


@router.get("/{battle_id}")
async def get_battle(
    battle_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Get battle by ID."""
    result = await session.execute(select(Battle).where(Battle.id == battle_id))
    battle = result.scalar_one_or_none()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    if current_user.id not in [battle.player1_id, battle.player2_id]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return battle.to_dict()


@router.post("/{battle_id}/move")
async def make_move(
    battle_id: int,
    request: BattleMoveRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Make a battle move."""
    result = await session.execute(select(Battle).where(Battle.id == battle_id))
    battle = result.scalar_one_or_none()
    
    if not battle:
        raise HTTPException(status_code=404, detail="Battle not found")
    
    if battle.status != BattleStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Battle is not active")
    
    # Determine player number
    is_player1 = current_user.id == battle.player1_id
    is_player2 = current_user.id == battle.player2_id
    
    if not is_player1 and not is_player2:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    player_number = 1 if is_player1 else 2
    
    if battle.current_turn != player_number:
        raise HTTPException(status_code=400, detail="Not your turn")
    
    # Get pets
    pet1 = battle.pet1
    pet2 = battle.pet2
    
    # Calculate damage
    attacker = pet1 if is_player1 else pet2
    defender = pet2 if is_player1 else pet1
    
    damage_result = battle.calculate_damage(
        attacker, defender, request.move_type, is_player1
    )
    
    # Apply damage
    if is_player1:
        battle.pet2_current_hp -= damage_result["damage"]
        battle.pet2_current_hp = max(0, battle.pet2_current_hp)
        if damage_result["heal"]:
            battle.pet1_current_hp = min(pet1.max_hp, battle.pet1_current_hp + damage_result["heal"])
        if damage_result["buffs"]:
            battle.pet1_buffs.update(damage_result["buffs"])
    else:
        battle.pet1_current_hp -= damage_result["damage"]
        battle.pet1_current_hp = max(0, battle.pet1_current_hp)
        if damage_result["heal"]:
            battle.pet2_current_hp = min(pet2.max_hp, battle.pet2_current_hp + damage_result["heal"])
        if damage_result["buffs"]:
            battle.pet2_buffs.update(damage_result["buffs"])
    
    # Record move
    move = BattleMove(
        battle_id=battle.id,
        turn_number=battle.turn_number,
        player_number=player_number,
        move_type=request.move_type,
        damage_dealt=damage_result["damage"],
        healing_done=damage_result["heal"],
        is_critical=damage_result["is_critical"],
        is_miss=damage_result["is_miss"],
        pet1_hp_after=battle.pet1_current_hp,
        pet2_hp_after=battle.pet2_current_hp,
    )
    session.add(move)
    
    # Add to battle log
    battle.add_log_entry({
        "player": player_number,
        "move": request.move_type.value,
        "damage": damage_result["damage"],
        "heal": damage_result["heal"],
        "critical": damage_result["is_critical"],
        "miss": damage_result["is_miss"],
    })
    
    # Check for winner
    if battle.pet1_current_hp <= 0:
        battle.finish(battle.player2_id)
    elif battle.pet2_current_hp <= 0:
        battle.finish(battle.player1_id)
    else:
        battle.switch_turn()
    
    await session.commit()
    
    return {
        "move_result": damage_result,
        "battle": battle.to_dict(),
    }
