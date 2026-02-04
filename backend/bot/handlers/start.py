"""
Start command handler and onboarding.
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models.user import User, Language
from bot.keyboards.main import get_main_menu_keyboard, get_language_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    session: AsyncSession,
    _,
    state: FSMContext,
) -> None:
    """Handle /start command."""
    user_id = message.from_user.id
    
    # Check if user exists
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        # New user - show language selection
        await message.answer(
            "🌍 Выберите язык / Choose language:\n\n"
            "🇷🇺 Русский\n"
            "🇬🇧 English",
            reply_markup=get_language_keyboard(),
        )
    else:
        # Existing user - show main menu
        await show_main_menu(message, user, _)


@router.callback_query(F.data.startswith("lang:"))
async def process_language_selection(
    callback: CallbackQuery,
    session: AsyncSession,
    _,
) -> None:
    """Process language selection."""
    await callback.answer()
    
    language_code = callback.data.split(":")[1]
    language = Language(language_code)
    
    # Create or update user
    user_id = callback.from_user.id
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        # Create new user
        user = User(
            id=user_id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name,
            last_name=callback.from_user.last_name,
            language_code=callback.from_user.language_code,
            language=language,
        )
        session.add(user)
        await session.commit()
        
        # Show welcome message
        welcome_text = _(
            "welcome",
            first_name=user.first_name,
        )
        
        await callback.message.edit_text(
            f"{welcome_text}\n\n"
            f"🎮 <b>Создайте своего первого питомца!</b>\n\n"
            f"Нажмите кнопку ниже, чтобы открыть Mini App и создать уникального питомца.",
            reply_markup=get_first_pet_keyboard(),
            parse_mode="HTML",
        )
    else:
        # Update language
        user.language = language
        await session.commit()
        
        await callback.message.edit_text(
            _("language_updated"),
            reply_markup=get_main_menu_keyboard(user),
        )


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ],
        ]
    )


def get_first_pet_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for creating first pet."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Создать питомца",
                    web_app=WebAppInfo(url=f"{settings.WEBAPP_URL}/create")
                ),
            ],
            [
                InlineKeyboardButton(text="📖 Гид", callback_data="help:tutorial"),
            ],
        ]
    )


async def show_main_menu(
    message: Message,
    user: User,
    _,
) -> None:
    """Show main menu to user."""
    # Get active pet info
    active_pet = None
    if user.pets:
        active_pets = [p for p in user.pets if p.status.value != "deceased"]
        if active_pets:
            active_pet = active_pets[0]
    
    if active_pet:
        # Show pet status summary
        status_emoji = {
            "active": "😊",
            "sleeping": "😴",
            "sick": "🤒",
            "depressed": "😢",
        }.get(active_pet.status.value, "😐")
        
        text = (
            f"{status_emoji} <b>{active_pet.name}</b> (Lv. {active_pet.level})\n\n"
            f"🍖 {_('hunger')}: {active_pet.hunger}/100\n"
            f"😊 {_('happiness')}: {active_pet.happiness}/100\n"
            f"❤️ {_('health')}: {active_pet.health}/100\n"
            f"⚡ {_('energy')}: {active_pet.energy}/100\n\n"
            f"🪙 {user.coins} | 💎 {user.crystals}"
        )
        
        # Check for warnings
        warnings = []
        if active_pet.hunger < 30:
            warnings.append("⚠️ Питомец голоден!")
        if active_pet.health < 50:
            warnings.append("⚠️ Питомец болен!")
        if active_pet.happiness < 30:
            warnings.append("⚠️ Питомец грустит!")
        
        if warnings:
            text += "\n\n" + "\n".join(warnings)
    else:
        text = (
            "🐾 <b>Добро пожаловать!</b>\n\n"
            "У вас пока нет питомца. Создайте его в Mini App!"
        )
    
    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard(user),
        parse_mode="HTML",
    )


@router.message(Command("menu"))
async def cmd_menu(
    message: Message,
    session: AsyncSession,
    _,
) -> None:
    """Show main menu."""
    user_id = message.from_user.id
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user:
        await show_main_menu(message, user, _)
    else:
        await cmd_start(message, session, _, None)
