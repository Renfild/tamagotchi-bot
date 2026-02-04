"""
Inventory API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from models.inventory import InventoryItem
from models.item import Item
from api.routes.auth import get_current_user

router = APIRouter()


class UseItemRequest(BaseModel):
    """Use item request."""
    item_id: int
    quantity: int = 1
    pet_id: int = None


@router.get("")
async def get_inventory(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get user's inventory."""
    return [item.to_dict() for item in current_user.inventory_items if item.quantity > 0]


@router.post("/use")
async def use_item(
    request: UseItemRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Use an item."""
    result = await session.execute(
        select(InventoryItem)
        .where(InventoryItem.owner_id == current_user.id)
        .where(InventoryItem.item_id == request.item_id)
    )
    inv_item = result.scalar_one_or_none()
    
    if not inv_item or inv_item.quantity < request.quantity:
        raise HTTPException(status_code=400, detail="Not enough items")
    
    # Apply item effects
    success = inv_item.use(request.quantity)
    
    if not success:
        raise HTTPException(status_code=400, detail="Cannot use item")
    
    await session.commit()
    
    return {
        "success": True,
        "item_name": inv_item.item_definition.name if inv_item.item_definition else None,
        "remaining": inv_item.quantity,
    }


@router.post("/equip/{inventory_item_id}")
async def equip_item(
    inventory_item_id: int,
    pet_id: int = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Equip an item."""
    result = await session.execute(
        select(InventoryItem)
        .where(InventoryItem.id == inventory_item_id)
        .where(InventoryItem.owner_id == current_user.id)
    )
    inv_item = result.scalar_one_or_none()
    
    if not inv_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    success = inv_item.equip(pet_id)
    
    await session.commit()
    
    return {"success": success}
