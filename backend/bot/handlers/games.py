"""
Games command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.main import get_games_keyboard, get_main_menu_keyboard

router = Router()


@router.message(Command("games"))
async def cmd_games(message: Message, _) -> None:
    """Handle /games command."""
    text = (
        "🎯 <b>Мини-игры</b>\n\n"
        "<b>Аркады:</b>\n"
        "🏃 Бег за едой - собирайте монетки\n"
        "🧩 Пазл - соберите картинку питомца\n"
        "🎵 Ритм-игра - нажимайте в такт\n"
        "🎣 Рыбалка - ловите рыбу\n"
        "🎯 Лабиринт - найдите выход\n\n"
        "<b>PvP:</b>\n"
        "⚔️ Дуэль - сразитесь с другом\n"
        "🏁 Гонки - кто быстрее"
    )
    
    await message.answer(text, reply_markup=get_games_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "games:list")
async def callback_games(callback: CallbackQuery, _) -> None:
    """Show games from callback."""
    await callback.answer()
    await cmd_games(callback.message, _)
