"""
Guild model for player guilds/clans.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List, Dict, Any
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


class GuildRole(str, PyEnum):
    """Guild member roles."""
    LEADER = "leader"
    OFFICER = "officer"
    MEMBER = "member"
    RECRUIT = "recruit"


class Guild(Base):
    """Player guild/clan."""
    
    __tablename__ = "guilds"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Basic info
    name: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    tag: Mapped[str] = mapped_column(String(4), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Leader
    leader_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    
    # Stats
    level: Mapped[int] = mapped_column(default=1, nullable=False)
    experience: Mapped[int] = mapped_column(default=0, nullable=False)
    max_members: Mapped[int] = mapped_column(default=20, nullable=False)
    
    # Treasury
    treasury_coins: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Visual
    emblem_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    emblem_color: Mapped[str] = mapped_column(String(7), default="#FFD700", nullable=False)
    
    # Settings
    is_recruiting: Mapped[bool] = mapped_column(default=True, nullable=False)
    min_level_required: Mapped[int] = mapped_column(default=1, nullable=False)
    is_public: Mapped[bool] = mapped_column(default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    # Relationships
    members: Mapped[List["GuildMember"]] = relationship(
        "GuildMember", back_populates="guild", lazy="selectin", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Guild(id={self.id}, name={self.name}, tag={self.tag})>"
    
    @property
    def member_count(self) -> int:
        """Get current member count."""
        return len(self.members)
    
    @property
    def is_full(self) -> bool:
        """Check if guild is full."""
        return self.member_count >= self.max_members
    
    @property
    can_join: bool = property(lambda self: self.is_recruiting and not self.is_full)
    
    def get_leader(self) -> Optional["GuildMember"]:
        """Get guild leader."""
        for member in self.members:
            if member.role == GuildRole.LEADER:
                return member
        return None
    
    def get_officers(self) -> List["GuildMember"]:
        """Get all officers."""
        return [m for m in self.members if m.role == GuildRole.OFFICER]
    
    def add_experience(self, amount: int) -> bool:
        """Add guild experience. Returns True if leveled up."""
        self.experience += amount
        
        # Simple level formula
        exp_needed = self.level * 1000
        
        if self.experience >= exp_needed:
            self.level_up()
            return True
        return False
    
    def level_up(self) -> None:
        """Level up the guild."""
        self.level += 1
        self.max_members = min(50, 20 + self.level * 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert guild to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "tag": self.tag,
            "description": self.description,
            "level": self.level,
            "experience": self.experience,
            "members": {
                "current": self.member_count,
                "max": self.max_members,
            },
            "leader": self.get_leader().to_dict() if self.get_leader() else None,
            "emblem": {
                "url": self.emblem_url,
                "color": self.emblem_color,
            },
            "is_recruiting": self.is_recruiting,
            "min_level": self.min_level_required,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class GuildMember(Base):
    """Guild membership."""
    
    __tablename__ = "guild_members"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Guild
    guild_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # User
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Role
    role: Mapped[GuildRole] = mapped_column(
        Enum(GuildRole), default=GuildRole.RECRUIT, nullable=False
    )
    
    # Contributions
    total_contributed_coins: Mapped[int] = mapped_column(default=0, nullable=False)
    battles_won: Mapped[int] = mapped_column(default=0, nullable=False)
    quests_completed: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Timestamps
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    # Relationships
    guild: Mapped["Guild"] = relationship("Guild", back_populates="members", lazy="selectin")
    user: Mapped["User"] = relationship("User", back_populates="guild_memberships", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<GuildMember(id={self.id}, guild={self.guild_id}, user={self.user_id}, role={self.role})>"
    
    @property
    def is_leader(self) -> bool:
        """Check if member is leader."""
        return self.role == GuildRole.LEADER
    
    @property
    def is_officer(self) -> bool:
        """Check if member is officer."""
        return self.role == GuildRole.OFFICER
    
    @property
    def can_invite(self) -> bool:
        """Check if member can invite others."""
        return self.role in [GuildRole.LEADER, GuildRole.OFFICER]
    
    @property
    def can_kick(self) -> bool:
        """Check if member can kick others."""
        return self.role in [GuildRole.LEADER, GuildRole.OFFICER]
    
    def promote(self) -> bool:
        """Promote member to next role."""
        promotion_order = [
            GuildRole.RECRUIT,
            GuildRole.MEMBER,
            GuildRole.OFFICER,
        ]
        
        if self.role not in promotion_order:
            return False
        
        current_idx = promotion_order.index(self.role)
        if current_idx < len(promotion_order) - 1:
            self.role = promotion_order[current_idx + 1]
            return True
        return False
    
    def demote(self) -> bool:
        """Demote member to previous role."""
        if self.role == GuildRole.LEADER:
            return False
        
        demotion_order = [
            GuildRole.OFFICER,
            GuildRole.MEMBER,
            GuildRole.RECRUIT,
        ]
        
        if self.role not in demotion_order:
            return False
        
        current_idx = demotion_order.index(self.role)
        if current_idx < len(demotion_order) - 1:
            self.role = demotion_order[current_idx + 1]
            return True
        return False
    
    def contribute(self, amount: int) -> None:
        """Contribute coins to guild treasury."""
        self.total_contributed_coins += amount
        if self.guild:
            self.guild.treasury_coins += amount
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_active_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert guild member to dictionary."""
        return {
            "id": self.id,
            "user": {
                "id": self.user_id,
                "name": self.user.display_name if self.user else None,
                "avatar": self.user.avatar_url if self.user else None,
            },
            "role": self.role.value,
            "contributions": {
                "coins": self.total_contributed_coins,
                "battles_won": self.battles_won,
                "quests_completed": self.quests_completed,
            },
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "last_active": self.last_active_at.isoformat() if self.last_active_at else None,
        }
