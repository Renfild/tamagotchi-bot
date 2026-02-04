"""
Internationalization middleware.
"""
from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, Language


class I18nMiddleware(BaseMiddleware):
    """Middleware to handle user language preferences."""
    
    # Translations dictionary
    TRANSLATIONS = {
        Language.RUSSIAN: {
            "welcome": "Добро пожаловать в Tamagotchi Bot! 🐾",
            "pet_status": "📊 Статус питомца",
            "hunger": "🍖 Сытость",
            "happiness": "😊 Настроение",
            "health": "❤️ Здоровье",
            "energy": "⚡ Энергия",
            "level": "📈 Уровень",
            "coins": "🪙 Монеты",
            "crystals": "💎 Кристаллы",
            "feed": "🍎 Покормить",
            "play": "🎮 Играть",
            "pet_action": "🤗 Погладить",
            "sleep": "😴 Уложить спать",
            "inventory": "🎒 Инвентарь",
            "shop": "🛒 Магазин",
            "games": "🎯 Мини-игры",
            "friends": "👥 Друзья",
            "arena": "⚔️ Арена",
            "quests": "📜 Квесты",
            "achievements": "🏆 Достижения",
            "settings": "⚙️ Настройки",
            "help": "❓ Помощь",
            "no_pet": "У вас еще нет питомца! Создайте его в Mini App.",
            "pet_hungry": "Ваш питомец голоден! Покормите его.",
            "pet_sick": "Ваш питомец заболел! Используйте лекарство.",
            "pet_happy": "Ваш питомец счастлив! 🎉",
            "level_up": "🎉 Поздравляем! {pet_name} достиг уровня {level}!",
        },
        Language.ENGLISH: {
            "welcome": "Welcome to Tamagotchi Bot! 🐾",
            "pet_status": "📊 Pet Status",
            "hunger": "🍖 Hunger",
            "happiness": "😊 Happiness",
            "health": "❤️ Health",
            "energy": "⚡ Energy",
            "level": "📈 Level",
            "coins": "🪙 Coins",
            "crystals": "💎 Crystals",
            "feed": "🍎 Feed",
            "play": "🎮 Play",
            "pet_action": "🤗 Pet",
            "sleep": "😴 Sleep",
            "inventory": "🎒 Inventory",
            "shop": "🛒 Shop",
            "games": "🎯 Mini-games",
            "friends": "👥 Friends",
            "arena": "⚔️ Arena",
            "quests": "📜 Quests",
            "achievements": "🏆 Achievements",
            "settings": "⚙️ Settings",
            "help": "❓ Help",
            "no_pet": "You don't have a pet yet! Create one in the Mini App.",
            "pet_hungry": "Your pet is hungry! Feed them.",
            "pet_sick": "Your pet is sick! Use medicine.",
            "pet_happy": "Your pet is happy! 🎉",
            "level_up": "🎉 Congratulations! {pet_name} reached level {level}!",
        },
    }
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Inject i18n function."""
        # Get user ID
        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        # Get user language from database
        language = Language.RUSSIAN  # Default
        if user_id and "session" in data:
            session: AsyncSession = data["session"]
            result = await session.execute(
                select(User.language).where(User.id == user_id)
            )
            user_lang = result.scalar_one_or_none()
            if user_lang:
                language = user_lang
        
        # Create translation function
        def _(key: str, **kwargs) -> str:
            """Get translated string."""
            translations = self.TRANSLATIONS.get(language, self.TRANSLATIONS[Language.RUSSIAN])
            text = translations.get(key, key)
            if kwargs:
                text = text.format(**kwargs)
            return text
        
        data["_"] = _
        data["language"] = language
        
        return await handler(event, data)
