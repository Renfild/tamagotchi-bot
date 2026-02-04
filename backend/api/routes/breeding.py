"""
Breeding API routes.
"""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from models.pet import Pet, PetStatus
from models.breeding import BreedingRequest, BreedingStatus
from api.routes.auth import get_current_user

router = APIRouter()


class CreateBreedingRequest(BaseModel):
    """Create breeding request."""
    pet1_id: int
    pet2_id: int
    recipient_id: int
    message: str = ""


@router.get("/requests")
async def get_breeding_requests(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get user's breeding requests."""
    requests = []
    
    for req in current_user.pets[0].breeding_requests_sent if current_user.pets else []:
        requests.append(req.to_dict())
    
    return requests


@router.post("/request")
async def create_breeding_request(
    request: CreateBreedingRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Create breeding request."""
    # Verify pets
    result = await session.execute(
        select(Pet).where(Pet.id == request.pet1_id, Pet.owner_id == current_user.id)
    )
    pet1 = result.scalar_one_or_none()
    
    if not pet1:
        raise HTTPException(status_code=404, detail="Your pet not found")
    
    result = await session.execute(
        select(Pet).where(Pet.id == request.pet2_id, Pet.owner_id == request.recipient_id)
    )
    pet2 = result.scalar_one_or_none()
    
    if not pet2:
        raise HTTPException(status_code=404, detail="Partner pet not found")
    
    # Check breeding conditions
    if not pet1.can_breed:
        raise HTTPException(status_code=400, detail="Your pet cannot breed")
    
    if not pet2.can_breed:
        raise HTTPException(status_code=400, detail="Partner pet cannot breed")
    
    # Check if user has enough coins
    if not current_user.can_afford(coins=500):
        raise HTTPException(status_code=400, detail="Not enough coins")
    
    # Create request
    breeding_request = BreedingRequest(
        requester_id=current_user.id,
        pet1_id=request.pet1_id,
        recipient_id=request.recipient_id,
        pet2_id=request.pet2_id,
        message=request.message,
        expires_at=datetime.utcnow() + timedelta(days=3),
    )
    
    session.add(breeding_request)
    await session.commit()
    
    return {"success": True, "request": breeding_request.to_dict()}


@router.post("/accept/{request_id}")
async def accept_breeding_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Accept breeding request."""
    result = await session.execute(
        select(BreedingRequest).where(
            BreedingRequest.id == request_id,
            BreedingRequest.recipient_id == current_user.id
        )
    )
    breeding_request = result.scalar_one_or_none()
    
    if not breeding_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if breeding_request.status != BreedingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")
    
    breeding_request.accept()
    breeding_request.start_breeding()
    
    # Deduct coins from requester
    result = await session.execute(
        select(User).where(User.id == breeding_request.requester_id)
    )
    requester = result.scalar_one_or_none()
    
    if requester:
        requester.deduct_currency(coins=500)
    
    await session.commit()
    
    return {"success": True, "request": breeding_request.to_dict()}


@router.post("/complete/{request_id}")
async def complete_breeding(
    request_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Complete breeding and get offspring."""
    result = await session.execute(
        select(BreedingRequest).where(
            BreedingRequest.id == request_id,
            BreedingRequest.requester_id == current_user.id
        )
    )
    breeding_request = result.scalar_one_or_none()
    
    if not breeding_request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if breeding_request.status != BreedingStatus.IN_PROGRESS:
        raise HTTPException(status_code=400, detail="Breeding not in progress")
    
    if not breeding_request.is_ready_to_complete:
        raise HTTPException(status_code=400, detail="Breeding not ready")
    
    # Generate offspring
    offspring_rarity = breeding_request.calculate_offspring_rarity()
    offspring_appearance = breeding_request.generate_offspring_appearance()
    
    # Create offspring pet
    offspring = Pet(
        owner_id=current_user.id,
        name="Детеныш",  # User will rename
        pet_type=breeding_request.pet1.pet_type,
        rarity=offspring_rarity,
        personality=breeding_request.pet1.personality,  # Or mix
        **offspring_appearance,
    )
    
    session.add(offspring)
    await session.flush()
    
    # Complete breeding
    inherited_traits = {
        "parent1_id": breeding_request.pet1_id,
        "parent2_id": breeding_request.pet2_id,
        "rarity": offspring_rarity.value,
        **offspring_appearance,
    }
    
    breeding_request.complete(offspring.id, inherited_traits)
    await session.commit()
    
    return {
        "success": True,
        "offspring": offspring.to_dict(),
    }
