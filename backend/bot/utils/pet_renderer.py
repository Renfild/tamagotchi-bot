"""
Pet status rendering utilities.
"""
from models.pet import Pet, PetStatus


def get_status_emoji(status: PetStatus) -> str:
    """Get emoji for pet status."""
    return {
        PetStatus.ACTIVE: "😊",
        PetStatus.SLEEPING: "😴",
        PetStatus.SICK: "🤒",
        PetStatus.DEPRESSED: "😢",
        PetStatus.RUNAWAY: "🏃",
        PetStatus.DECEASED: "💀",
        PetStatus.IN_STORAGE: "📦",
    }.get(status, "😐")


def get_rarity_emoji(rarity: str) -> str:
    """Get emoji for rarity."""
    return {
        "common": "⚪",
        "uncommon": "🟢",
        "rare": "🔵",
        "epic": "🟣",
        "legendary": "🟡",
        "mythic": "🔴",
    }.get(rarity.lower(), "⚪")


def get_progress_bar(value: int, max_value: int = 100, length: int = 10) -> str:
    """Generate a progress bar."""
    filled = int((value / max_value) * length)
    empty = length - filled
    
    # Color based on value
    if value >= 70:
        bar = "🟩" * filled + "⬜" * empty
    elif value >= 40:
        bar = "🟨" * filled + "⬜" * empty
    else:
        bar = "🟥" * filled + "⬜" * empty
    
    return bar


async def render_pet_status(pet: Pet, _) -> str:
    """Render pet status text."""
    status_emoji = get_status_emoji(pet.status)
    rarity_emoji = get_rarity_emoji(pet.rarity.value)
    
    text = f"{status_emoji} <b>{pet.name}</b> {rarity_emoji}\n"
    text += f"📈 Уровень {pet.level} | {pet.evolution_stage.value.title()}\n\n"
    
    # Stats with progress bars
    text += f"🍖 {_('hunger')}: {get_progress_bar(pet.hunger)} {pet.hunger}%\n"
    text += f"😊 {_('happiness')}: {get_progress_bar(pet.happiness)} {pet.happiness}%\n"
    text += f"❤️ {_('health')}: {get_progress_bar(pet.health)} {pet.health}%\n"
    text += f"⚡ {_('energy')}: {get_progress_bar(pet.energy)} {pet.energy}%\n"
    text += f"🧼 Гигиена: {get_progress_bar(pet.hygiene)} {pet.hygiene}%\n\n"
    
    # Experience
    exp_percent = pet.exp_progress_percent
    text += f"⭐ Опыт: {pet.experience}/{pet.exp_to_next_level} ({exp_percent:.1f}%)\n"
    text += f"{get_progress_bar(int(exp_percent))}\n\n"
    
    # Battle stats
    text += f"⚔️ Атака: {pet.attack} | 🛡️ Защита: {pet.defense} | 💨 Скорость: {pet.speed}\n\n"
    
    # Status warnings
    warnings = []
    if pet.hunger < 30:
        warnings.append("⚠️ Голоден!")
    if pet.happiness < 30:
        warnings.append("⚠️ Грустит!")
    if pet.health < 50:
        warnings.append("⚠️ Болеет!")
    if pet.energy < 20:
        warnings.append("⚠️ Устал!")
    
    if warnings:
        text += "\n".join(warnings)
    elif pet.happiness > 80 and pet.hunger > 80:
        text += "✨ Питомец счастлив и доволен!"
    
    return text


def get_personality_description(personality: str) -> str:
    """Get description for personality type."""
    descriptions = {
        "playful": "🎮 Игривый - любит игры, быстро тратит энергию",
        "lazy": "😴 Ленивый - медленно восстанавливается, но экономит энергию",
        "aggressive": "😠 Агрессивный - силен в боях, но не любит ласку",
        "affectionate": "🥰 Ласковый - обожает внимание, быстро привязывается",
        "mysterious": "🌙 Загадочный - непредсказуем, дает случайные бонусы",
        "brave": "🦁 Храбрый - отлично защищается, быстро выздоравливает",
        "clever": "🧠 Умный - быстрее учится, получает больше опыта",
        "greedy": "🍖 Жадный - находит больше монет, но ест больше",
    }
    return descriptions.get(personality.lower(), "Обычный характер")
