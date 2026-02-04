"""
Breeding model for pet breeding/ mating.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Dict, Any
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    String,
    Integer,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    Text,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from core.database import Base

if TYPE_CHECKING:
    from models.pet import Pet


class BreedingStatus(str, PyEnum):
    """Breeding request status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class BreedingRequest(Base):
    """Request for breeding two pets."""
    
    __tablename__ = "breeding_requests"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Requester (pet 1 owner)
    requester_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    pet1_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False
    )
    
    # Recipient (pet 2 owner)
    recipient_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    pet2_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False
    )
    
    # Status
    status: Mapped[BreedingStatus] = mapped_column(
        Enum(BreedingStatus), default=BreedingStatus.PENDING, nullable=False
    )
    
    # Message
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Breeding duration (hours)
    breeding_duration_hours: Mapped[int] = mapped_column(default=24, nullable=False)
    breeding_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    breeding_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Result
    result_pet_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("pets.id", ondelete="SET NULL"), nullable=True
    )
    
    # Inheritance data
    inherited_traits: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Costs
    coins_cost: Mapped[int] = mapped_column(default=500, nullable=False)
    crystals_cost: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Who paid
    paid_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    responded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    pet1: Mapped["Pet"] = relationship(
        "Pet", foreign_keys=[pet1_id], back_populates="breeding_requests_sent", lazy="selectin"
    )
    pet2: Mapped["Pet"] = relationship(
        "Pet", foreign_keys=[pet2_id], back_populates="breeding_requests_received", lazy="selectin"
    )
    result_pet: Mapped[Optional["Pet"]] = relationship(
        "Pet", foreign_keys=[result_pet_id], lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<BreedingRequest(id={self.id}, pet1={self.pet1_id}, pet2={self.pet2_id}, status={self.status})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if request has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def progress_percent(self) -> float:
        """Calculate breeding progress percentage."""
        if self.status != BreedingStatus.IN_PROGRESS:
            return 0.0 if self.status != BreedingStatus.COMPLETED else 100.0
        
        if not self.breeding_started_at:
            return 0.0
        
        elapsed = (datetime.utcnow() - self.breeding_started_at).total_seconds()
        total = self.breeding_duration_hours * 3600
        
        return min(100.0, (elapsed / total) * 100)
    
    @property
    def is_ready_to_complete(self) -> bool:
        """Check if breeding is ready to be completed."""
        if self.status != BreedingStatus.IN_PROGRESS:
            return False
        
        if not self.breeding_started_at:
            return False
        
        elapsed_hours = (datetime.utcnow() - self.breeding_started_at).total_seconds() / 3600
        return elapsed_hours >= self.breeding_duration_hours
    
    def accept(self) -> None:
        """Accept breeding request."""
        self.status = BreedingStatus.ACCEPTED
        self.responded_at = datetime.utcnow()
    
    def decline(self) -> None:
        """Decline breeding request."""
        self.status = BreedingStatus.DECLINED
        self.responded_at = datetime.utcnow()
    
    def start_breeding(self) -> None:
        """Start the breeding process."""
        self.status = BreedingStatus.IN_PROGRESS
        self.breeding_started_at = datetime.utcnow()
        
        # Set cooldowns on parent pets
        if self.pet1:
            from datetime import timedelta
            self.pet1.breeding_cooldown_until = datetime.utcnow() + timedelta(days=7)
        if self.pet2:
            from datetime import timedelta
            self.pet2.breeding_cooldown_until = datetime.utcnow() + timedelta(days=7)
    
    def complete(self, result_pet_id: int, inherited_traits: Dict[str, Any]) -> None:
        """Complete breeding with result."""
        self.status = BreedingStatus.COMPLETED
        self.breeding_completed_at = datetime.utcnow()
        self.result_pet_id = result_pet_id
        self.inherited_traits = inherited_traits
    
    def calculate_offspring_rarity(self) -> "Rarity":
        """Calculate offspring rarity based on parents."""
        import random
        from models.pet import Rarity
        
        if not self.pet1 or not self.pet2:
            return Rarity.COMMON
        
        # Rarity hierarchy
        rarity_order = [
            Rarity.COMMON,
            Rarity.UNCOMMON,
            Rarity.RARE,
            Rarity.EPIC,
            Rarity.LEGENDARY,
            Rarity.MYTHIC,
        ]
        
        r1_idx = rarity_order.index(self.pet1.rarity)
        r2_idx = rarity_order.index(self.pet2.rarity)
        
        # Average rarity
        avg_idx = (r1_idx + r2_idx) // 2
        
        # 20% chance to upgrade rarity
        if random.random() < 0.2 and avg_idx < len(rarity_order) - 1:
            avg_idx += 1
        
        return rarity_order[avg_idx]
    
    def generate_offspring_appearance(self) -> Dict[str, Any]:
        """Generate offspring appearance from parents."""
        import random
        
        if not self.pet1 or not self.pet2:
            return {}
        
        # Mix colors
        def mix_color(c1: str, c2: str) -> str:
            # Simple color mixing - in production use proper color math
            return c1 if random.random() < 0.5 else c2
        
        return {
            "primary_color": mix_color(self.pet1.primary_color, self.pet2.primary_color),
            "secondary_color": mix_color(self.pet1.secondary_color, self.pet2.secondary_color),
            "eye_color": mix_color(self.pet1.eye_color, self.pet2.eye_color),
            "pattern": self.pet1.pattern if random.random() < 0.5 else self.pet2.pattern,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert breeding request to dictionary."""
        return {
            "id": self.id,
            "status": self.status.value,
            "pet1": self.pet1.to_dict() if self.pet1 else None,
            "pet2": self.pet2.to_dict() if self.pet2 else None,
            "result_pet": self.result_pet.to_dict() if self.result_pet else None,
            "progress_percent": self.progress_percent,
            "is_ready_to_complete": self.is_ready_to_complete,
            "costs": {
                "coins": self.coins_cost,
                "crystals": self.crystals_cost,
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
