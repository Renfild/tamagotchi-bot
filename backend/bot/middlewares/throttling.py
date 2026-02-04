"""
Throttling middleware to prevent spam.
"""
from typing import Callable, Awaitable, Dict, Any
from datetime import datetime, timedelta

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware to throttle user requests."""
    
    def __init__(
        self,
        message_rate: int = 1,  # messages per second
        callback_rate: int = 3,  # callbacks per second
    ):
        self.message_cache = TTLCache(maxsize=10000, ttl=1)
        self.callback_cache = TTLCache(maxsize=10000, ttl=1)
        self.message_rate = message_rate
        self.callback_rate = callback_rate
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """Check rate limit."""
        user_id = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id
            cache = self.message_cache
            rate = self.message_rate
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            cache = self.callback_cache
            rate = self.callback_rate
        else:
            return await handler(event, data)
        
        if user_id is None:
            return await handler(event, data)
        
        # Check cache
        current_count = cache.get(user_id, 0)
        
        if current_count >= rate:
            # Rate limit exceeded
            if isinstance(event, Message):
                await event.answer("⚠️ Слишком быстро! Подождите немного.")
            return None
        
        # Update cache
        cache[user_id] = current_count + 1
        
        return await handler(event, data)
