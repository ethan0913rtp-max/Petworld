from datetime import datetime, timedelta

SPECIES = {
    "dragon": {
        "emoji": "🐉",
        "description": "A fierce fire-breathing dragon. High attack, but needs more food.",
        "xp_mult": 1.2,
        "hunger_rate": 1.4,
    },
    "bunny": {
        "emoji": "🐰",
        "description": "An adorable fluffy bunny. Gains happiness easily.",
        "xp_mult": 1.0,
        "hunger_rate": 0.8,
    },
    "cat": {
        "emoji": "🐱",
        "description": "A sleek and mysterious cat. Balanced and independent.",
        "xp_mult": 1.1,
        "hunger_rate": 1.0,
    },
    "fox": {
        "emoji": "🦊",
        "description": "A cunning fox. Earns more coins from battles.",
        "xp_mult": 1.15,
        "hunger_rate": 1.1,
    },
    "penguin": {
        "emoji": "🐧",
        "description": "A cheerful penguin. Very resilient and hard to tire out.",
        "xp_mult": 0.9,
        "hunger_rate": 0.9,
    },
    "wolf": {
        "emoji": "🐺",
        "description": "A loyal wolf. Trains faster than any other pet.",
        "xp_mult": 1.3,
        "hunger_rate": 1.3,
    },
}

XP_PER_LEVEL = 100

SHOP_ITEMS = {
    "apple": {"cost": 10, "emoji": "🍎", "description": "Restores 20 hunger", "hunger": 20},
    "feast": {"cost": 30, "emoji": "🍖", "description": "Restores 50 hunger", "hunger": 50},
    "toy": {"cost": 20, "emoji": "🧸", "description": "Restores 25 happiness", "happiness": 25},
    "potion": {"cost": 40, "emoji": "🧪", "description": "Restores 30 health", "health": 30},
    "energy_drink": {"cost": 25, "emoji": "⚡", "description": "Restores 40 energy", "energy": 40},
}

BATTLE_REWARDS = {
    "win": {"coins": 30, "xp": 40},
    "lose": {"coins": 5, "xp": 10},
    "draw": {"coins": 15, "xp": 20},
}

def clamp(val, lo=0, hi=100):
    return max(lo, min(hi, val))

def hours_since(iso_str: str) -> float:
    if not iso_str:
        return 0.0
    try:
        dt = datetime.fromisoformat(iso_str)
        return (datetime.utcnow() - dt).total_seconds() / 3600
    except Exception:
        return 0.0

def apply_time_decay(pet: dict) -> dict:
    """Reduce pet stats based on time elapsed since last actions."""
    pet = dict(pet)
    hours_hungry = hours_since(pet.get("last_fed"))
    hours_bored = hours_since(pet.get("last_played"))
    hours_tired = hours_since(pet.get("last_rested"))

    species_info = SPECIES.get(pet.get("species", "cat"), SPECIES["cat"])
    hunger_rate = species_info["hunger_rate"]

    hunger_loss = int(hours_hungry * 5 * hunger_rate)
    happiness_loss = int(hours_bored * 4)
    energy_loss = int(hours_tired * 3)

    pet["hunger"] = clamp(pet["hunger"] - hunger_loss)
    pet["happiness"] = clamp(pet["happiness"] - happiness_loss)
    pet["energy"] = clamp(pet["energy"] - energy_loss)

    if pet["hunger"] == 0:
        pet["health"] = clamp(pet["health"] - int(hours_hungry * 2))

    return pet

def xp_for_next_level(level: int) -> int:
    return XP_PER_LEVEL * level

def check_level_up(pet: dict):
    """Returns (new_level, leveled_up)"""
    level = pet["level"]
    xp = pet["xp"]
    needed = xp_for_next_level(level)
    if xp >= needed:
        return level + 1, True
    return level, False

def pet_status_bar(value: int, width: int = 10) -> str:
    filled = int(value / 100 * width)
    bar = "█" * filled + "░" * (width - filled)
    color = "🟢" if value >= 60 else ("🟡" if value >= 30 else "🔴")
    return f"{color} [{bar}] {value}%"

def get_species_emoji(species: str) -> str:
    return SPECIES.get(species, {}).get("emoji", "🐾")

def battle_score(pet: dict) -> int:
    level = pet.get("level", 1)
    health = pet.get("health", 100)
    happiness = pet.get("happiness", 100)
    return level * 20 + health // 5 + happiness // 10
