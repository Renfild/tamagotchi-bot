"""
Breeding command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.pet import Pet
from bot.keyboards.main import get_main_menu_keyboard

router = Router()


@router.message(Command("breeding"))
async def cmd_breeding(
    message: Message,
    session: AsyncSession,
    _,
) -> None:
    """Handle /breeding command."""
    user_id = message.from_user.id
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.pets:
        await message.answer(
            "У вас нет питомцев для разведения!",
            reply_markup=get_main_menu_keyboard(user) if user else None,
        )
        return
    
    # Count breedable pets
    breedable_pets = [p for p in user.pets if p.level >= 10]
    
    text = (
        f"🐾 <b>Разведение питомцев</b>\n\n"
        f"Питомцев для разведения: {len(breedable_pets)}\n\n"
        f"<b>Условия:</b>\n"
        f"• Оба питомца должны быть 10+ уровня\n"
        f"• Питомцы должны быть здоровы\n"
        f"• Кулдаун 7 дней после разведения\n\n"
        f"<b>Стоимость:</b> 500 🪜\n\n"
        f"Детеныш наследует черты обоих родителей!"
    )
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 Найти партнера", callback_data="breeding:find"),
            ],
            [
                InlineKeyboardButton(text="📨 Мои заявки", callback_data="breeding:requests"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )
    
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "friends:breeding")
async def callback_breeding(callback: CallbackQuery, session: AsyncSession, _) -> None:
    """Show breeding from callback."""
    await callback.answer()
    await cmd_breeding(callback.message, session, _)
