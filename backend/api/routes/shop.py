"""
Shop API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from models.item import Item, ItemType
from models.inventory import InventoryItem
from api.routes.auth import get_current_user

router = APIRouter()


class BuyItemRequest(BaseModel):
    """Buy item request."""
    item_id: int
    quantity: int = 1


@router.get("/items")
async def get_shop_items(
    item_type: ItemType = None,
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get shop items."""
    query = select(Item).where(Item.is_purchasable == True)
    
    if item_type:
        query = query.where(Item.item_type == item_type)
    
    result = await session.execute(query)
    items = result.scalars().all()
    
    return [item.to_dict() for item in items]


@router.post("/buy")
async def buy_item(
    request: BuyItemRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Buy an item."""
    result = await session.execute(select(Item).where(Item.id == request.item_id))
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if not item.is_purchasable:
        raise HTTPException(status_code=400, detail="Item not available for purchase")
    
    # Calculate price
    total_coins = (item.buy_price_coins or 0) * request.quantity
    total_crystals = (item.buy_price_crystals or 0) * request.quantity
    
    # Check if user can afford
    if not current_user.can_afford(total_coins, total_crystals):
        raise HTTPException(status_code=400, detail="Not enough currency")
    
    # Deduct currency
    current_user.deduct_currency(total_coins, total_crystals)
    
    # Add to inventory
    result = await session.execute(
        select(InventoryItem)
        .where(InventoryItem.owner_id == current_user.id)
        .where(InventoryItem.item_id == item.id)
    )
    inv_item = result.scalar_one_or_none()
    
    if inv_item:
        inv_item.quantity += request.quantity
    else:
        inv_item = InventoryItem(
            owner_id=current_user.id,
            item_id=item.id,
            quantity=request.quantity,
            obtained_from="shop",
        )
        session.add(inv_item)
    
    await session.commit()
    
    return {
        "success": True,
        "item_name": item.name,
        "quantity": request.quantity,
        "spent_coins": total_coins,
        "spent_crystals": total_crystals,
    }
