"""
Shop command handler.
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.item import Item, ItemType
from bot.keyboards.main import get_shop_keyboard, get_main_menu_keyboard

router = Router()


@router.message(Command("shop"))
async def cmd_shop(
    message: Message,
    session: AsyncSession,
    _,
) -> None:
    """Handle /shop command."""
    text = (
        "🛒 <b>Магазин</b>\n\n"
        "Выберите категорию товаров:\n\n"
        "🍎 <b>Еда</b> - Поддерживайте сытость питомца\n"
        "🎾 <b>Игрушки</b> - Развлекайте питомца\n"
        "💊 <b>Лекарства</b> - Лечите болезни\n"
        "🎁 <b>Контейнеры</b> - Случайные награды\n"
        "🧥 <b>Одежда</b> - Украшайте питомца\n"
        "🏠 <b>Декор</b> - Улучшайте комнату"
    )
    
    await message.answer(text, reply_markup=get_shop_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "shop:show")
async def callback_shop(
    callback: CallbackQuery,
    session: AsyncSession,
    _,
) -> None:
    """Show shop from callback."""
    await callback.answer()
    await cmd_shop(callback.message, session, _)


@router.callback_query(F.data.startswith("shop:category:"))
async def callback_shop_category(
    callback: CallbackQuery,
    session: AsyncSession,
    _,
) -> None:
    """Show shop category."""
    await callback.answer()
    
    category = callback.data.split(":")[2]
    item_type = ItemType(category)
    
    # Get items from this category
    result = await session.execute(
        select(Item)
        .where(Item.item_type == item_type)
        .where(Item.is_purchasable == True)
        .where(Item.is_active == True)
    )
    items = result.scalars().all()
    
    if not items:
        await callback.message.edit_text(
            "В этой категории пока нет товаров.",
            reply_markup=get_shop_keyboard(),
        )
        return
    
    text = f"📦 <b>{category.title()}</b>\n\n"
    
    for item in items:
        price = ""
        if item.buy_price_crystals:
            price = f"💎 {item.buy_price_crystals}"
        elif item.buy_price_coins:
            price = f"🪙 {item.buy_price_coins}"
        
        text += f"<b>{item.name}</b> - {price}\n"
        text += f"{item.description}\n\n"
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="shop:show")],
        ]
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
