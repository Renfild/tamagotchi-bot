"""
Settings command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from bot.keyboards.main import get_settings_keyboard, get_main_menu_keyboard

router = Router()


@router.message(Command("settings"))
async def cmd_settings(
    message: Message,
    session: AsyncSession,
    _,
) -> None:
    """Handle /settings command."""
    user_id = message.from_user.id
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        await message.answer("Сначала запустите бота: /start")
        return
    
    text = (
        f"⚙️ <b>Настройки</b>\n\n"
        f"<b>Профиль:</b>\n"
        f"Имя: {user.first_name}\n"
        f"ID: {user.id}\n"
        f"Дата регистрации: {user.created_at.strftime('%d.%m.%Y') if user.created_at else 'N/A'}\n\n"
        f"<b>Статистика:</b>\n"
        f"Питомцев создано: {user.pets_created}\n"
        f"Побед в боях: {user.battles_won}\n"
        f"Квестов выполнено: {user.quests_completed}\n"
        f"Время в игре: {user.total_playtime_minutes // 60}ч"
    )
    
    await message.answer(text, reply_markup=get_settings_keyboard(user), parse_mode="HTML")


@router.callback_query(F.data == "settings:menu")
async def callback_settings(callback: CallbackQuery, session: AsyncSession, _) -> None:
    """Show settings from callback."""
    await callback.answer()
    await cmd_settings(callback.message, session, _)


@router.callback_query(F.data == "settings:language")
async def callback_language(callback: CallbackQuery, session: AsyncSession, _) -> None:
    """Show language selection."""
    await callback.answer()
    
    from bot.keyboards.main import get_language_keyboard
    await callback.message.edit_text(
        "🌍 Выберите язык:",
        reply_markup=get_language_keyboard(),
    )
