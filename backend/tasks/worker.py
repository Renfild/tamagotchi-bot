"""
Celery worker configuration.
"""
from celery import Celery
from core.config import settings

# Create Celery app
celery_app = Celery(
    "tamagotchi",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.pet_care",
        "tasks.notifications",
        "tasks.quests",
        "tasks.cleanup",
    ],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    worker_prefetch_multiplier=1,
)

# Beat schedule
celery_app.conf.beat_schedule = {
    "apply-pet-decay": {
        "task": "tasks.pet_care.apply_pet_decay",
        "schedule": 3600.0,  # Every hour
    },
    "check-notifications": {
        "task": "tasks.notifications.check_and_send_notifications",
        "schedule": 300.0,  # Every 5 minutes
    },
    "reset-daily-quests": {
        "task": "tasks.quests.reset_daily_quests",
        "schedule": "crontab(hour=0, minute=0)",  # Midnight
    },
    "cleanup-expired": {
        "task": "tasks.cleanup.cleanup_expired_data",
        "schedule": 86400.0,  # Daily
    },
}
