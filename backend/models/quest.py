"""
Quest model for daily/weekly quests.
"""
from datetime import datetime, timedelta
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
    Boolean,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from core.database import Base

if TYPE_CHECKING:
    from models.user import User


class QuestType(str, PyEnum):
    """Types of quest objectives."""
    FEED_PET = "feed_pet"
    PLAY_GAME = "play_game"
    PET_PET = "pet_pet"
    WIN_BATTLE = "win_battle"
    LEVEL_UP_PET = "level_up_pet"
    BREED_PET = "breed_pet"
    BUY_ITEM = "buy_item"
    USE_ITEM = "use_item"
    VISIT_FRIEND = "visit_friend"
    SEND_GIFT = "send_gift"
    COMPLETE_DAILY = "complete_daily"
    PLAY_MINI_GAME = "play_mini_game"


class QuestFrequency(str, PyEnum):
    """Quest frequency/reset period."""
    DAILY = "daily"
    WEEKLY = "weekly"
    EVENT = "event"
    ONE_TIME = "one_time"


class Quest(Base):
    """Quest definition/template."""
    
    __tablename__ = "quests"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Basic info
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Quest type
    quest_type: Mapped[QuestType] = mapped_column(Enum(QuestType), nullable=False, index=True)
    frequency: Mapped[QuestFrequency] = mapped_column(
        Enum(QuestFrequency), default=QuestFrequency.DAILY, nullable=False
    )
    
    # Requirements
    target_count: Mapped[int] = mapped_column(default=1, nullable=False)
    target_item_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("items.id", ondelete="SET NULL"), nullable=True
    )
    min_level_required: Mapped[int] = mapped_column(default=1, nullable=False)
    
    # Rewards
    reward_coins: Mapped[int] = mapped_column(default=0, nullable=False)
    reward_crystals: Mapped[int] = mapped_column(default=0, nullable=False)
    reward_exp: Mapped[int] = mapped_column(default=0, nullable=False)
    reward_item_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("items.id", ondelete="SET NULL"), nullable=True
    )
    reward_item_quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    
    # Visual
    icon_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    # Event quest
    event_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Active status
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<Quest(id={self.id}, title={self.title}, type={self.quest_type})>"
    
    @property
    def is_available(self) -> bool:
        """Check if quest is currently available."""
        if not self.is_active:
            return False
        
        now = datetime.utcnow()
        if self.starts_at and now < self.starts_at:
            return False
        if self.ends_at and now > self.ends_at:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quest to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.quest_type.value,
            "frequency": self.frequency.value,
            "target_count": self.target_count,
            "rewards": {
                "coins": self.reward_coins,
                "crystals": self.reward_crystals,
                "exp": self.reward_exp,
                "item_id": self.reward_item_id,
                "item_quantity": self.reward_item_quantity,
            },
            "icon_url": self.icon_url,
            "is_available": self.is_available,
        }


class UserQuest(Base):
    """User's quest progress."""
    
    __tablename__ = "user_quests"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # User
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Quest
    quest_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("quests.id", ondelete="CASCADE"), nullable=False
    )
    
    # Progress
    current_progress: Mapped[int] = mapped_column(default=0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_claimed: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="quests", lazy="selectin")
    quest: Mapped["Quest"] = relationship("Quest", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<UserQuest(id={self.id}, user={self.user_id}, quest={self.quest_id}, progress={self.current_progress})>"
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if not self.quest:
            return 0.0
        return min(100.0, (self.current_progress / self.quest.target_count) * 100)
    
    @property
    def is_expired(self) -> bool:
        """Check if quest has expired."""
        return datetime.utcnow() > self.expires_at
    
    def add_progress(self, amount: int = 1) -> bool:
        """Add progress to quest. Returns True if completed."""
        if self.is_completed or self.is_expired:
            return False
        
        self.current_progress += amount
        
        if self.quest and self.current_progress >= self.quest.target_count:
            self.complete()
            return True
        
        return False
    
    def complete(self) -> None:
        """Mark quest as completed."""
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        self.current_progress = self.quest.target_count if self.quest else self.current_progress
    
    def claim(self) -> Dict[str, int]:
        """Claim quest rewards. Returns reward amounts."""
        if not self.is_completed or self.is_claimed:
            return {}
        
        self.is_claimed = True
        self.claimed_at = datetime.utcnow()
        
        if not self.quest:
            return {}
        
        return {
            "coins": self.quest.reward_coins,
            "crystals": self.quest.reward_crystals,
            "exp": self.quest.reward_exp,
            "item_id": self.quest.reward_item_id,
            "item_quantity": self.quest.reward_item_quantity,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user quest to dictionary."""
        return {
            "id": self.id,
            "quest": self.quest.to_dict() if self.quest else None,
            "progress": {
                "current": self.current_progress,
                "target": self.quest.target_count if self.quest else 0,
                "percent": self.progress_percent,
            },
            "is_completed": self.is_completed,
            "is_claimed": self.is_claimed,
            "is_expired": self.is_expired,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
