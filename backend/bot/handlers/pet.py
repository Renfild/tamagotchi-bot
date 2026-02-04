"""
Pet command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.pet import Pet, PetStatus
from bot.keyboards.main import get_pet_action_keyboard, get_main_menu_keyboard
from bot.utils.pet_renderer import render_pet_status

router = Router()


@router.message(Command("pet"))
async def cmd_pet(
    message: Message,
    session: AsyncSession,
    _,
) -> None:
    """Handle /pet command."""
    await show_pet_status(message, session, _)


@router.callback_query(F.data == "pet:status")
async def callback_pet_status(
    callback: CallbackQuery,
    session: AsyncSession,
    _,
) -> None:
    """Show pet status from callback."""
    await callback.answer()
    await show_pet_status(callback.message, session, _, edit=True)


async def show_pet_status(
    message: Message,
    session: AsyncSession,
    _,
    edit: bool = False,
) -> None:
    """Show pet status to user."""
    user_id = message.chat.id
    
    # Get user with pets
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.pets:
        text = _("no_pet")
        keyboard = get_main_menu_keyboard(user) if user else None
        
        if edit:
            await message.edit_text(text, reply_markup=keyboard)
        else:
            await message.answer(text, reply_markup=keyboard)
        return
    
    # Get active pet
    active_pets = [p for p in user.pets if p.status != PetStatus.DECEASED]
    if not active_pets:
        text = _("no_pet")
        if edit:
            await message.edit_text(text, reply_markup=get_main_menu_keyboard(user))
        else:
            await message.answer(text, reply_markup=get_main_menu_keyboard(user))
        return
    
    pet = active_pets[0]
    
    # Render pet status
    text = await render_pet_status(pet, _)
    keyboard = get_pet_action_keyboard(pet.id)
    
    if edit:
        await message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("pet:feed:"))
async def callback_feed_pet(
    callback: CallbackQuery,
    session: AsyncSession,
    _,
) -> None:
    """Feed pet."""
    await callback.answer()
    
    pet_id = int(callback.data.split(":")[2])
    
    result = await session.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    
    if not pet:
        await callback.message.edit_text("Питомец не найден!")
        return
    
    # Check if pet can be fed
    if pet.hunger >= 100:
        await callback.answer("Питомец уже сыт!", show_alert=True)
        return
    
    # Feed pet
    old_hunger = pet.hunger
    pet.feed(food_value=25)
    
    # Check for level up
    leveled_up = pet.add_experience(5)
    
    await session.commit()
    
    # Show result
    text = f"🍖 Вы покормили {pet.name}!\n\n"
    text += f"Сытость: {old_hunger} → {pet.hunger}\n"
    
    if leveled_up:
        text += f"\n🎉 {pet.name} получил уровень! Текущий уровень: {pet.level}"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_pet_action_keyboard(pet.id),
    )


@router.callback_query(F.data.startswith("pet:pet:"))
async def callback_pet_pet(
    callback: CallbackQuery,
    session: AsyncSession,
    _,
) -> None:
    """Pet the pet."""
    await callback.answer()
    
    pet_id = int(callback.data.split(":")[2])
    
    result = await session.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    
    if not pet:
        await callback.message.edit_text("Питомец не найден!")
        return
    
    # Pet the pet
    old_happiness = pet.happiness
    pet.pet()
    
    await session.commit()
    
    # Show result with random reaction
    import random
    reactions = [
        f"{pet.name} мурлычет от удовольствия! 😊",
        f"{pet.name} радостно виляет хвостиком! 🐾",
        f"{pet.name} нежится под вашими руками! 💕",
        f"{pet.name} смотрит на вас с любовью! ❤️",
    ]
    
    text = random.choice(reactions) + "\n\n"
    text += f"Настроение: {old_happiness} → {pet.happiness}"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_pet_action_keyboard(pet.id),
    )


@router.callback_query(F.data.startswith("pet:play:"))
async def callback_play_with_pet(
    callback: CallbackQuery,
    session: AsyncSession,
    _,
) -> None:
    """Play with pet."""
    await callback.answer()
    
    pet_id = int(callback.data.split(":")[2])
    
    result = await session.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    
    if not pet:
        await callback.message.edit_text("Питомец не найден!")
        return
    
    # Check energy
    if pet.energy < 15:
        await callback.answer(
            f"{pet.name} слишком устал для игры! Дайте ему отдохнуть.",
            show_alert=True,
        )
        return
    
    # Play with pet
    old_happiness = pet.happiness
    old_energy = pet.energy
    
    success = pet.play(fun_value=20, energy_cost=15)
    
    if not success:
        await callback.answer("Недостаточно энергии!", show_alert=True)
        return
    
    leveled_up = pet.add_experience(10)
    
    await session.commit()
    
    # Show result
    import random
    games = [
        "Вы играете в мячик",
        "Вы запускаете лазерную указку",
        "Вы прячетесь в прятки",
        "Вы играете в догонялки",
    ]
    
    text = f"{random.choice(games)} с {pet.name}!\n\n"
    text += f"Настроение: {old_happiness} → {pet.happiness}\n"
    text += f"Энергия: {old_energy} → {pet.energy}\n"
    text += f"Опыт: +10"
    
    if leveled_up:
        text += f"\n\n🎉 Уровень повышен! Теперь {pet.name} {pet.level} уровня!"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_pet_action_keyboard(pet.id),
    )


@router.callback_query(F.data.startswith("pet:sleep:"))
async def callback_sleep_pet(
    callback: CallbackQuery,
    session: AsyncSession,
    _,
) -> None:
    """Put pet to sleep."""
    await callback.answer()
    
    pet_id = int(callback.data.split(":")[2])
    
    result = await session.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    
    if not pet:
        await callback.message.edit_text("Питомец не найден!")
        return
    
    # Check if already sleeping
    if pet.status == PetStatus.SLEEPING:
        await callback.answer(f"{pet.name} уже спит!", show_alert=True)
        return
    
    # Put to sleep
    pet.sleep(hours=4)
    
    await session.commit()
    
    text = (
        f"😴 {pet.name} уложен спать.\n\n"
        f"Питомец будет спать 4 часа и восстановит энергию.\n"
        f"Вы можете разбудить его досрочно."
    )
    
    # Add wake up button
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏰ Разбудить",
                    callback_data=f"pet:wake:{pet.id}"
                ),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="pet:status"),
            ],
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("pet:wake:"))
async def callback_wake_pet(
    callback: CallbackQuery,
    session: AsyncSession,
    _,
) -> None:
    """Wake up pet."""
    await callback.answer()
    
    pet_id = int(callback.data.split(":")[2])
    
    result = await session.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()
    
    if not pet:
        await callback.message.edit_text("Питомец не найден!")
        return
    
    if pet.status != PetStatus.SLEEPING:
        await callback.answer("Питомец не спит!", show_alert=True)
        return
    
    # Wake up
    pet.wake_up()
    
    await session.commit()
    
    await callback.message.edit_text(
        f"⏰ {pet.name} проснулся! Энергия восстановлена.",
        reply_markup=get_pet_action_keyboard(pet.id),
    )
