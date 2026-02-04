"""
Inventory model for user items.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any

from sqlalchemy import (
    BigInteger,
    Integer,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from core.database import Base

if TYPE_CHECKING:
    from models.user import User
    from models.item import Item


class InventoryItem(Base):
    """User's inventory item instance."""
    
    __tablename__ = "inventory"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Owner
    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Item definition
    item_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    
    # Quantity
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # State
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    equipped_on_pet_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("pets.id", ondelete="SET NULL"), nullable=True
    )
    
    # Durability (for toys/clothing)
    durability: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_durability: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Metadata
    obtained_from: Mapped[str] = mapped_column(
        String(32), default="unknown", nullable=False
    )  # shop, quest, battle, gift, breeding, etc.
    obtained_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    # For time-limited items
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Custom data
    custom_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )  # For items with unique properties
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="inventory_items", lazy="selectin")
    item_definition: Mapped["Item"] = relationship(
        "Item", back_populates="inventory_items", lazy="selectin"
    )
    equipped_on_pet: Mapped[Optional["Pet"]] = relationship("Pet", lazy="selectin")
    
    # Unique constraint - one row per item type per user
    __table_args__ = (
        UniqueConstraint("owner_id", "item_id", name="uix_inventory_user_item"),
    )
    
    def __repr__(self) -> str:
        return f"<InventoryItem(id={self.id}, owner={self.owner_id}, item={self.item_id}, qty={self.quantity})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if item has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def durability_percent(self) -> Optional[float]:
        """Calculate durability percentage."""
        if self.max_durability is None or self.durability is None:
            return None
        if self.max_durability == 0:
            return 100.0
        return round((self.durability / self.max_durability) * 100, 2)
    
    @property
    def is_usable(self) -> bool:
        """Check if item can be used."""
        if self.is_expired:
            return False
        if self.durability is not None and self.durability <= 0:
            return False
        return True
    
    def use(self, amount: int = 1) -> bool:
        """Use the item. Returns True if successful."""
        if not self.is_usable:
            return False
        if self.quantity < amount:
            return False
        
        self.quantity -= amount
        
        # Reduce durability for equippable items
        if self.is_equipped and self.durability is not None:
            self.durability -= 1
        
        return True
    
    def equip(self, pet_id: Optional[int] = None) -> bool:
        """Equip the item."""
        if self.item_definition.item_type not in [
            "clothing", "toy", "decor"
        ]:
            return False
        
        self.is_equipped = True
        self.equipped_on_pet_id = pet_id
        return True
    
    def unequip(self) -> None:
        """Unequip the item."""
        self.is_equipped = False
        self.equipped_on_pet_id = None
    
    def repair(self, amount: int) -> None:
        """Repair item durability."""
        if self.durability is not None and self.max_durability is not None:
            self.durability = min(self.max_durability, self.durability + amount)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory item to dictionary."""
        return {
            "id": self.id,
            "item": self.item_definition.to_dict() if self.item_definition else None,
            "quantity": self.quantity,
            "is_equipped": self.is_equipped,
            "equipped_on_pet": self.equipped_on_pet_id,
            "durability": self.durability,
            "durability_percent": self.durability_percent,
            "is_usable": self.is_usable,
            "is_expired": self.is_expired,
            "obtained_from": self.obtained_from,
            "obtained_at": self.obtained_at.isoformat() if self.obtained_at else None,
        }
