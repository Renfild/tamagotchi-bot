"""
Pets API routes.
"""
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from models.pet import Pet, PetType, Rarity, Personality, PetStatus
from api.routes.auth import get_current_user

router = APIRouter()


class PetCreateRequest(BaseModel):
    """Pet creation request."""
    name: str = Field(..., min_length=1, max_length=32)
    pet_type: PetType
    rarity: Rarity = Rarity.COMMON
    personality: Personality = Personality.PLAYFUL
    primary_color: str = "#FF6B6B"
    secondary_color: str = "#4ECDC4"
    eye_color: str = "#000000"
    pattern: str = "solid"
    custom_description: Optional[str] = None


class PetUpdateRequest(BaseModel):
    """Pet update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=32)
    is_favorite: Optional[bool] = None


class PetResponse(BaseModel):
    """Pet response."""
    id: int
    name: str
    pet_type: str
    rarity: str
    personality: str
    level: int
    experience: int
    exp_to_next_level: int
    exp_progress_percent: float
    evolution_stage: str
    stats: dict
    battle_stats: dict
    status: str
    is_favorite: bool
    appearance: dict
    images: dict
    age_days: int
    can_battle: bool
    can_breed: bool
    is_alive: bool


@router.get("", response_model=List[PetResponse])
async def get_pets(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[Pet]:
    """Get user's pets."""
    return current_user.pets


@router.get("/active", response_model=Optional[PetResponse])
async def get_active_pet(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Optional[Pet]:
    """Get user's active pet."""
    active_pets = [p for p in current_user.pets if p.status != PetStatus.DECEASED]
    return active_pets[0] if active_pets else None


@router.post("", response_model=PetResponse)
async def create_pet(
    request: PetCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Pet:
    """Create a new pet."""
    # Check max pets limit
    if len(current_user.pets) >= 10:  # MAX_PETS_PER_USER
        raise HTTPException(status_code=400, detail="Maximum pets limit reached")
    
    # Create pet
    pet = Pet(
        owner_id=current_user.id,
        name=request.name,
        pet_type=request.pet_type,
        rarity=request.rarity,
        personality=request.personality,
        primary_color=request.primary_color,
        secondary_color=request.secondary_color,
        eye_color=request.eye_color,
        pattern=request.pattern,
        custom_description=request.custom_description,
    )
    
    # Set stats based on rarity
    rarity_multipliers = {
        Rarity.COMMON: 1.0,
        Rarity.UNCOMMON: 1.1,
        Rarity.RARE: 1.2,
        Rarity.EPIC: 1.3,
        Rarity.LEGENDARY: 1.5,
        Rarity.MYTHIC: 2.0,
    }
    multiplier = rarity_multipliers.get(request.rarity, 1.0)
    
    pet.attack = int(10 * multiplier)
    pet.defense = int(10 * multiplier)
    pet.speed = int(10 * multiplier)
    pet.max_hp = int(100 * multiplier)
    
    session.add(pet)
    
    # Update user stats
    current_user.pets_created += 1
    
    await session.commit()
    await session.refresh(pet)
    
    return pet


@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Pet:
    """Get pet by ID."""
    result = await session.execute(
        select(Pet).where(Pet.id == pet_id, Pet.owner_id == current_user.id)
    )
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    return pet


@router.patch("/{pet_id}", response_model=PetResponse)
async def update_pet(
    pet_id: int,
    request: PetUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Pet:
    """Update pet."""
    result = await session.execute(
        select(Pet).where(Pet.id == pet_id, Pet.owner_id == current_user.id)
    )
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    if request.name is not None:
        pet.name = request.name
    if request.is_favorite is not None:
        pet.is_favorite = request.is_favorite
    
    await session.commit()
    await session.refresh(pet)
    
    return pet


@router.post("/{pet_id}/feed")
async def feed_pet(
    pet_id: int,
    food_value: int = 25,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Feed pet."""
    result = await session.execute(
        select(Pet).where(Pet.id == pet_id, Pet.owner_id == current_user.id)
    )
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    old_hunger = pet.hunger
    pet.feed(food_value)
    leveled_up = pet.add_experience(5)
    
    await session.commit()
    
    return {
        "success": True,
        "hunger_before": old_hunger,
        "hunger_after": pet.hunger,
        "leveled_up": leveled_up,
        "new_level": pet.level if leveled_up else None,
    }


@router.post("/{pet_id}/pet")
async def pet_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Pet the pet."""
    result = await session.execute(
        select(Pet).where(Pet.id == pet_id, Pet.owner_id == current_user.id)
    )
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    old_happiness = pet.happiness
    pet.pet()
    
    await session.commit()
    
    return {
        "success": True,
        "happiness_before": old_happiness,
        "happiness_after": pet.happiness,
    }


@router.post("/{pet_id}/play")
async def play_with_pet(
    pet_id: int,
    fun_value: int = 20,
    energy_cost: int = 15,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Play with pet."""
    result = await session.execute(
        select(Pet).where(Pet.id == pet_id, Pet.owner_id == current_user.id)
    )
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    if pet.energy < energy_cost:
        raise HTTPException(status_code=400, detail="Not enough energy")
    
    old_happiness = pet.happiness
    old_energy = pet.energy
    
    success = pet.play(fun_value, energy_cost)
    if not success:
        raise HTTPException(status_code=400, detail="Not enough energy")
    
    leveled_up = pet.add_experience(10)
    
    await session.commit()
    
    return {
        "success": True,
        "happiness_before": old_happiness,
        "happiness_after": pet.happiness,
        "energy_before": old_energy,
        "energy_after": pet.energy,
        "leveled_up": leveled_up,
        "new_level": pet.level if leveled_up else None,
    }


@router.post("/{pet_id}/sleep")
async def sleep_pet(
    pet_id: int,
    hours: int = 4,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Put pet to sleep."""
    result = await session.execute(
        select(Pet).where(Pet.id == pet_id, Pet.owner_id == current_user.id)
    )
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    if pet.status == PetStatus.SLEEPING:
        raise HTTPException(status_code=400, detail="Pet is already sleeping")
    
    pet.sleep(hours)
    
    await session.commit()
    
    return {
        "success": True,
        "sleep_until": pet.sleep_until.isoformat() if pet.sleep_until else None,
    }


@router.post("/{pet_id}/wake")
async def wake_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Wake up pet."""
    result = await session.execute(
        select(Pet).where(Pet.id == pet_id, Pet.owner_id == current_user.id)
    )
    pet = result.scalar_one_or_none()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    
    if pet.status != PetStatus.SLEEPING:
        raise HTTPException(status_code=400, detail="Pet is not sleeping")
    
    pet.wake_up()
    
    await session.commit()
    
    return {
        "success": True,
        "energy": pet.energy,
    }
