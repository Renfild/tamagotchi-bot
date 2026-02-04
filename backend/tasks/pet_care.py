"""
Pet care background tasks.
"""
import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from tasks.worker import celery_app
from core.config import settings
from core.database import Base
from models.pet import Pet, PetStatus
from models.user import User

# Create async engine for tasks
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@celery_app.task(bind=True)
def apply_pet_decay(self):
    """Apply stat decay to all active pets."""
    asyncio.run(_apply_pet_decay_async())
    return {"status": "completed", "processed": "pets"}


async def _apply_pet_decay_async():
    """Async implementation of pet decay."""
    async with AsyncSessionLocal() as session:
        # Get all active pets
        result = await session.execute(
            select(Pet).where(Pet.status.notin_([PetStatus.DECEASED, PetStatus.RUNAWAY]))
        )
        pets = result.scalars().all()
        
        notifications_to_send = []
        
        for pet in pets:
            # Apply decay (1 hour)
            changes = pet.apply_decay(hours=1)
            
            # Check for critical conditions
            if "critical_hunger" in changes:
                notifications_to_send.append({
                    "user_id": pet.owner_id,
                    "message": f"🍖 {pet.name} очень голоден! Покормите его срочно!",
                })
            
            if "sick" in changes:
                notifications_to_send.append({
                    "user_id": pet.owner_id,
                    "message": f"🤒 {pet.name} заболел! Нужно лечение!",
                })
            
            if "depressed" in changes:
                notifications_to_send.append({
                    "user_id": pet.owner_id,
                    "message": f"😢 {pet.name} впал в депрессию! Поиграйте с ним!",
                })
            
            if "runaway" in changes:
                notifications_to_send.append({
                    "user_id": pet.owner_id,
                    "message": f"🏃 {pet.name} сбежал из-за отсутствия ухода...",
                })
        
        await session.commit()
        
        # Send notifications (implement with bot API)
        for notif in notifications_to_send:
            # TODO: Send notification via bot
            pass


@celery_app.task
def wake_up_pets():
    """Wake up pets whose sleep time has ended."""
    asyncio.run(_wake_up_pets_async())
    return {"status": "completed"}


async def _wake_up_pets_async():
    """Async implementation of wake up."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Pet).where(
                Pet.status == PetStatus.SLEEPING,
                Pet.sleep_until <= datetime.utcnow()
            )
        )
        pets = result.scalars().all()
        
        for pet in pets:
            pet.wake_up()
        
        await session.commit()


@celery_app.task
def heal_pets_over_time():
    """Gradually heal pets that are not sick."""
    asyncio.run(_heal_pets_async())
    return {"status": "completed"}


async def _heal_pets_async():
    """Async implementation of healing."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Pet).where(
                Pet.status == PetStatus.ACTIVE,
                Pet.health < 100
            )
        )
        pets = result.scalars().all()
        
        for pet in pets:
            pet.health = min(100, pet.health + 5)
        
        await session.commit()
