"""
Achievements command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from bot.keyboards.main import get_main_menu_keyboard

router = Router()


@router.message(Command("achievements"))
async def cmd_achievements(
    message: Message,
    session: AsyncSession,
    _,
) -> None:
    """Handle /achievements command."""
    user_id = message.from_user.id
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("Сначала запустите бота: /start")
        return
    
    earned_count = len(user.achievements)
    
    text = (
        f"🏆 <b>Достижения</b>\n\n"
        f"Получено: {earned_count} достижений\n\n"
        f"Собирайте достижения, выполняя различные действия:\n"
        f"• Заботьтесь о питомце\n"
        f"• Выигрывайте бои\n"
        f"• Коллекционируйте питомцев\n"
        f"• Дружите с другими игроками\n\n"
        f"Каждое достижение дает награды!"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏅 Мои достижения", callback_data="achievements:mine"),
                InlineKeyboardButton(text="📊 Все достижения", callback_data="achievements:all"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "achievements:list")
async def callback_achievements(callback: CallbackQuery, session: AsyncSession, _) -> None:
    """Show achievements from callback."""
    await callback.answer()
    await cmd_achievements(callback.message, session, _)
