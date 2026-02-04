"""
Inventory command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.inventory import InventoryItem
from models.item import ItemType
from bot.keyboards.main import get_main_menu_keyboard

router = Router()


@router.message(Command("inventory"))
async def cmd_inventory(
    message: Message,
    session: AsyncSession,
    _,
) -> None:
    """Handle /inventory command."""
    user_id = message.from_user.id
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.inventory_items:
        await message.answer(
            "🎒 Ваш инвентарь пуст!\n\n"
            "Посетите магазин, чтобы купить предметы.",
            reply_markup=get_main_menu_keyboard(user) if user else None,
        )
        return
    
    # Group items by type
    items_by_type = {}
    for inv_item in user.inventory_items:
        if inv_item.quantity > 0:
            item_type = inv_item.item_definition.item_type.value
            if item_type not in items_by_type:
                items_by_type[item_type] = []
            items_by_type[item_type].append(inv_item)
    
    # Build text
    text = "🎒 <b>Ваш инвентарь:</b>\n\n"
    
    type_emojis = {
        "food": "🍎",
        "toy": "🎾",
        "medicine": "💊",
        "container": "🎁",
        "clothing": "🧥",
        "decor": "🏠",
    }
    
    for item_type, items in items_by_type.items():
        emoji = type_emojis.get(item_type, "📦")
        text += f"{emoji} <b>{item_type.title()}:</b>\n"
        for inv_item in items:
            item = inv_item.item_definition
            equipped = " 👕" if inv_item.is_equipped else ""
            text += f"  • {item.name} x{inv_item.quantity}{equipped}\n"
        text += "\n"
    
    await message.answer(text, reply_markup=get_main_menu_keyboard(user), parse_mode="HTML")


@router.callback_query(F.data == "inventory:show")
async def callback_inventory(
    callback: CallbackQuery,
    session: AsyncSession,
    _,
) -> None:
    """Show inventory from callback."""
    await callback.answer()
    await cmd_inventory(callback.message, session, _)
