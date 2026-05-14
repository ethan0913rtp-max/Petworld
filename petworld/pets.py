from datetime import datetime, timedelta

# ── Species ─────────────────────────────────────────────────────────────────
# category: mammals | birds | reptiles | fish | insects | amphibians | mythical
# is_mammal: True  → hatches immediately (no egg phase)
# is_bird:   True  → unlocks /fly command
# rarity: common | uncommon | rare | legendary
# element: Fire | Water | Earth | Lightning | Shadow | Ice | Wind | Lava

SPECIES = {
    # ── MAMMALS (no egg) ────────────────────────────────────────────────────
    "cat":       {"emoji":"🐱","category":"mammals","is_mammal":True,"is_bird":False,"element":"Shadow","rarity":"common","xp_mult":1.1,"hunger_rate":1.0,"description":"A sleek, mysterious cat. Balanced all-rounder."},
    "dog":       {"emoji":"🐶","category":"mammals","is_mammal":True,"is_bird":False,"element":"Wind","rarity":"common","xp_mult":1.0,"hunger_rate":1.0,"description":"A loyal and energetic companion. Loves to play!"},
    "bunny":     {"emoji":"🐰","category":"mammals","is_mammal":True,"is_bird":False,"element":"Wind","rarity":"common","xp_mult":1.0,"hunger_rate":0.8,"description":"Fluffy and cheerful. Gains happiness very easily."},
    "hamster":   {"emoji":"🐹","category":"mammals","is_mammal":True,"is_bird":False,"element":"Earth","rarity":"common","xp_mult":0.9,"hunger_rate":0.7,"description":"Tiny but mighty. Doesn't need much food."},
    "fox":       {"emoji":"🦊","category":"mammals","is_mammal":True,"is_bird":False,"element":"Fire","rarity":"uncommon","xp_mult":1.15,"hunger_rate":1.1,"description":"Cunning and clever. Earns bonus coins in battle."},
    "wolf":      {"emoji":"🐺","category":"mammals","is_mammal":True,"is_bird":False,"element":"Shadow","rarity":"uncommon","xp_mult":1.3,"hunger_rate":1.3,"description":"A fierce wolf. Trains faster than any other pet."},
    "raccoon":   {"emoji":"🦝","category":"mammals","is_mammal":True,"is_bird":False,"element":"Shadow","rarity":"uncommon","xp_mult":1.05,"hunger_rate":1.0,"description":"A clever scavenger that always finds treasure."},
    "deer":      {"emoji":"🦌","category":"mammals","is_mammal":True,"is_bird":False,"element":"Wind","rarity":"uncommon","xp_mult":0.95,"hunger_rate":0.9,"description":"Graceful and swift. Hard to hit in battle."},
    "panda":     {"emoji":"🐼","category":"mammals","is_mammal":True,"is_bird":False,"element":"Earth","rarity":"uncommon","xp_mult":0.9,"hunger_rate":1.1,"description":"Peaceful and sturdy. High defence in battle."},
    "koala":     {"emoji":"🐨","category":"mammals","is_mammal":True,"is_bird":False,"element":"Earth","rarity":"uncommon","xp_mult":0.85,"hunger_rate":0.8,"description":"Sleepy but resilient. Recovers energy very fast."},
    "bear":      {"emoji":"🐻","category":"mammals","is_mammal":True,"is_bird":False,"element":"Earth","rarity":"rare","xp_mult":1.2,"hunger_rate":1.3,"description":"Massive and powerful. Huge battle damage output."},
    "tiger":     {"emoji":"🐯","category":"mammals","is_mammal":True,"is_bird":False,"element":"Fire","rarity":"rare","xp_mult":1.25,"hunger_rate":1.3,"description":"Ferocious hunter. Deals devastating battle strikes."},
    "lion":      {"emoji":"🦁","category":"mammals","is_mammal":True,"is_bird":False,"element":"Fire","rarity":"rare","xp_mult":1.2,"hunger_rate":1.2,"description":"The king of beasts. Commands respect everywhere."},
    "elephant":  {"emoji":"🐘","category":"mammals","is_mammal":True,"is_bird":False,"element":"Earth","rarity":"rare","xp_mult":1.0,"hunger_rate":1.4,"description":"Wise and ancient. Very high HP in battle."},
    "unicorn":   {"emoji":"🦄","category":"mythical","is_mammal":True,"is_bird":False,"element":"Ice","rarity":"legendary","xp_mult":1.4,"hunger_rate":0.9,"description":"A radiant magical horse. Heals allies and soothes foes."},
    "cerberus":  {"emoji":"🐕","category":"mythical","is_mammal":True,"is_bird":False,"element":"Shadow","rarity":"legendary","xp_mult":1.45,"hunger_rate":1.5,"description":"The three-headed guardian of the underworld. Terrifying."},
    "kitsune":   {"emoji":"🦊","category":"mythical","is_mammal":True,"is_bird":False,"element":"Fire","rarity":"legendary","xp_mult":1.5,"hunger_rate":1.1,"description":"A nine-tailed fox spirit with ancient magical powers."},
    "kirin":     {"emoji":"🦒","category":"mythical","is_mammal":True,"is_bird":False,"element":"Lightning","rarity":"legendary","xp_mult":1.4,"hunger_rate":1.0,"description":"A divine chimeric beast that appears at auspicious times."},

    # ── BIRDS (egg, unlocks /fly) ────────────────────────────────────────────
    "parrot":    {"emoji":"🦜","category":"birds","is_mammal":False,"is_bird":True,"element":"Wind","rarity":"common","xp_mult":1.0,"hunger_rate":0.9,"description":"Colourful and chatty. Mimics enemies to confuse them."},
    "penguin":   {"emoji":"🐧","category":"birds","is_mammal":False,"is_bird":True,"element":"Ice","rarity":"common","xp_mult":0.9,"hunger_rate":0.9,"description":"Cheerful and resilient. Slow to tire out."},
    "crow":      {"emoji":"🐦‍⬛","category":"birds","is_mammal":False,"is_bird":True,"element":"Shadow","rarity":"uncommon","xp_mult":1.1,"hunger_rate":1.0,"description":"Ominous and intelligent. Finds hidden coins on walks."},
    "owl":       {"emoji":"🦉","category":"birds","is_mammal":False,"is_bird":True,"element":"Shadow","rarity":"uncommon","xp_mult":1.15,"hunger_rate":0.9,"description":"Wise and nocturnal. Bonus XP gained during night hours."},
    "flamingo":  {"emoji":"🦩","category":"birds","is_mammal":False,"is_bird":True,"element":"Water","rarity":"uncommon","xp_mult":1.0,"hunger_rate":1.0,"description":"Elegant and striking. Wins style points in every battle."},
    "toucan":    {"emoji":"🦚","category":"birds","is_mammal":False,"is_bird":True,"element":"Wind","rarity":"uncommon","xp_mult":1.05,"hunger_rate":1.0,"description":"Vibrant and exotic. Its beak packs a surprising punch."},
    "peacock":   {"emoji":"🦚","category":"birds","is_mammal":False,"is_bird":True,"element":"Wind","rarity":"rare","xp_mult":1.1,"hunger_rate":1.1,"description":"Breathtakingly beautiful. High happiness boosts battle power."},
    "eagle":     {"emoji":"🦅","category":"birds","is_mammal":False,"is_bird":True,"element":"Wind","rarity":"rare","xp_mult":1.2,"hunger_rate":1.1,"description":"Sharp-eyed and fierce. Swoops from above for bonus damage."},
    "hummingbird":{"emoji":"🐦","category":"birds","is_mammal":False,"is_bird":True,"element":"Wind","rarity":"rare","xp_mult":1.1,"hunger_rate":1.2,"description":"Impossibly fast wings. Dodges attacks with ease."},
    "phoenix":   {"emoji":"🔥","category":"mythical","is_mammal":False,"is_bird":True,"element":"Fire","rarity":"legendary","xp_mult":1.5,"hunger_rate":1.2,"description":"A blazing immortal bird. Revives once per battle with 50% HP."},
    "griffin":   {"emoji":"🦅","category":"mythical","is_mammal":False,"is_bird":True,"element":"Wind","rarity":"legendary","xp_mult":1.45,"hunger_rate":1.3,"description":"Lion-eagle hybrid of royalty. Majestic and powerful."},

    # ── REPTILES (egg) ───────────────────────────────────────────────────────
    "dragon":    {"emoji":"🐉","category":"reptiles","is_mammal":False,"is_bird":False,"element":"Fire","rarity":"rare","xp_mult":1.2,"hunger_rate":1.4,"description":"A fire-breathing legend. High attack, very hungry."},
    "lizard":    {"emoji":"🦎","category":"reptiles","is_mammal":False,"is_bird":False,"element":"Earth","rarity":"common","xp_mult":0.95,"hunger_rate":0.9,"description":"Quick and adaptable. Blends into any environment."},
    "chameleon": {"emoji":"🦎","category":"reptiles","is_mammal":False,"is_bird":False,"element":"Shadow","rarity":"uncommon","xp_mult":1.05,"hunger_rate":0.9,"description":"Master of disguise. Evades first strike in every battle."},
    "turtle":    {"emoji":"🐢","category":"reptiles","is_mammal":False,"is_bird":False,"element":"Water","rarity":"uncommon","xp_mult":0.85,"hunger_rate":0.8,"description":"Slow but impenetrable. Takes reduced damage in all battles."},
    "snake":     {"emoji":"🐍","category":"reptiles","is_mammal":False,"is_bird":False,"element":"Shadow","rarity":"uncommon","xp_mult":1.1,"hunger_rate":1.0,"description":"Stealthy and venomous. Applies poison in battle."},
    "crocodile": {"emoji":"🐊","category":"reptiles","is_mammal":False,"is_bird":False,"element":"Water","rarity":"rare","xp_mult":1.2,"hunger_rate":1.3,"description":"Ancient apex predator. Terrifying bite force."},
    "hydra":     {"emoji":"🐉","category":"mythical","is_mammal":False,"is_bird":False,"element":"Water","rarity":"legendary","xp_mult":1.4,"hunger_rate":1.6,"description":"The many-headed sea serpent. Grows stronger as it takes damage."},

    # ── FISH / AQUATIC (egg) ─────────────────────────────────────────────────
    "koi":       {"emoji":"🐟","category":"fish","is_mammal":False,"is_bird":False,"element":"Water","rarity":"common","xp_mult":0.9,"hunger_rate":0.7,"description":"A serene ornamental fish. Brings its trainer good luck."},
    "clownfish": {"emoji":"🐠","category":"fish","is_mammal":False,"is_bird":False,"element":"Water","rarity":"common","xp_mult":0.95,"hunger_rate":0.8,"description":"Cheerful and bright. Boosts team happiness in battle."},
    "shark":     {"emoji":"🦈","category":"fish","is_mammal":False,"is_bird":False,"element":"Water","rarity":"rare","xp_mult":1.25,"hunger_rate":1.4,"description":"Apex ocean predator. Relentless in battle — never retreats."},
    "jellyfish": {"emoji":"🪼","category":"fish","is_mammal":False,"is_bird":False,"element":"Ice","rarity":"rare","xp_mult":1.0,"hunger_rate":0.6,"description":"Ethereal drifter. Stuns opponents with electric tendrils."},
    "axolotl":   {"emoji":"🦋","category":"fish","is_mammal":False,"is_bird":False,"element":"Water","rarity":"uncommon","xp_mult":1.0,"hunger_rate":0.8,"description":"Adorable regenerating amphibian. Slowly restores HP in battle."},

    # ── INSECTS (egg) ────────────────────────────────────────────────────────
    "butterfly": {"emoji":"🦋","category":"insects","is_mammal":False,"is_bird":False,"element":"Wind","rarity":"common","xp_mult":0.9,"hunger_rate":0.6,"description":"Delicate and beautiful. Boosts happiness by simply existing."},
    "firefly":   {"emoji":"✨","category":"insects","is_mammal":False,"is_bird":False,"element":"Lightning","rarity":"uncommon","xp_mult":1.0,"hunger_rate":0.7,"description":"Magical glowing bug. Lights the way in dark dungeons."},
    "bee":       {"emoji":"🐝","category":"insects","is_mammal":False,"is_bird":False,"element":"Wind","rarity":"uncommon","xp_mult":1.0,"hunger_rate":0.8,"description":"Hardworking and disciplined. Earns extra coins from /work."},
    "beetle":    {"emoji":"🪲","category":"insects","is_mammal":False,"is_bird":False,"element":"Earth","rarity":"uncommon","xp_mult":1.0,"hunger_rate":0.7,"description":"Armoured and resilient. Its shell deflects weak attacks."},

    # ── AMPHIBIANS (egg) ─────────────────────────────────────────────────────
    "frog":      {"emoji":"🐸","category":"amphibians","is_mammal":False,"is_bird":False,"element":"Water","rarity":"common","xp_mult":0.95,"hunger_rate":0.8,"description":"Leaping and lively. Its sticky tongue never misses a target."},
    "salamander":{"emoji":"🦎","category":"amphibians","is_mammal":False,"is_bird":False,"element":"Fire","rarity":"uncommon","xp_mult":1.05,"hunger_rate":0.9,"description":"A fire salamander with blazing skin. Scorches all who touch it."},
    "toad":      {"emoji":"🐸","category":"amphibians","is_mammal":False,"is_bird":False,"element":"Earth","rarity":"common","xp_mult":0.9,"hunger_rate":0.7,"description":"Grumpy and venomous. Poisons attackers who get too close."},

    # ── MYTHICAL EXTRA (egg) ─────────────────────────────────────────────────
    "sprite":    {"emoji":"🧚","category":"mythical","is_mammal":False,"is_bird":False,"element":"Lightning","rarity":"rare","xp_mult":1.3,"hunger_rate":0.8,"description":"A tiny magical fairy creature. Zaps foes with arcane sparks."},
    "leviathan": {"emoji":"🐉","category":"mythical","is_mammal":False,"is_bird":False,"element":"Lava","rarity":"legendary","xp_mult":1.6,"hunger_rate":1.8,"description":"An ancient sea monster of legend. Catastrophically powerful."},
    "thunderbird":{"emoji":"🦅","category":"mythical","is_mammal":False,"is_bird":True,"element":"Lightning","rarity":"legendary","xp_mult":1.5,"hunger_rate":1.3,"description":"A storm-god bird that calls down lightning with every wingbeat."},
}

# ── Element interactions ─────────────────────────────────────────────────────
# strong_against: attacker's element → list of elements it beats (1.5× damage)
# weak_against:   attacker's element → list of elements that beat it (0.5× damage)
ELEMENT_COLORS = {
    "Fire": "🔥", "Water": "💧", "Earth": "🌿", "Lightning": "⚡",
    "Shadow": "🌑", "Ice": "❄️", "Wind": "🌪️", "Lava": "🌋",
}

ELEMENT_STRONG_AGAINST = {
    "Fire":      ["Ice", "Wind"],
    "Water":     ["Fire", "Lava"],
    "Earth":     ["Lightning", "Fire"],
    "Lightning": ["Water", "Wind"],
    "Shadow":    ["Earth", "Ice"],
    "Ice":       ["Wind", "Water"],
    "Wind":      ["Lightning", "Shadow"],
    "Lava":      ["Ice", "Earth"],
}

def element_multiplier(attacker_elem: str, defender_elem: str) -> float:
    strong = ELEMENT_STRONG_AGAINST.get(attacker_elem, [])
    if defender_elem in strong:
        return 1.5
    # check reverse — if defender is strong against attacker
    defender_strong = ELEMENT_STRONG_AGAINST.get(defender_elem, [])
    if attacker_elem in defender_strong:
        return 0.65
    return 1.0

# ── Rarity ───────────────────────────────────────────────────────────────────
RARITY_ORDER = ["common", "uncommon", "rare", "legendary"]
RARITY_EMOJI = {"common": "⚪", "uncommon": "🟢", "rare": "🔵", "legendary": "🟡"}

# Offspring pool per parent-rarity combination (ordered by [p1, p2] sorted)
BREED_OFFSPRING_POOLS = {
    ("common", "common"):       (["common"] * 7) + (["uncommon"] * 3),
    ("common", "uncommon"):     (["uncommon"] * 6) + (["common"] * 2) + (["rare"] * 2),
    ("common", "rare"):         (["uncommon"] * 5) + (["rare"] * 4) + (["legendary"] * 1),
    ("common", "legendary"):    (["rare"] * 5) + (["uncommon"] * 3) + (["legendary"] * 2),
    ("uncommon", "uncommon"):   (["uncommon"] * 6) + (["rare"] * 3) + (["common"] * 1),
    ("uncommon", "rare"):       (["rare"] * 6) + (["uncommon"] * 3) + (["legendary"] * 1),
    ("uncommon", "legendary"):  (["rare"] * 5) + (["legendary"] * 4) + (["uncommon"] * 1),
    ("rare", "rare"):           (["rare"] * 5) + (["legendary"] * 4) + (["uncommon"] * 1),
    ("rare", "legendary"):      (["legendary"] * 6) + (["rare"] * 4),
    ("legendary", "legendary"): (["legendary"] * 9) + (["rare"] * 1),
}

def get_breed_rarity(r1: str, r2: str) -> str:
    import random
    key = tuple(sorted([r1, r2]))
    pool = BREED_OFFSPRING_POOLS.get(key, ["common"] * 10)
    return random.choice(pool)

def get_random_species_of_rarity(rarity: str, exclude_mammals: bool = False) -> str:
    import random
    candidates = [
        s for s, d in SPECIES.items()
        if d["rarity"] == rarity and (not exclude_mammals or not d["is_mammal"])
    ]
    if not candidates:
        candidates = [s for s, d in SPECIES.items() if d["rarity"] == rarity]
    if not candidates:
        candidates = list(SPECIES.keys())
    return random.choice(candidates)

# ── Shop ─────────────────────────────────────────────────────────────────────
SHOP_ITEMS = {
    # consumables
    "apple":        {"cost": 10,  "emoji": "🍎",  "type": "consumable", "description": "Restores 20 hunger",       "hunger":    20},
    "feast":        {"cost": 30,  "emoji": "🍖",  "type": "consumable", "description": "Restores 50 hunger",       "hunger":    50},
    "toy":          {"cost": 20,  "emoji": "🧸",  "type": "consumable", "description": "Restores 25 happiness",    "happiness": 25},
    "potion":       {"cost": 40,  "emoji": "🧪",  "type": "consumable", "description": "Restores 30 health",       "health":    30},
    "energy_drink": {"cost": 25,  "emoji": "⚡",  "type": "consumable", "description": "Restores 40 energy",       "energy":    40},
    "hatch_gem":    {"cost": 150, "emoji": "💎",  "type": "consumable", "description": "Instantly hatches an egg", "hatch":     True},
    # hats
    "top_hat":      {"cost": 80,  "emoji": "🎩",  "type": "hat",        "description": "A dapper top hat. Very classy."},
    "witch_hat":    {"cost": 90,  "emoji": "🧙",  "type": "hat",        "description": "A pointy witch's hat. Spooky!"},
    "crown":        {"cost": 200, "emoji": "👑",  "type": "hat",        "description": "A royal crown. Only for champions."},
    "party_hat":    {"cost": 50,  "emoji": "🎉",  "type": "hat",        "description": "A festive party hat. Let's celebrate!"},
    # outfits
    "cape":         {"cost": 100, "emoji": "🦸",  "type": "outfit",     "description": "A flowing hero's cape. Adds +5% battle score."},
    "armor":        {"cost": 180, "emoji": "🛡️",  "type": "outfit",     "description": "Heavy plate armor. Adds +10% battle score."},
    "scarf":        {"cost": 60,  "emoji": "🧣",  "type": "outfit",     "description": "A cozy knitted scarf. Slows energy decay."},
    "sweater":      {"cost": 55,  "emoji": "🧥",  "type": "outfit",     "description": "A warm sweater. Slows hunger decay."},
    # collars
    "gold_collar":  {"cost": 120, "emoji": "🏅",  "type": "collar",     "description": "A shiny gold collar. Boosts coin earnings."},
    "bow_collar":   {"cost": 45,  "emoji": "🎀",  "type": "collar",     "description": "An adorable bow collar. Boosts happiness gain."},
    # accessories
    "sunglasses":   {"cost": 70,  "emoji": "😎",  "type": "accessory",  "description": "Cool shades. Intimidates opponents in battle."},
    "ribbon":       {"cost": 40,  "emoji": "🎗️",  "type": "accessory",  "description": "A delicate ribbon. Looks adorable."},
    "wings":        {"cost": 220, "emoji": "🪽",  "type": "accessory",  "description": "Magical wings. Boosts /fly rewards for birds, too!"},
}

EQUIP_SLOTS = ["hat", "outfit", "collar", "accessory"]

OUTFIT_BATTLE_BONUS = {
    "cape":   0.05,
    "armor":  0.10,
}

COLLAR_COIN_BONUS = {
    "gold_collar": 0.20,
}

BATTLE_REWARDS = {
    "win":  {"coins": 30, "xp": 40},
    "lose": {"coins": 5,  "xp": 10},
    "draw": {"coins": 15, "xp": 20},
}

XP_PER_LEVEL = 100

# ── Helpers ───────────────────────────────────────────────────────────────────
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
    pet = dict(pet)
    if pet.get("is_egg"):
        return pet
    hours_hungry = hours_since(pet.get("last_fed"))
    hours_bored  = hours_since(pet.get("last_played"))
    hours_tired  = hours_since(pet.get("last_rested"))

    species_info = SPECIES.get(pet.get("species", "cat"), SPECIES["cat"])
    hr = species_info["hunger_rate"]

    # sweater slows hunger decay
    equip = pet.get("equipment") or {}
    if isinstance(equip, str):
        import json
        try:
            equip = json.loads(equip)
        except Exception:
            equip = {}

    hunger_rate_mod = 0.7 if equip.get("outfit") == "sweater" else 1.0
    energy_rate_mod = 0.7 if equip.get("outfit") == "scarf"   else 1.0

    pet["hunger"]    = clamp(pet["hunger"]    - int(hours_hungry * 5 * hr * hunger_rate_mod))
    pet["happiness"] = clamp(pet["happiness"] - int(hours_bored  * 4))
    pet["energy"]    = clamp(pet["energy"]    - int(hours_tired  * 3 * energy_rate_mod))

    if pet["hunger"] == 0:
        pet["health"] = clamp(pet["health"] - int(hours_hungry * 2))

    return pet

def xp_for_next_level(level: int) -> int:
    return XP_PER_LEVEL * level

def check_level_up(pet: dict):
    level = pet["level"]
    xp    = pet["xp"]
    if xp >= xp_for_next_level(level):
        return level + 1, True
    return level, False

def pet_status_bar(value: int, width: int = 10) -> str:
    filled = int(value / 100 * width)
    bar    = "█" * filled + "░" * (width - filled)
    color  = "🟢" if value >= 60 else ("🟡" if value >= 30 else "🔴")
    return f"{color} [{bar}] {value}%"

def get_species_emoji(species: str) -> str:
    return SPECIES.get(species, {}).get("emoji", "🐾")

def battle_score(pet: dict, equip: dict | None = None) -> int:
    level     = pet.get("level", 1)
    health    = pet.get("health", 100)
    happiness = pet.get("happiness", 100)
    base      = level * 20 + health // 5 + happiness // 10
    if equip:
        outfit = equip.get("outfit", "")
        bonus  = OUTFIT_BATTLE_BONUS.get(outfit, 0.0)
        acc    = equip.get("accessory", "")
        if acc == "sunglasses":
            bonus += 0.05
        base = int(base * (1 + bonus))
    return base

def egg_hours_remaining(created_at: str) -> float:
    elapsed = hours_since(created_at)
    return max(0.0, 24.0 - elapsed)

def species_list_embed_text() -> str:
    lines = []
    cats = {}
    for name, d in SPECIES.items():
        cat = d["category"]
        cats.setdefault(cat, []).append((name, d))
    cat_emoji = {
        "mammals": "🦁", "birds": "🐦", "reptiles": "🦎",
        "fish": "🐟", "insects": "🐛", "amphibians": "🐸", "mythical": "✨",
    }
    for cat, members in cats.items():
        parts = " ".join(f"{d['emoji']}`{n}`" for n, d in members)
        lines.append(f"{cat_emoji.get(cat,'•')} **{cat.capitalize()}**: {parts}")
    return "\n".join(lines)
