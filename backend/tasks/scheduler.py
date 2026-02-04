"""
Celery beat scheduler configuration.
"""
from celery import Celery
from celery.signals import beat_init

from tasks.worker import celery_app


@beat_init.connect
def on_beat_init(sender, **kwargs):
    """Called when beat starts."""
    print("Celery beat scheduler started")


# The scheduler is configured in worker.py via beat_schedule
# This file exists for any additional scheduler configuration
