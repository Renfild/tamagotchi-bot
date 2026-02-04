"""
Arena command handler for PvP battles.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.keyboards.main import get_main_menu_keyboard

router = Router()


@router.message(Command("arena"))
async def cmd_arena(message: Message, _) -> None:
    """Handle /arena command."""
    text = (
        "⚔️ <b>Арена</b>\n\n"
        "<b>Режимы:</b>\n"
        "🥊 Дружеский спарринг\n"
        "🏆 Рейтинговые бои\n"
        "🎲 Ставочные бои\n\n"
        "<b>Ваш рейтинг:</b> Бронза III\n"
        "<b>Побед:</b> 0 | <b>Поражений:</b> 0\n\n"
        "Выберите режим боя в Mini App!"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚔️ Найти противника",
                    callback_data="arena:find"
                ),
            ],
            [
                InlineKeyboardButton(text="📊 Рейтинг", callback_data="arena:leaderboard"),
                InlineKeyboardButton(text="📜 История", callback_data="arena:history"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "arena:menu")
async def callback_arena(callback: CallbackQuery, _) -> None:
    """Show arena from callback."""
    await callback.answer()
    await cmd_arena(callback.message, _)
