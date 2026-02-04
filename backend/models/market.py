"""
Market model for player-to-player trading.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    Integer,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from core.database import Base

if TYPE_CHECKING:
    from models.user import User
    from models.item import Item


class MarketStatus(str, PyEnum):
    """Market listing status."""
    ACTIVE = "active"
    SOLD = "sold"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class MarketListing(Base):
    """Player market listing."""
    
    __tablename__ = "market_listings"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Seller
    seller_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Item
    item_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("items.id", ondelete="CASCADE"), nullable=False
    )
    
    # Listing details
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    price_coins: Mapped[int] = mapped_column(nullable=False)
    price_crystals: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Status
    status: Mapped[MarketStatus] = mapped_column(
        Enum(MarketStatus), default=MarketStatus.ACTIVE, nullable=False
    )
    
    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    sold_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Buyer (if sold)
    buyer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    
    # Relationships
    seller: Mapped["User"] = relationship(
        "User", foreign_keys=[seller_id], lazy="selectin"
    )
    buyer: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[buyer_id], lazy="selectin"
    )
    item: Mapped["Item"] = relationship("Item", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<MarketListing(id={self.id}, seller={self.seller_id}, item={self.item_id}, price={self.price_coins})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if listing has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def total_price_coins(self) -> int:
        """Calculate total price in coins."""
        return self.price_coins * self.quantity
    
    def cancel(self) -> bool:
        """Cancel the listing. Returns True if successful."""
        if self.status != MarketStatus.ACTIVE:
            return False
        
        self.status = MarketStatus.CANCELLED
        return True
    
    def mark_sold(self, buyer_id: int) -> None:
        """Mark listing as sold."""
        self.status = MarketStatus.SOLD
        self.buyer_id = buyer_id
        self.sold_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert listing to dictionary."""
        return {
            "id": self.id,
            "seller": {
                "id": self.seller_id,
                "name": self.seller.display_name if self.seller else None,
            },
            "item": self.item.to_dict() if self.item else None,
            "quantity": self.quantity,
            "price": {
                "coins": self.price_coins,
                "crystals": self.price_crystals,
                "total_coins": self.total_price_coins,
            },
            "status": self.status.value,
            "is_expired": self.is_expired,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }


class MarketTransaction(Base):
    """Record of market transactions."""
    
    __tablename__ = "market_transactions"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Listing reference
    listing_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("market_listings.id", ondelete="SET NULL"), nullable=True
    )
    
    # Transaction details
    seller_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    buyer_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    item_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price_coins: Mapped[int] = mapped_column(nullable=False)
    price_crystals: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Fees
    market_fee_percent: Mapped[int] = mapped_column(default=5, nullable=False)
    market_fee_amount: Mapped[int] = mapped_column(nullable=False)
    seller_received: Mapped[int] = mapped_column(nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<MarketTransaction(id={self.id}, seller={self.seller_id}, buyer={self.buyer_id})>"
    
    @classmethod
    def from_listing(cls, listing: MarketListing, buyer_id: int) -> "MarketTransaction":
        """Create transaction from listing."""
        fee_percent = 5
        total_price = listing.total_price_coins
        fee_amount = total_price * fee_percent // 100
        seller_received = total_price - fee_amount
        
        return cls(
            listing_id=listing.id,
            seller_id=listing.seller_id,
            buyer_id=buyer_id,
            item_id=listing.item_id,
            quantity=listing.quantity,
            price_coins=listing.price_coins,
            price_crystals=listing.price_crystals,
            market_fee_percent=fee_percent,
            market_fee_amount=fee_amount,
            seller_received=seller_received,
        )
