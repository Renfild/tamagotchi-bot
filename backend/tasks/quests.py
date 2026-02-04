"""
Quest-related tasks.
"""
import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tasks.worker import celery_app
from tasks.pet_care import AsyncSessionLocal
from models.quest import Quest, UserQuest, QuestFrequency
from models.user import User


@celery_app.task
def reset_daily_quests():
    """Reset daily quests for all users."""
    asyncio.run(_reset_daily_quests_async())
    return {"status": "completed"}


async def _reset_daily_quests_async():
    """Async implementation of daily quest reset."""
    async with AsyncSessionLocal() as session:
        # Get all daily quests
        result = await session.execute(
            select(Quest).where(Quest.frequency == QuestFrequency.DAILY)
        )
        daily_quests = result.scalars().all()
        
        # Get all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            # Remove expired daily quests
            for uq in user.quests:
                if uq.quest and uq.quest.frequency == QuestFrequency.DAILY:
                    await session.delete(uq)
            
            # Assign new daily quests
            for quest in daily_quests:
                # Check if quest is available for user level
                if user.pets and any(p.level >= quest.min_level_required for p in user.pets):
                    user_quest = UserQuest(
                        user_id=user.id,
                        quest_id=quest.id,
                        expires_at=datetime.utcnow() + timedelta(days=1),
                    )
                    session.add(user_quest)
        
        await session.commit()


@celery_app.task
def reset_weekly_quests():
    """Reset weekly quests for all users."""
    asyncio.run(_reset_weekly_quests_async())
    return {"status": "completed"}


async def _reset_weekly_quests_async():
    """Async implementation of weekly quest reset."""
    async with AsyncSessionLocal() as session:
        # Get all weekly quests
        result = await session.execute(
            select(Quest).where(Quest.frequency == QuestFrequency.WEEKLY)
        )
        weekly_quests = result.scalars().all()
        
        # Get all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            # Remove expired weekly quests
            for uq in user.quests:
                if uq.quest and uq.quest.frequency == QuestFrequency.WEEKLY:
                    await session.delete(uq)
            
            # Assign new weekly quests
            for quest in weekly_quests:
                if user.pets and any(p.level >= quest.min_level_required for p in user.pets):
                    user_quest = UserQuest(
                        user_id=user.id,
                        quest_id=quest.id,
                        expires_at=datetime.utcnow() + timedelta(weeks=1),
                    )
                    session.add(user_quest)
        
        await session.commit()
