"""
Main keyboards for the bot.
"""
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
)

from core.config import settings
from models.user import User


def get_main_menu_keyboard(user: User) -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎮 Открыть игру",
                    web_app=WebAppInfo(url=settings.WEBAPP_URL)
                ),
            ],
            [
                InlineKeyboardButton(text="🐾 Мой питомец", callback_data="pet:status"),
                InlineKeyboardButton(text="🎒 Инвентарь", callback_data="inventory:show"),
            ],
            [
                InlineKeyboardButton(text="🛒 Магазин", callback_data="shop:show"),
                InlineKeyboardButton(text="🎯 Игры", callback_data="games:list"),
            ],
            [
                InlineKeyboardButton(text="👥 Друзья", callback_data="friends:list"),
                InlineKeyboardButton(text="⚔️ Арена", callback_data="arena:menu"),
            ],
            [
                InlineKeyboardButton(text="📜 Квесты", callback_data="quests:list"),
                InlineKeyboardButton(text="🏆 Достижения", callback_data="achievements:list"),
            ],
            [
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings:menu"),
                InlineKeyboardButton(text="❓ Помощь", callback_data="help:menu"),
            ],
        ]
    )


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
            ],
            [
                InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang:es"),
                InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="lang:de"),
            ],
        ]
    )


def get_pet_action_keyboard(pet_id: int) -> InlineKeyboardMarkup:
    """Get pet action keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🍎 Покормить", callback_data=f"pet:feed:{pet_id}"),
                InlineKeyboardButton(text="🤗 Погладить", callback_data=f"pet:pet:{pet_id}"),
            ],
            [
                InlineKeyboardButton(text="🎮 Играть", callback_data=f"pet:play:{pet_id}"),
                InlineKeyboardButton(text="😴 Уложить спать", callback_data=f"pet:sleep:{pet_id}"),
            ],
            [
                InlineKeyboardButton(text="🎒 Дать предмет", callback_data=f"pet:item:{pet_id}"),
                InlineKeyboardButton(text="👕 Одежда", callback_data=f"pet:clothes:{pet_id}"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )


def get_shop_keyboard() -> InlineKeyboardMarkup:
    """Get shop categories keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🍎 Еда", callback_data="shop:category:food"),
                InlineKeyboardButton(text="🎾 Игрушки", callback_data="shop:category:toy"),
            ],
            [
                InlineKeyboardButton(text="💊 Лекарства", callback_data="shop:category:medicine"),
                InlineKeyboardButton(text="🎁 Контейнеры", callback_data="shop:category:container"),
            ],
            [
                InlineKeyboardButton(text="🧥 Одежда", callback_data="shop:category:clothing"),
                InlineKeyboardButton(text="🏠 Декор", callback_data="shop:category:decor"),
            ],
            [
                InlineKeyboardButton(text="💎 Премиум", callback_data="shop:premium"),
                InlineKeyboardButton(text="🎁 Наборы", callback_data="shop:bundles"),
            ],
            [
                InlineKeyboardButton(text="💳 Пополнить", callback_data="shop:deposit"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )


def get_games_keyboard() -> InlineKeyboardMarkup:
    """Get games list keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏃 Бег за едой", callback_data="game:food_run"),
                InlineKeyboardButton(text="🧩 Пазл", callback_data="game:puzzle"),
            ],
            [
                InlineKeyboardButton(text="🎵 Ритм-игра", callback_data="game:rhythm"),
                InlineKeyboardButton(text="🎣 Рыбалка", callback_data="game:fishing"),
            ],
            [
                InlineKeyboardButton(text="🎯 Лабиринт", callback_data="game:maze"),
                InlineKeyboardButton(text="🎲 Угадайка", callback_data="game:guess"),
            ],
            [
                InlineKeyboardButton(text="⚔️ PvP Дуэль", callback_data="game:pvp_duel"),
                InlineKeyboardButton(text="🏁 Гонки", callback_data="game:racing"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )


def get_friends_keyboard() -> InlineKeyboardMarkup:
    """Get friends menu keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👥 Мои друзья", callback_data="friends:list"),
                InlineKeyboardButton(text="➕ Добавить", callback_data="friends:add"),
            ],
            [
                InlineKeyboardButton(text="📨 Заявки", callback_data="friends:requests"),
                InlineKeyboardButton(text="🎁 Подарки", callback_data="friends:gifts"),
            ],
            [
                InlineKeyboardButton(text="🐾 Разведение", callback_data="friends:breeding"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )


def get_settings_keyboard(user: User) -> InlineKeyboardMarkup:
    """Get settings keyboard."""
    notif_text = "🔔 Уведомления: " + ("Вкл" if user.notifications.value != "none" else "Выкл")
    privacy_text = "👁 Приватность: " + user.privacy.value
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🌍 Язык", callback_data="settings:language"),
                InlineKeyboardButton(text=notif_text, callback_data="settings:notifications"),
            ],
            [
                InlineKeyboardButton(text=privacy_text, callback_data="settings:privacy"),
                InlineKeyboardButton(text="🔕 Тихий час", callback_data="settings:quiet_hours"),
            ],
            [
                InlineKeyboardButton(text="📊 Моя статистика", callback_data="settings:stats"),
                InlineKeyboardButton(text="📤 Экспорт данных", callback_data="settings:export"),
            ],
            [
                InlineKeyboardButton(text="🔙 Назад", callback_data="menu:main"),
            ],
        ]
    )


def get_confirmation_keyboard(
    confirm_callback: str,
    cancel_callback: str = "menu:main",
) -> InlineKeyboardMarkup:
    """Get confirmation keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да", callback_data=confirm_callback),
                InlineKeyboardButton(text="❌ Нет", callback_data=cancel_callback),
            ],
        ]
    )


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    base_callback: str,
) -> InlineKeyboardMarkup:
    """Get pagination keyboard."""
    buttons = []
    
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(text="◀️", callback_data=f"{base_callback}:page:{current_page - 1}")
        )
    
    buttons.append(
        InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="noop")
    )
    
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(text="▶️", callback_data=f"{base_callback}:page:{current_page + 1}")
        )
    
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
