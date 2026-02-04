"""
Friend model for user friendships.
"""
from datetime import datetime
from typing import TYPE_CHECKING
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from core.database import Base

if TYPE_CHECKING:
    from models.user import User


class FriendStatus(str, PyEnum):
    """Friend request status."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    BLOCKED = "blocked"
    DECLINED = "declined"


class Friend(Base):
    """Friendship relationship between users."""
    
    __tablename__ = "friends"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Users in friendship
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    friend_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Status
    status: Mapped[FriendStatus] = mapped_column(
        Enum(FriendStatus), default=FriendStatus.PENDING, nullable=False
    )
    
    # Interaction tracking
    last_interaction_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    gifts_sent: Mapped[int] = mapped_column(default=0, nullable=False)
    gifts_received: Mapped[int] = mapped_column(default=0, nullable=False)
    battles_together: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Metadata
    initiated_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message: Mapped[str] = mapped_column(default="", nullable=True)  # Optional message with request
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User", foreign_keys=[user_id], back_populates="friends_sent", lazy="selectin"
    )
    friend: Mapped["User"] = relationship(
        "User", foreign_keys=[friend_id], back_populates="friends_received", lazy="selectin"
    )
    
    # Unique constraint - prevent duplicate friendships
    __table_args__ = (
        UniqueConstraint("user_id", "friend_id", name="uix_friendship"),
    )
    
    def __repr__(self) -> str:
        return f"<Friend(id={self.id}, user={self.user_id}, friend={self.friend_id}, status={self.status})>"
    
    def accept(self) -> None:
        """Accept friend request."""
        self.status = FriendStatus.ACCEPTED
        self.last_interaction_at = datetime.utcnow()
    
    def decline(self) -> None:
        """Decline friend request."""
        self.status = FriendStatus.DECLINED
    
    def block(self) -> None:
        """Block the friendship."""
        self.status = FriendStatus.BLOCKED
    
    def record_gift(self, sent: bool = True) -> None:
        """Record a gift exchange."""
        if sent:
            self.gifts_sent += 1
        else:
            self.gifts_received += 1
        self.last_interaction_at = datetime.utcnow()
    
    def record_battle(self) -> None:
        """Record a battle together."""
        self.battles_together += 1
        self.last_interaction_at = datetime.utcnow()
    
    @property
    def is_mutual(self) -> bool:
        """Check if friendship is mutual (accepted)."""
        return self.status == FriendStatus.ACCEPTED
    
    @property
    def friendship_score(self) -> int:
        """Calculate friendship score based on interactions."""
        return (
            self.gifts_sent * 10 +
            self.gifts_received * 10 +
            self.battles_together * 5
        )
