"""
Help command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.main import get_main_menu_keyboard

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message, _) -> None:
    """Handle /help command."""
    text = (
        "❓ <b>Помощь</b>\n\n"
        "<b>Основные команды:</b>\n"
        "/start - Начать работу с ботом\n"
        "/pet - Статус питомца\n"
        "/inventory - Ваш инвентарь\n"
        "/shop - Магазин\n"
        "/games - Мини-игры\n"
        "/friends - Друзья\n"
        "/arena - PvP арена\n"
        "/quests - Квесты\n"
        "/achievements - Достижения\n"
        "/leaderboard - Рейтинг\n"
        "/settings - Настройки\n"
        "/help - Эта помощь\n\n"
        "<b>Как играть:</b>\n"
        "1. Создайте питомца в Mini App\n"
        "2. Ухаживайте за ним: кормите, играйте, лечите\n"
        "3. Выполняйте квесты для наград\n"
        "4. Сражайтесь на арене\n"
        "5. Добавляйте друзей и разводите питомцев\n\n"
        "<b>Поддержка:</b> @support"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Подробный гид", callback_data="help:guide"),
                InlineKeyboardButton(text="🎥 Видеоуроки", callback_data="help:videos"),
            ],
            [
                InlineKeyboardButton(text="💬 Поддержка", url="https://t.me/support"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "help:menu")
async def callback_help(callback: CallbackQuery, _) -> None:
    """Show help from callback."""
    await callback.answer()
    await cmd_help(callback.message, _)


@router.callback_query(F.data == "menu:main")
async def callback_main_menu(callback: CallbackQuery, session, _) -> None:
    """Return to main menu."""
    await callback.answer()
    
    from bot.handlers.start import show_main_menu
    await show_main_menu(callback.message, session, _, edit=True)
