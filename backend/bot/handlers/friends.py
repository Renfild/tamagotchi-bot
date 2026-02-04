"""
Friends command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.friend import Friend, FriendStatus
from bot.keyboards.main import get_friends_keyboard, get_main_menu_keyboard

router = Router()


@router.message(Command("friends"))
async def cmd_friends(
    message: Message,
    session: AsyncSession,
    _,
) -> None:
    """Handle /friends command."""
    user_id = message.from_user.id
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("Сначала запустите бота: /start")
        return
    
    # Count friends
    friends_count = len([f for f in user.friends_sent if f.status == FriendStatus.ACCEPTED])
    friends_count += len([f for f in user.friends_received if f.status == FriendStatus.ACCEPTED])
    
    pending_count = len([f for f in user.friends_received if f.status == FriendStatus.PENDING])
    
    text = (
        f"👥 <b>Друзья</b>\n\n"
        f"У вас {friends_count} друзей\n"
        f"{pending_count} новых заявок\n\n"
        f"Добавляйте друзей, чтобы:\n"
        f"• Видеть их питомцев\n"
        f"• Помогать с уходом\n"
        f"• Обмениваться подарками\n"
        f"• Разводить питомцев"
    )
    
    await message.answer(text, reply_markup=get_friends_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "friends:list")
async def callback_friends(callback: CallbackQuery, session: AsyncSession, _) -> None:
    """Show friends from callback."""
    await callback.answer()
    await cmd_friends(callback.message, session, _)
