"""
Quests command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.quest import QuestFrequency
from bot.keyboards.main import get_main_menu_keyboard

router = Router()


@router.message(Command("quests"))
async def cmd_quests(
    message: Message,
    session: AsyncSession,
    _,
) -> None:
    """Handle /quests command."""
    user_id = message.from_user.id
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("Сначала запустите бота: /start")
        return
    
    # Count quests
    daily_completed = sum(1 for q in user.quests 
                         if q.quest and q.quest.frequency == QuestFrequency.DAILY and q.is_completed)
    daily_total = sum(1 for q in user.quests 
                     if q.quest and q.quest.frequency == QuestFrequency.DAILY)
    
    text = (
        f"📜 <b>Квесты</b>\n\n"
        f"<b>Ежедневные:</b> {daily_completed}/{daily_total} выполнено\n\n"
        f"Выполняйте квесты, чтобы получать:\n"
        f"• 🪙 Монеты\n"
        f"• 💎 Кристаллы\n"
        f"• 🎁 Редкие предметы\n\n"
        f"Квесты обновляются каждый день!"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 Текущие", callback_data="quests:current"),
                InlineKeyboardButton(text="✅ Выполненные", callback_data="quests:completed"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "quests:list")
async def callback_quests(callback: CallbackQuery, session: AsyncSession, _) -> None:
    """Show quests from callback."""
    await callback.answer()
    await cmd_quests(callback.message, session, _)
