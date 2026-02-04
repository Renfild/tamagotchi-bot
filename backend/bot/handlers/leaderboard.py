"""
Leaderboard command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User

router = Router()


@router.message(Command("leaderboard"))
async def cmd_leaderboard(
    message: Message,
    session: AsyncSession,
    _,
) -> None:
    """Handle /leaderboard command."""
    # Get top 10 users by level of their best pet
    result = await session.execute(
        select(User)
        .order_by(desc(User.battles_won))
        .limit(10)
    )
    top_users = result.scalars().all()
    
    text = "🏆 <b>Топ игроков</b>\n\n"
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for i, user in enumerate(top_users):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        win_rate = user.win_rate if hasattr(user, 'win_rate') else 0
        text += f"{medal} {user.display_name} - {user.battles_won} побед ({win_rate}%)\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👥 Среди друзей", callback_data="leaderboard:friends"),
                InlineKeyboardButton(text="🌍 Глобальный", callback_data="leaderboard:global"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "leaderboard:global")
async def callback_leaderboard(callback: CallbackQuery, session: AsyncSession, _) -> None:
    """Show leaderboard from callback."""
    await callback.answer()
    await cmd_leaderboard(callback.message, session, _)
