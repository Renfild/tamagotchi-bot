"""
User model for Telegram users.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    String,
    Boolean,
    DateTime,
    Integer,
    Float,
    Text,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from core.database import Base

if TYPE_CHECKING:
    from models.pet import Pet
    from models.inventory import InventoryItem
    from models.friend import Friend
    from models.battle import Battle
    from models.quest import UserQuest
    from models.achievement import UserAchievement
    from models.guild import GuildMember


class Language(str, PyEnum):
    """Supported languages."""
    RUSSIAN = "ru"
    ENGLISH = "en"
    SPANISH = "es"
    GERMAN = "de"
    FRENCH = "fr"


class NotificationLevel(str, PyEnum):
    """Notification preference levels."""
    ALL = "all"
    IMPORTANT = "important"
    NONE = "none"


class PrivacyLevel(str, PyEnum):
    """Privacy settings."""
    PUBLIC = "public"
    FRIENDS_ONLY = "friends_only"
    PRIVATE = "private"


class User(Base):
    """Telegram user model."""
    
    __tablename__ = "users"
    
    # Primary key - Telegram user ID
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    
    # Telegram info
    username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True, index=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    language_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Profile
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Currency
    coins: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    crystals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    arena_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Premium status
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    premium_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Statistics
    total_playtime_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    battles_won: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    battles_lost: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    quests_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pets_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Settings
    language: Mapped[Language] = mapped_column(
        Enum(Language), default=Language.RUSSIAN, nullable=False
    )
    notifications: Mapped[NotificationLevel] = mapped_column(
        Enum(NotificationLevel), default=NotificationLevel.ALL, nullable=False
    )
    privacy: Mapped[PrivacyLevel] = mapped_column(
        Enum(PrivacyLevel), default=PrivacyLevel.FRIENDS_ONLY, nullable=False
    )
    quiet_hours_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-23
    quiet_hours_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # 0-23
    
    # Feature flags
    can_receive_gifts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_be_invited: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    show_online_status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_daily_claim: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    pets: Mapped[List["Pet"]] = relationship(
        "Pet", back_populates="owner", lazy="selectin", cascade="all, delete-orphan"
    )
    inventory_items: Mapped[List["InventoryItem"]] = relationship(
        "InventoryItem", back_populates="owner", lazy="selectin", cascade="all, delete-orphan"
    )
    friends_sent: Mapped[List["Friend"]] = relationship(
        "Friend",
        foreign_keys="Friend.user_id",
        back_populates="user",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    friends_received: Mapped[List["Friend"]] = relationship(
        "Friend",
        foreign_keys="Friend.friend_id",
        back_populates="friend",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    battles_as_player1: Mapped[List["Battle"]] = relationship(
        "Battle",
        foreign_keys="Battle.player1_id",
        back_populates="player1",
        lazy="selectin",
    )
    battles_as_player2: Mapped[List["Battle"]] = relationship(
        "Battle",
        foreign_keys="Battle.player2_id",
        back_populates="player2",
        lazy="selectin",
    )
    quests: Mapped[List["UserQuest"]] = relationship(
        "UserQuest", back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )
    achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )
    guild_memberships: Mapped[List["GuildMember"]] = relationship(
        "GuildMember", back_populates="user", lazy="selectin", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, coins={self.coins})>"
    
    @property
    def display_name(self) -> str:
        """Get user's display name."""
        if self.username:
            return f"@{self.username}"
        name = self.first_name
        if self.last_name:
            name += f" {self.last_name}"
        return name
    
    @property
    def total_battles(self) -> int:
        """Get total number of battles."""
        return self.battles_won + self.battles_lost
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        total = self.total_battles
        if total == 0:
            return 0.0
        return round((self.battles_won / total) * 100, 2)
    
    def is_quiet_hours(self, hour: int) -> bool:
        """Check if given hour is in quiet hours."""
        if self.quiet_hours_start is None or self.quiet_hours_end is None:
            return False
        
        if self.quiet_hours_start <= self.quiet_hours_end:
            return self.quiet_hours_start <= hour < self.quiet_hours_end
        else:  # Crosses midnight
            return hour >= self.quiet_hours_start or hour < self.quiet_hours_end
    
    def can_afford(self, coins: int = 0, crystals: int = 0) -> bool:
        """Check if user can afford the given amount."""
        return self.coins >= coins and self.crystals >= crystals
    
    def deduct_currency(self, coins: int = 0, crystals: int = 0) -> bool:
        """Deduct currency from user. Returns True if successful."""
        if not self.can_afford(coins, crystals):
            return False
        self.coins -= coins
        self.crystals -= crystals
        return True
    
    def add_currency(self, coins: int = 0, crystals: int = 0) -> None:
        """Add currency to user."""
        self.coins += coins
        self.crystals += crystals
