"""
Achievement model for user achievements.
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
    from models.user import User


class AchievementCategory(str, PyEnum):
    """Achievement categories."""
    GENERAL = "general"
    COLLECTION = "collection"
    BATTLE = "battle"
    SOCIAL = "social"
    CARE = "care"
    SPECIAL = "special"
    EVENT = "event"


class AchievementRarity(str, PyEnum):
    """Achievement rarity."""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class Achievement(Base):
    """Achievement definition."""
    
    __tablename__ = "achievements"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Basic info
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Category
    category: Mapped[AchievementCategory] = mapped_column(
        Enum(AchievementCategory), default=AchievementCategory.GENERAL, nullable=False
    )
    rarity: Mapped[AchievementRarity] = mapped_column(
        Enum(AchievementRarity), default=AchievementRarity.BRONZE, nullable=False
    )
    
    # Requirements
    requirement_type: Mapped[str] = mapped_column(String(32), nullable=False)
    requirement_value: Mapped[int] = mapped_column(nullable=False)
    requirement_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Rewards
    reward_coins: Mapped[int] = mapped_column(default=0, nullable=False)
    reward_crystals: Mapped[int] = mapped_column(default=0, nullable=False)
    reward_title: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    # Visual
    icon_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    badge_color: Mapped[str] = mapped_column(String(7), default="#CD7F32", nullable=False)
    
    # Hidden achievement
    is_hidden: Mapped[bool] = mapped_column(default=False, nullable=False)
    hidden_hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Order
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Relationships
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement", lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Achievement(id={self.id}, name={self.name}, category={self.category})>"
    
    def to_dict(self, include_hidden: bool = False) -> Dict[str, Any]:
        """Convert achievement to dictionary."""
        data = {
            "id": self.id,
            "name": self.name,
            "title": self.title if not self.is_hidden or include_hidden else "???",
            "description": self.description if not self.is_hidden or include_hidden else self.hidden_hint or "Секретное достижение",
            "category": self.category.value,
            "rarity": self.rarity.value,
            "icon_url": self.icon_url,
            "badge_color": self.badge_color,
            "is_hidden": self.is_hidden,
            "rewards": {
                "coins": self.reward_coins,
                "crystals": self.reward_crystals,
                "title": self.reward_title,
            },
        }
        return data


class UserAchievement(Base):
    """User's earned achievement."""
    
    __tablename__ = "user_achievements"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # User
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Achievement
    achievement_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False
    )
    
    # Progress (for multi-tier achievements)
    progress: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Earned
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    # Claimed
    is_reward_claimed: Mapped[bool] = mapped_column(default=False, nullable=False)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements", lazy="selectin")
    achievement: Mapped["Achievement"] = relationship(
        "Achievement", back_populates="user_achievements", lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<UserAchievement(id={self.id}, user={self.user_id}, achievement={self.achievement_id})>"
    
    def claim_reward(self) -> Dict[str, int]:
        """Claim achievement reward."""
        if self.is_reward_claimed or not self.achievement:
            return {}
        
        self.is_reward_claimed = True
        self.claimed_at = datetime.utcnow()
        
        return {
            "coins": self.achievement.reward_coins,
            "crystals": self.achievement.reward_crystals,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user achievement to dictionary."""
        return {
            "id": self.id,
            "achievement": self.achievement.to_dict(include_hidden=True) if self.achievement else None,
            "earned_at": self.earned_at.isoformat() if self.earned_at else None,
            "is_reward_claimed": self.is_reward_claimed,
        }
