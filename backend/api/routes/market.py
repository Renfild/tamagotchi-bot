"""
Market API routes.
"""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.user import User
from models.market import MarketListing, MarketTransaction, MarketStatus
from models.inventory import InventoryItem
from api.routes.auth import get_current_user

router = APIRouter()


class CreateListingRequest(BaseModel):
    """Create market listing request."""
    item_id: int
    quantity: int
    price_coins: int
    price_crystals: int = 0


class BuyListingRequest(BaseModel):
    """Buy listing request."""
    listing_id: int


@router.get("/listings")
async def get_listings(
    item_id: int = None,
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get active market listings."""
    query = select(MarketListing).where(MarketListing.status == MarketStatus.ACTIVE)
    
    if item_id:
        query = query.where(MarketListing.item_id == item_id)
    
    result = await session.execute(query)
    listings = result.scalars().all()
    
    return [l.to_dict() for l in listings if not l.is_expired]


@router.post("/listings")
async def create_listing(
    request: CreateListingRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Create a market listing."""
    # Check inventory
    result = await session.execute(
        select(InventoryItem)
        .where(InventoryItem.owner_id == current_user.id)
        .where(InventoryItem.item_id == request.item_id)
    )
    inv_item = result.scalar_one_or_none()
    
    if not inv_item or inv_item.quantity < request.quantity:
        raise HTTPException(status_code=400, detail="Not enough items")
    
    # Deduct items from inventory
    inv_item.quantity -= request.quantity
    
    # Create listing
    listing = MarketListing(
        seller_id=current_user.id,
        item_id=request.item_id,
        quantity=request.quantity,
        price_coins=request.price_coins,
        price_crystals=request.price_crystals,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    
    session.add(listing)
    await session.commit()
    
    return {"success": True, "listing": listing.to_dict()}


@router.post("/buy")
async def buy_listing(
    request: BuyListingRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """Buy a market listing."""
    result = await session.execute(
        select(MarketListing).where(MarketListing.id == request.listing_id)
    )
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing.status != MarketStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Listing not active")
    
    if listing.is_expired:
        raise HTTPException(status_code=400, detail="Listing expired")
    
    if listing.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot buy your own listing")
    
    # Check if buyer can afford
    total_coins = listing.total_price_coins
    total_crystals = listing.price_crystals * listing.quantity
    
    if not current_user.can_afford(total_coins, total_crystals):
        raise HTTPException(status_code=400, detail="Not enough currency")
    
    # Deduct from buyer
    current_user.deduct_currency(total_coins, total_crystals)
    
    # Add to seller
    result = await session.execute(
        select(User).where(User.id == listing.seller_id)
    )
    seller = result.scalar_one_or_none()
    
    if seller:
        fee = total_coins * 5 // 100  # 5% fee
        seller.coins += total_coins - fee
    
    # Add item to buyer's inventory
    result = await session.execute(
        select(InventoryItem)
        .where(InventoryItem.owner_id == current_user.id)
        .where(InventoryItem.item_id == listing.item_id)
    )
    buyer_inv = result.scalar_one_or_none()
    
    if buyer_inv:
        buyer_inv.quantity += listing.quantity
    else:
        buyer_inv = InventoryItem(
            owner_id=current_user.id,
            item_id=listing.item_id,
            quantity=listing.quantity,
            obtained_from="market",
        )
        session.add(buyer_inv)
    
    # Mark listing as sold
    listing.mark_sold(current_user.id)
    
    # Create transaction record
    transaction = MarketTransaction.from_listing(listing, current_user.id)
    session.add(transaction)
    
    await session.commit()
    
    return {
        "success": True,
        "item_name": listing.item.name if listing.item else None,
        "quantity": listing.quantity,
        "spent_coins": total_coins,
        "spent_crystals": total_crystals,
    }


@router.get("/my-listings")
async def get_my_listings(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[dict]:
    """Get user's market listings."""
    result = await session.execute(
        select(MarketListing).where(MarketListing.seller_id == current_user.id)
    )
    listings = result.scalars().all()
    
    return [l.to_dict() for l in listings]
