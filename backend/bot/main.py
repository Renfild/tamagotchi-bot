"""
Main entry point for the Telegram Bot.
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from core.config import settings
from bot.handlers import (
    start,
    pet,
    inventory,
    shop,
    games,
    friends,
    breeding,
    arena,
    quests,
    achievements,
    leaderboard,
    settings as settings_handler,
    help as help_handler,
)
from bot.middlewares.i18n import I18nMiddleware
from bot.middlewares.database import DatabaseMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main bot entry point."""
    logger.info("Starting Tamagotchi Bot...")
    
    # Initialize bot
    bot = Bot(
        token=settings.BOT_TOKEN,
        parse_mode=ParseMode.HTML,
    )
    
    # Initialize storage
    storage = RedisStorage.from_url(settings.REDIS_URL)
    
    # Initialize dispatcher
    dp = Dispatcher(storage=storage)
    
    # Register middlewares
    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())
    
    # Register routers
    dp.include_router(start.router)
    dp.include_router(pet.router)
    dp.include_router(inventory.router)
    dp.include_router(shop.router)
    dp.include_router(games.router)
    dp.include_router(friends.router)
    dp.include_router(breeding.router)
    dp.include_router(arena.router)
    dp.include_router(quests.router)
    dp.include_router(achievements.router)
    dp.include_router(leaderboard.router)
    dp.include_router(settings_handler.router)
    dp.include_router(help_handler.router)
    
    # Set up menu button
    await setup_menu_button(bot)
    
    # Start polling
    logger.info("Bot started successfully!")
    await dp.start_polling(bot)


async def setup_menu_button(bot: Bot) -> None:
    """Set up the menu button for the bot."""
    from aiogram.types import MenuButtonWebApp, WebAppInfo
    
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🎮 Открыть игру",
            web_app=WebAppInfo(url=settings.WEBAPP_URL)
        )
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
    except Exception as e:
        logger.exception("Bot crashed: %s", e)
        sys.exit(1)
