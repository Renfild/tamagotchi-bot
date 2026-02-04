"""
Cleanup tasks.
"""
import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.worker import celery_app
from tasks.pet_care import AsyncSessionLocal
from models.friend import Friend, FriendStatus
from models.breeding import BreedingRequest, BreedingStatus
from models.market import MarketListing, MarketStatus
from models.quest import UserQuest


@celery_app.task
def cleanup_expired_data():
    """Clean up expired data."""
    asyncio.run(_cleanup_expired_async())
    return {"status": "completed"}


async def _cleanup_expired_async():
    """Async implementation of cleanup."""
    async with AsyncSessionLocal() as session:
        # Clean up expired friend requests
        await session.execute(
            delete(Friend).where(
                Friend.status == FriendStatus.PENDING,
                Friend.created_at < datetime.utcnow() - timedelta(days=7)
            )
        )
        
        # Clean up expired breeding requests
        result = await session.execute(
            select(BreedingRequest).where(
                BreedingRequest.status == BreedingStatus.PENDING,
                BreedingRequest.expires_at < datetime.utcnow()
            )
        )
        expired_requests = result.scalars().all()
        for req in expired_requests:
            req.status = BreedingStatus.EXPIRED
        
        # Clean up expired market listings
        result = await session.execute(
            select(MarketListing).where(
                MarketListing.status == MarketStatus.ACTIVE,
                MarketListing.expires_at < datetime.utcnow()
            )
        )
        expired_listings = result.scalars().all()
        for listing in expired_listings:
            listing.status = MarketStatus.EXPIRED
        
        # Clean up expired user quests
        await session.execute(
            delete(UserQuest).where(
                UserQuest.is_claimed == False,
                UserQuest.expires_at < datetime.utcnow() - timedelta(days=1)
            )
        )
        
        await session.commit()


@celery_app.task
def archive_old_data():
    """Archive old data."""
    # TODO: Implement data archiving
    return {"status": "completed"}
