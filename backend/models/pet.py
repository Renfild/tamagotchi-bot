"""
Pet model for virtual pets.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List, Dict, Any
from enum import Enum as PyEnum

from sqlalchemy import (
    BigInteger,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    Enum,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from core.database import Base

if TYPE_CHECKING:
    from models.user import User
    from models.breeding import BreedingRequest
    from models.battle import Battle


class PetType(str, PyEnum):
    """Types of pets available."""
    CAT = "cat"
    DOG = "dog"
    RABBIT = "rabbit"
    FOX = "fox"
    DRAGON = "dragon"
    UNICORN = "unicorn"
    PHOENIX = "phoenix"
    ROBOT = "robot"
    SLIME = "slime"
    CUSTOM = "custom"


class Rarity(str, PyEnum):
    """Pet rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class Personality(str, PyEnum):
    """Pet personality types affecting behavior."""
    PLAYFUL = "playful"      # +happiness from games, -energy faster
    LAZY = "lazy"            # +energy recovery, -happiness from activity
    AGGRESSIVE = "aggressive"  # +attack in battles, -happiness from petting
    AFFECTIONATE = "affectionate"  # +happiness from petting, +bonding
    MYSTERIOUS = "mysterious"  # Random bonuses, unpredictable
    BRAVE = "brave"          # +defense in battles, recovers faster from illness
    CLEVER = "clever"        # +exp from games, learns skills faster
    GREEDY = "greedy"        # Finds more coins, eats more food


class EvolutionStage(str, PyEnum):
    """Evolution stages of pets."""
    BABY = "baby"
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"
    ELITE = "elite"
    MASTER = "master"


class PetStatus(str, PyEnum):
    """Current status of pet."""
    ACTIVE = "active"
    SLEEPING = "sleeping"
    SICK = "sick"
    DEPRESSED = "depressed"
    RUNAWAY = "runaway"
    DECEASED = "deceased"
    IN_STORAGE = "in_storage"


class Pet(Base):
    """Virtual pet model."""
    
    __tablename__ = "pets"
    
    # Primary key
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    # Owner
    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    
    # Basic info
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    pet_type: Mapped[PetType] = mapped_column(Enum(PetType), nullable=False, index=True)
    rarity: Mapped[Rarity] = mapped_column(Enum(Rarity), default=Rarity.COMMON, nullable=False)
    personality: Mapped[Personality] = mapped_column(
        Enum(Personality), default=Personality.PLAYFUL, nullable=False
    )
    
    # Evolution
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    experience: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    evolution_stage: Mapped[EvolutionStage] = mapped_column(
        Enum(EvolutionStage), default=EvolutionStage.BABY, nullable=False
    )
    evolution_branch: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    
    # Stats (0-100 scale)
    hunger: Mapped[int] = mapped_column(Integer, default=80, nullable=False)
    happiness: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    health: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    energy: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    hygiene: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    
    # Battle stats
    attack: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    defense: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    speed: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    max_hp: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    
    # Status
    status: Mapped[PetStatus] = mapped_column(
        Enum(PetStatus), default=PetStatus.ACTIVE, nullable=False, index=True
    )
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Appearance
    primary_color: Mapped[str] = mapped_column(String(7), default="#FF6B6B", nullable=False)  # Hex color
    secondary_color: Mapped[str] = mapped_column(String(7), default="#4ECDC4", nullable=False)
    eye_color: Mapped[str] = mapped_column(String(7), default="#000000", nullable=False)
    pattern: Mapped[str] = mapped_column(String(32), default="solid", nullable=False)
    accessories: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    # Images
    image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    animation_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Custom description for AI-generated pets
    custom_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timers
    sleep_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_fed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_played_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_petted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    breeding_cooldown_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    born_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="pets", lazy="selectin")
    breeding_requests_sent: Mapped[List["BreedingRequest"]] = relationship(
        "BreedingRequest",
        foreign_keys="BreedingRequest.pet1_id",
        back_populates="pet1",
        lazy="selectin",
    )
    breeding_requests_received: Mapped[List["BreedingRequest"]] = relationship(
        "BreedingRequest",
        foreign_keys="BreedingRequest.pet2_id",
        back_populates="pet2",
        lazy="selectin",
    )
    battles_as_pet1: Mapped[List["Battle"]] = relationship(
        "Battle",
        foreign_keys="Battle.pet1_id",
        back_populates="pet1",
        lazy="selectin",
    )
    battles_as_pet2: Mapped[List["Battle"]] = relationship(
        "Battle",
        foreign_keys="Battle.pet2_id",
        back_populates="pet2",
        lazy="selectin",
    )
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_pets_owner_status", "owner_id", "status"),
        Index("idx_pets_level", "level"),
        Index("idx_pets_rarity", "rarity"),
    )
    
    def __repr__(self) -> str:
        return f"<Pet(id={self.id}, name={self.name}, type={self.pet_type}, level={self.level})>"
    
    @property
    def is_alive(self) -> bool:
        """Check if pet is alive."""
        return self.status not in [PetStatus.DECEASED, PetStatus.RUNAWAY]
    
    @property
    def can_battle(self) -> bool:
        """Check if pet can participate in battles."""
        return (
            self.is_alive
            and self.status != PetStatus.SLEEPING
            and self.energy >= 20
            and self.health >= 30
        )
    
    @property
    def can_breed(self) -> bool:
        """Check if pet can breed."""
        if not self.is_alive or self.status == PetStatus.SLEEPING:
            return False
        if self.level < 10:  # Minimum level for breeding
            return False
        if self.breeding_cooldown_until and self.breeding_cooldown_until > datetime.utcnow():
            return False
        return True
    
    @property
    def age_days(self) -> int:
        """Calculate pet age in days."""
        return (datetime.utcnow() - self.born_at).days
    
    @property
    def exp_to_next_level(self) -> int:
        """Calculate experience needed for next level."""
        return int(100 * (self.level ** 1.5))
    
    @property
    def exp_progress_percent(self) -> float:
        """Calculate experience progress percentage."""
        needed = self.exp_to_next_level
        if needed == 0:
            return 100.0
        return min(100.0, (self.experience / needed) * 100)
    
    @property
    def overall_happiness(self) -> int:
        """Calculate overall happiness score."""
        weights = {
            "hunger": 0.25,
            "happiness": 0.25,
            "health": 0.20,
            "energy": 0.15,
            "hygiene": 0.15,
        }
        score = (
            self.hunger * weights["hunger"] +
            self.happiness * weights["happiness"] +
            self.health * weights["health"] +
            self.energy * weights["energy"] +
            self.hygiene * weights["hygiene"]
        )
        return int(score)
    
    def feed(self, food_value: int = 20) -> None:
        """Feed the pet."""
        self.hunger = min(100, self.hunger + food_value)
        self.last_fed_at = datetime.utcnow()
        self.add_experience(5)
    
    def play(self, fun_value: int = 15, energy_cost: int = 10) -> bool:
        """Play with pet. Returns False if not enough energy."""
        if self.energy < energy_cost:
            return False
        self.happiness = min(100, self.happiness + fun_value)
        self.energy -= energy_cost
        self.last_played_at = datetime.utcnow()
        self.add_experience(10)
        return True
    
    def pet(self) -> None:
        """Pet the pet (increases happiness)."""
        bonus = 3 if self.personality == Personality.AFFECTIONATE else 2
        self.happiness = min(100, self.happiness + bonus)
        self.last_petted_at = datetime.utcnow()
    
    def sleep(self, hours: int = 4) -> None:
        """Put pet to sleep."""
        self.status = PetStatus.SLEEPING
        self.sleep_until = datetime.utcnow() + __import__("datetime").timedelta(hours=hours)
    
    def wake_up(self) -> None:
        """Wake up the pet."""
        self.status = PetStatus.ACTIVE
        self.sleep_until = None
        self.energy = min(100, self.energy + 30)
    
    def heal(self, amount: int = 20) -> None:
        """Heal the pet."""
        self.health = min(100, self.health + amount)
        if self.health > 50 and self.status == PetStatus.SICK:
            self.status = PetStatus.ACTIVE
    
    def add_experience(self, amount: int) -> bool:
        """Add experience and check for level up. Returns True if leveled up."""
        self.experience += amount
        leveled_up = False
        
        while self.experience >= self.exp_to_next_level:
            self.experience -= self.exp_to_next_level
            self.level_up()
            leveled_up = True
        
        return leveled_up
    
    def level_up(self) -> None:
        """Level up the pet."""
        self.level += 1
        
        # Increase stats
        self.attack += self._get_stat_growth()
        self.defense += self._get_stat_growth()
        self.speed += self._get_stat_growth()
        self.max_hp += self._get_stat_growth() * 2
        
        # Check evolution
        self._check_evolution()
    
    def _get_stat_growth(self) -> int:
        """Calculate stat growth on level up based on rarity."""
        growth_map = {
            Rarity.COMMON: 1,
            Rarity.UNCOMMON: 1,
            Rarity.RARE: 2,
            Rarity.EPIC: 2,
            Rarity.LEGENDARY: 3,
            Rarity.MYTHIC: 4,
        }
        return growth_map.get(self.rarity, 1)
    
    def _check_evolution(self) -> None:
        """Check and apply evolution based on level."""
        evolution_levels = {
            10: EvolutionStage.CHILD,
            25: EvolutionStage.TEEN,
            50: EvolutionStage.ADULT,
            100: EvolutionStage.ELITE,
        }
        
        for level, stage in evolution_levels.items():
            if self.level >= level and self.evolution_stage.value < stage.value:
                self.evolution_stage = stage
                break
    
    def apply_decay(self, hours: int = 1) -> List[str]:
        """Apply stat decay over time. Returns list of status changes."""
        from core.config import settings
        
        changes = []
        
        # Hunger decay
        hunger_decay = settings.HUNGER_DECAY_PER_HOUR * hours
        self.hunger = max(0, self.hunger - hunger_decay)
        
        if self.hunger < 20:
            changes.append("critical_hunger")
        elif self.hunger < 50:
            changes.append("hungry")
        
        # Happiness decay
        happiness_decay = settings.HAPPINESS_DECAY_PER_HOUR * hours
        if self.personality == Personality.PLAYFUL:
            happiness_decay *= 1.2
        elif self.personality == Personality.LAZY:
            happiness_decay *= 0.8
        
        self.happiness = max(0, self.happiness - int(happiness_decay))
        
        if self.happiness < 20:
            self.status = PetStatus.DEPRESSED
            changes.append("depressed")
        
        # Energy recovery during sleep
        if self.status == PetStatus.SLEEPING:
            energy_recovery = settings.ENERGY_RECOVERY_PER_HOUR * hours * 2
            self.energy = min(100, self.energy + energy_recovery)
        else:
            self.energy = max(0, self.energy - 2 * hours)
        
        # Health effects
        if self.hunger < 10 or self.hygiene < 10:
            self.health = max(0, self.health - 5 * hours)
            if self.health < 30 and self.status != PetStatus.SICK:
                self.status = PetStatus.SICK
                changes.append("sick")
        
        # Critical condition
        if self.hunger == 0 and self.health == 0:
            if self.status != PetStatus.DECEASED:
                # Chance to run away instead of dying
                import random
                if random.random() < 0.5:
                    self.status = PetStatus.RUNAWAY
                    changes.append("runaway")
                else:
                    self.status = PetStatus.DECEASED
                    changes.append("deceased")
        
        return changes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pet to dictionary for API response."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.pet_type.value,
            "rarity": self.rarity.value,
            "personality": self.personality.value,
            "level": self.level,
            "experience": self.experience,
            "exp_to_next_level": self.exp_to_next_level,
            "exp_progress_percent": self.exp_progress_percent,
            "evolution_stage": self.evolution_stage.value,
            "evolution_branch": self.evolution_branch,
            "stats": {
                "hunger": self.hunger,
                "happiness": self.happiness,
                "health": self.health,
                "energy": self.energy,
                "hygiene": self.hygiene,
            },
            "battle_stats": {
                "attack": self.attack,
                "defense": self.defense,
                "speed": self.speed,
                "max_hp": self.max_hp,
            },
            "status": self.status.value,
            "is_favorite": self.is_favorite,
            "appearance": {
                "primary_color": self.primary_color,
                "secondary_color": self.secondary_color,
                "eye_color": self.eye_color,
                "pattern": self.pattern,
                "accessories": self.accessories,
            },
            "images": {
                "full": self.image_url,
                "thumbnail": self.thumbnail_url,
            },
            "age_days": self.age_days,
            "can_battle": self.can_battle,
            "can_breed": self.can_breed,
            "is_alive": self.is_alive,
        }
