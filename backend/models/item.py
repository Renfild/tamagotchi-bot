"""
Item model for game items.
"""
from typing import TYPE_CHECKING, Optional, List, Dict, Any
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    Enum,
    JSON,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from core.database import Base

if TYPE_CHECKING:
    from models.inventory import InventoryItem


class ItemType(str, PyEnum):
    """Types of items."""
    FOOD = "food"
    TOY = "toy"
    MEDICINE = "medicine"
    CONTAINER = "container"
    CLOTHING = "clothing"
    DECOR = "decor"
    EVOLUTION = "evolution"
    SPECIAL = "special"


class ItemRarity(str, PyEnum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class ItemEffect(str, PyEnum):
    """Possible item effects."""
    HEAL = "heal"
    FEED = "feed"
    BOOST_HAPPINESS = "boost_happiness"
    BOOST_ENERGY = "boost_energy"
    BOOST_XP = "boost_xp"
    CURE_SICKNESS = "cure_sickness"
    CURE_POISON = "cure_poison"
    REVIVE = "revive"
    EVOLVE = "evolve"
    CHANGE_COLOR = "change_color"
    RANDOM_PET = "random_pet"


class Item(Base):
    """Game item definition."""
    
    __tablename__ = "items"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Basic info
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False, index=True)
    rarity: Mapped[ItemRarity] = mapped_column(
        Enum(ItemRarity), default=ItemRarity.COMMON, nullable=False
    )
    
    # Pricing
    buy_price_coins: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    buy_price_crystals: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sell_price_coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Availability
    is_purchasable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_sellable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_tradable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_consumable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Limitations
    min_level_required: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    max_stack_size: Mapped[int] = mapped_column(Integer, default=99, nullable=False)
    
    # Effects
    effects: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )  # {"heal": 20, "feed": 30}
    
    # Visual
    icon_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    animation_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    # Special flags
    is_premium_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_event_item: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    event_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    
    # Timed availability
    available_from: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    available_until: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Daily deal
    is_daily_deal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    daily_deal_discount: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Percentage
    
    # Relationships
    inventory_items: Mapped[List["InventoryItem"]] = relationship(
        "InventoryItem", back_populates="item_definition", lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Item(id={self.id}, name={self.name}, type={self.item_type})>"
    
    @property
    def display_price(self) -> str:
        """Get formatted price string."""
        if self.buy_price_crystals:
            return f"💎 {self.buy_price_crystals}"
        elif self.buy_price_coins:
            return f"🪙 {self.buy_price_coins}"
        return "🎁 Бесплатно"
    
    def get_effective_price(self) -> Dict[str, int]:
        """Get effective price with daily deal discount."""
        price = {}
        if self.buy_price_coins:
            discount = self.buy_price_coins * self.daily_deal_discount // 100
            price["coins"] = self.buy_price_coins - discount
        if self.buy_price_crystals:
            discount = self.buy_price_crystals * self.daily_deal_discount // 100
            price["crystals"] = self.buy_price_crystals - discount
        return price
    
    def can_be_used_on(self, pet_status: str) -> bool:
        """Check if item can be used on pet with given status."""
        if pet_status in ["deceased", "runaway"]:
            return ItemEffect.REVIVE in self.effects
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.item_type.value,
            "rarity": self.rarity.value,
            "price": self.get_effective_price(),
            "sell_price": self.sell_price_coins,
            "effects": self.effects,
            "icon_url": self.icon_url,
            "max_stack": self.max_stack_size,
            "is_premium": self.is_premium_only,
            "is_daily_deal": self.is_daily_deal,
            "daily_discount": self.daily_deal_discount,
        }
