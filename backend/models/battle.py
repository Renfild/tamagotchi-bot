"""
Battle model for PvP battles.
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
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from core.database import Base

if TYPE_CHECKING:
    from models.user import User
    from models.pet import Pet


class BattleStatus(str, PyEnum):
    """Battle status."""
    PENDING = "pending"      # Waiting for opponent to accept
    ACTIVE = "active"        # Battle in progress
    FINISHED = "finished"    # Battle completed
    CANCELLED = "cancelled"  # Cancelled by player
    EXPIRED = "expired"      # Expired without response


class BattleType(str, PyEnum):
    """Type of battle."""
    FRIENDLY = "friendly"    # No rewards/losses
    RANKED = "ranked"        # Affects rating
    BETTING = "betting"      # Players bet coins
    TOURNAMENT = "tournament"  # Part of tournament
    GUILD = "guild"          # Guild vs guild


class BattleMoveType(str, PyEnum):
    """Types of battle moves."""
    ATTACK = "attack"
    DEFEND = "defend"
    HEAL = "heal"
    BUFF_ATTACK = "buff_attack"
    BUFF_DEFENSE = "buff_defense"
    BUFF_SPEED = "buff_speed"
    SPECIAL = "special"
    SKIP = "skip"


class Battle(Base):
    """PvP battle between two pets."""
    
    __tablename__ = "battles"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Battle type
    battle_type: Mapped[BattleType] = mapped_column(
        Enum(BattleType), default=BattleType.FRIENDLY, nullable=False
    )
    
    # Player 1 (initiator)
    player1_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    pet1_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False
    )
    
    # Player 2 (opponent)
    player2_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    pet2_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False
    )
    
    # Status
    status: Mapped[BattleStatus] = mapped_column(
        Enum(BattleStatus), default=BattleStatus.PENDING, nullable=False
    )
    
    # Current state
    current_turn: Mapped[int] = mapped_column(default=1, nullable=False)  # 1 or 2
    turn_number: Mapped[int] = mapped_column(default=1, nullable=False)
    time_limit_seconds: Mapped[int] = mapped_column(default=30, nullable=False)
    turn_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # HP tracking
    pet1_current_hp: Mapped[int] = mapped_column(nullable=True)
    pet2_current_hp: Mapped[int] = mapped_column(nullable=True)
    
    # Buffs/debuffs
    pet1_buffs: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    pet2_buffs: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Battle log
    battle_log: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    
    # Winner
    winner_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    winner_pet_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("pets.id", ondelete="SET NULL"), nullable=True
    )
    
    # Betting
    bet_amount: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Rewards
    exp_reward: Mapped[int] = mapped_column(default=0, nullable=False)
    coin_reward: Mapped[int] = mapped_column(default=0, nullable=False)
    arena_token_reward: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Rating changes (for ranked battles)
    player1_rating_change: Mapped[int] = mapped_column(default=0, nullable=False)
    player2_rating_change: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    player1: Mapped["User"] = relationship(
        "User", foreign_keys=[player1_id], back_populates="battles_as_player1", lazy="selectin"
    )
    player2: Mapped["User"] = relationship(
        "User", foreign_keys=[player2_id], back_populates="battles_as_player2", lazy="selectin"
    )
    pet1: Mapped["Pet"] = relationship(
        "Pet", foreign_keys=[pet1_id], back_populates="battles_as_pet1", lazy="selectin"
    )
    pet2: Mapped["Pet"] = relationship(
        "Pet", foreign_keys=[pet2_id], back_populates="battles_as_pet2", lazy="selectin"
    )
    winner: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[winner_id], lazy="selectin"
    )
    moves: Mapped[List["BattleMove"]] = relationship(
        "BattleMove", back_populates="battle", lazy="selectin", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Battle(id={self.id}, p1={self.player1_id}, p2={self.player2_id}, status={self.status})>"
    
    def start(self) -> None:
        """Start the battle."""
        self.status = BattleStatus.ACTIVE
        self.started_at = datetime.utcnow()
        self.turn_deadline = datetime.utcnow() + __import__("datetime").timedelta(
            seconds=self.time_limit_seconds
        )
        
        # Initialize HP
        if self.pet1:
            self.pet1_current_hp = self.pet1.max_hp
        if self.pet2:
            self.pet2_current_hp = self.pet2.max_hp
    
    def finish(self, winner_id: Optional[int] = None) -> None:
        """Finish the battle."""
        self.status = BattleStatus.FINISHED
        self.finished_at = datetime.utcnow()
        self.winner_id = winner_id
        
        if winner_id == self.player1_id:
            self.winner_pet_id = self.pet1_id
        elif winner_id == self.player2_id:
            self.winner_pet_id = self.pet2_id
    
    def switch_turn(self) -> None:
        """Switch to next player's turn."""
        self.current_turn = 2 if self.current_turn == 1 else 1
        self.turn_number += 1
        self.turn_deadline = datetime.utcnow() + __import__("datetime").timedelta(
            seconds=self.time_limit_seconds
        )
    
    def add_log_entry(self, entry: Dict[str, Any]) -> None:
        """Add entry to battle log."""
        entry["turn"] = self.turn_number
        entry["timestamp"] = datetime.utcnow().isoformat()
        self.battle_log.append(entry)
    
    def calculate_damage(
        self,
        attacker_pet: "Pet",
        defender_pet: "Pet",
        move_type: BattleMoveType,
        is_player1: bool
    ) -> Dict[str, Any]:
        """Calculate damage for a move."""
        import random
        
        result = {
            "damage": 0,
            "is_critical": False,
            "is_miss": False,
            "heal": 0,
            "buffs": {},
        }
        
        # Get current buffs
        attacker_buffs = self.pet1_buffs if is_player1 else self.pet2_buffs
        
        if move_type == BattleMoveType.ATTACK:
            base_damage = attacker_pet.attack
            
            # Apply attack buff
            if "attack" in attacker_buffs:
                base_damage = int(base_damage * (1 + attacker_buffs["attack"] / 100))
            
            # Defense reduction
            defense = defender_pet.defense
            defender_buffs = self.pet2_buffs if is_player1 else self.pet1_buffs
            if "defense" in defender_buffs:
                defense = int(defense * (1 + defender_buffs["defense"] / 100))
            
            damage = max(1, base_damage - defense // 4)
            
            # Critical hit (10% chance)
            if random.random() < 0.1:
                damage = int(damage * 1.5)
                result["is_critical"] = True
            
            # Miss chance (5%)
            if random.random() < 0.05:
                damage = 0
                result["is_miss"] = True
            
            result["damage"] = damage
        
        elif move_type == BattleMoveType.HEAL:
            result["heal"] = attacker_pet.max_hp // 4
        
        elif move_type == BattleMoveType.BUFF_ATTACK:
            result["buffs"]["attack"] = 20
        
        elif move_type == BattleMoveType.BUFF_DEFENSE:
            result["buffs"]["defense"] = 20
        
        elif move_type == BattleMoveType.BUFF_SPEED:
            result["buffs"]["speed"] = 20
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert battle to dictionary."""
        return {
            "id": self.id,
            "battle_type": self.battle_type.value,
            "status": self.status.value,
            "player1": {
                "user": self.player1.to_dict() if self.player1 else None,
                "pet": self.pet1.to_dict() if self.pet1 else None,
                "current_hp": self.pet1_current_hp,
                "buffs": self.pet1_buffs,
            },
            "player2": {
                "user": self.player2.to_dict() if self.player2 else None,
                "pet": self.pet2.to_dict() if self.pet2 else None,
                "current_hp": self.pet2_current_hp,
                "buffs": self.pet2_buffs,
            },
            "current_turn": self.current_turn,
            "turn_number": self.turn_number,
            "turn_deadline": self.turn_deadline.isoformat() if self.turn_deadline else None,
            "winner_id": self.winner_id,
            "bet_amount": self.bet_amount,
            "rewards": {
                "exp": self.exp_reward,
                "coins": self.coin_reward,
                "arena_tokens": self.arena_token_reward,
            },
            "battle_log": self.battle_log,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
        }


class BattleMove(Base):
    """Individual move in a battle."""
    
    __tablename__ = "battle_moves"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Battle reference
    battle_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("battles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Move details
    turn_number: Mapped[int] = mapped_column(nullable=False)
    player_number: Mapped[int] = mapped_column(nullable=False)  # 1 or 2
    move_type: Mapped[BattleMoveType] = mapped_column(Enum(BattleMoveType), nullable=False)
    
    # Results
    damage_dealt: Mapped[int] = mapped_column(default=0, nullable=False)
    healing_done: Mapped[int] = mapped_column(default=0, nullable=False)
    is_critical: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_miss: Mapped[bool] = mapped_column(default=False, nullable=False)
    
    # State after move
    pet1_hp_after: Mapped[int] = mapped_column(nullable=False)
    pet2_hp_after: Mapped[int] = mapped_column(nullable=False)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    # Relationships
    battle: Mapped["Battle"] = relationship("Battle", back_populates="moves", lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<BattleMove(id={self.id}, battle={self.battle_id}, turn={self.turn_number})>"
