"""
Notification tasks.
"""
import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.worker import celery_app
from tasks.pet_care import AsyncSessionLocal
from models.pet import Pet, PetStatus
from models.user import User


@celery_app.task
def check_and_send_notifications():
    """Check pets and send notifications to owners."""
    asyncio.run(_check_notifications_async())
    return {"status": "completed"}


async def _check_notifications_async():
    """Async implementation of notification check."""
    async with AsyncSessionLocal() as session:
        # Get all active pets with low stats
        result = await session.execute(
            select(Pet, User)
            .join(User, Pet.owner_id == User.id)
            .where(Pet.status.notin_([PetStatus.DECEASED, PetStatus.RUNAWAY]))
        )
        rows = result.all()
        
        notifications = []
        
        for pet, user in rows:
            # Skip if user has notifications disabled
            if user.notifications.value == "none":
                continue
            
            # Skip if in quiet hours
            current_hour = datetime.utcnow().hour
            if user.is_quiet_hours(current_hour):
                continue
            
            # Check for low stats
            if pet.hunger < 30 and not hasattr(pet, '_hunger_notified'):
                notifications.append({
                    "user_id": user.id,
                    "message": f"🍖 {pet.name} голоден! Сытость: {pet.hunger}%",
                })
            
            if pet.happiness < 30 and not hasattr(pet, '_happiness_notified'):
                notifications.append({
                    "user_id": user.id,
                    "message": f"😢 {pet.name} грустит! Настроение: {pet.happiness}%",
                })
            
            if pet.energy < 20 and not hasattr(pet, '_energy_notified'):
                notifications.append({
                    "user_id": user.id,
                    "message": f"⚡ {pet.name} устал! Энергия: {pet.energy}%",
                })
        
        # Send notifications
        for notif in notifications:
            # TODO: Implement bot notification sending
            pass


@celery_app.task
def send_daily_reminder():
    """Send daily reminder to active users."""
    asyncio.run(_send_reminders_async())
    return {"status": "completed"}


async def _send_reminders_async():
    """Async implementation of reminders."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            # Check if user has pets
            if user.pets:
                active_pets = [p for p in user.pets if p.status != PetStatus.DECEASED]
                if active_pets:
                    # TODO: Send reminder
                    pass
