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


# ── Evolution ─────────────────────────────────────────────────────────────────
# Two evolutions: stage 1 at level 25, stage 2 at level 50.
# stat_boost is added to health, hunger, happiness, energy caps (clamped at 100).

_CATEGORY_EVO: dict[str, list] = {
    "mammals":    [{"emoji":"🦁","title":"Alpha","stat_boost":10},      {"emoji":"🦁","title":"Ancient One","stat_boost":20}],
    "birds":      [{"emoji":"🦅","title":"Soaring","stat_boost":10},    {"emoji":"🦅","title":"Sky Legend","stat_boost":20}],
    "reptiles":   [{"emoji":"🐉","title":"Ancient","stat_boost":10},    {"emoji":"🐉","title":"Primordial","stat_boost":20}],
    "fish":       [{"emoji":"🐟","title":"Deepwater","stat_boost":10},  {"emoji":"🐟","title":"Abyssal","stat_boost":20}],
    "insects":    [{"emoji":"🦋","title":"Matured","stat_boost":10},    {"emoji":"🦋","title":"Elder","stat_boost":20}],
    "amphibians": [{"emoji":"🐸","title":"Elder","stat_boost":10},      {"emoji":"🐸","title":"Ancient","stat_boost":20}],
    "mythical":   [{"emoji":"✨","title":"Awakened","stat_boost":15},   {"emoji":"⭐","title":"Transcendent","stat_boost":30}],
}

EVOLUTIONS: dict[str, list] = {
    "cat":        [{"emoji":"🐈",   "title":"Prowler",          "stat_boost":10}, {"emoji":"🐈‍⬛","title":"Shadow Lord",      "stat_boost":20}],
    "dog":        [{"emoji":"🦮",   "title":"Guardian",         "stat_boost":10}, {"emoji":"🐕‍🦺","title":"Warden",           "stat_boost":20}],
    "bunny":      [{"emoji":"🐇",   "title":"Swift Hare",       "stat_boost":10}, {"emoji":"🐰", "title":"Moon Bunny",        "stat_boost":18}],
    "hamster":    [{"emoji":"🐹",   "title":"Speedster",        "stat_boost": 8}, {"emoji":"🐹", "title":"Titan Hamster",     "stat_boost":16}],
    "fox":        [{"emoji":"🦊",   "title":"Vixen",            "stat_boost":10}, {"emoji":"🦊", "title":"Nine-Tail",         "stat_boost":22}],
    "wolf":       [{"emoji":"🐺",   "title":"Alpha Wolf",       "stat_boost":12}, {"emoji":"🐺", "title":"Dire Wolf",         "stat_boost":25}],
    "raccoon":    [{"emoji":"🦝",   "title":"Bandit",           "stat_boost":10}, {"emoji":"🦝", "title":"Master Thief",      "stat_boost":20}],
    "deer":       [{"emoji":"🦌",   "title":"Stag",             "stat_boost":10}, {"emoji":"🦌", "title":"Celestial Stag",    "stat_boost":20}],
    "panda":      [{"emoji":"🐼",   "title":"Iron Panda",       "stat_boost":10}, {"emoji":"🐼", "title":"Jade Guardian",     "stat_boost":22}],
    "koala":      [{"emoji":"🐨",   "title":"Sleepy Elder",     "stat_boost": 8}, {"emoji":"🐨", "title":"Ancient Koala",     "stat_boost":18}],
    "bear":       [{"emoji":"🐻",   "title":"Grizzly",          "stat_boost":12}, {"emoji":"🐻‍❄️","title":"Glacier Bear",      "stat_boost":25}],
    "tiger":      [{"emoji":"🐯",   "title":"Apex Tiger",       "stat_boost":12}, {"emoji":"🐯", "title":"Shadow Tiger",      "stat_boost":25}],
    "lion":       [{"emoji":"🦁",   "title":"Mane King",        "stat_boost":12}, {"emoji":"🦁", "title":"Solar Lion",        "stat_boost":25}],
    "elephant":   [{"emoji":"🐘",   "title":"Tusk Lord",        "stat_boost":12}, {"emoji":"🐘", "title":"Ancient Mammoth",   "stat_boost":25}],
    "unicorn":    [{"emoji":"🦄",   "title":"Alicorn",          "stat_boost":15}, {"emoji":"🌟", "title":"Celestial",         "stat_boost":30}],
    "cerberus":   [{"emoji":"🐕",   "title":"Hell Guardian",    "stat_boost":15}, {"emoji":"🐺", "title":"Infernal Warden",   "stat_boost":30}],
    "kitsune":    [{"emoji":"🦊",   "title":"Seven-Tail",       "stat_boost":15}, {"emoji":"🌟", "title":"Divine Kitsune",    "stat_boost":32}],
    "kirin":      [{"emoji":"🦒",   "title":"Radiant Kirin",    "stat_boost":15}, {"emoji":"⭐", "title":"Divine Kirin",      "stat_boost":32}],
    "parrot":     [{"emoji":"🦜",   "title":"Elder Parrot",     "stat_boost":10}, {"emoji":"🦜", "title":"Oracle Parrot",     "stat_boost":20}],
    "penguin":    [{"emoji":"🐧",   "title":"Commander",        "stat_boost":10}, {"emoji":"🐧", "title":"Emperor",           "stat_boost":20}],
    "crow":       [{"emoji":"🐦‍⬛","title":"Raven",             "stat_boost":10}, {"emoji":"🐦‍⬛","title":"Shadow Raven",    "stat_boost":22}],
    "owl":        [{"emoji":"🦉",   "title":"Sage Owl",         "stat_boost":10}, {"emoji":"🦉", "title":"Oracle",            "stat_boost":22}],
    "flamingo":   [{"emoji":"🦩",   "title":"Rose Queen",       "stat_boost":10}, {"emoji":"🦩", "title":"Eternal Flamingo",  "stat_boost":20}],
    "toucan":     [{"emoji":"🦚",   "title":"Prism Beak",       "stat_boost":10}, {"emoji":"🦚", "title":"Rainbow Toucan",    "stat_boost":20}],
    "peacock":    [{"emoji":"🦚",   "title":"Crown Peacock",    "stat_boost":10}, {"emoji":"🦚", "title":"Imperial",          "stat_boost":22}],
    "eagle":      [{"emoji":"🦅",   "title":"Apex Eagle",       "stat_boost":12}, {"emoji":"🦅", "title":"Storm Lord",        "stat_boost":25}],
    "hummingbird":[{"emoji":"🐦",   "title":"Blur Wing",        "stat_boost":10}, {"emoji":"🌈", "title":"Prismatic Wing",    "stat_boost":20}],
    "phoenix":    [{"emoji":"🦅",   "title":"Reborn Phoenix",   "stat_boost":15}, {"emoji":"🌟", "title":"Immortal Blaze",    "stat_boost":30}],
    "griffin":    [{"emoji":"🦅",   "title":"Royal Griffin",    "stat_boost":15}, {"emoji":"🌟", "title":"Celestial Griffin", "stat_boost":30}],
    "dragon":     [{"emoji":"🐲",   "title":"Drake",            "stat_boost":12}, {"emoji":"🐲", "title":"Elder Dragon",      "stat_boost":28}],
    "chameleon":  [{"emoji":"🦎",   "title":"Phantom",          "stat_boost":10}, {"emoji":"🌫️","title":"Void Shade",        "stat_boost":22}],
    "turtle":     [{"emoji":"🐢",   "title":"Iron Shell",       "stat_boost":10}, {"emoji":"🐢", "title":"Ancient Shell",     "stat_boost":22}],
    "snake":      [{"emoji":"🐍",   "title":"Viper",            "stat_boost":10}, {"emoji":"🐍", "title":"Shadow Serpent",    "stat_boost":22}],
    "crocodile":  [{"emoji":"🐊",   "title":"Titan Croc",       "stat_boost":12}, {"emoji":"🐊", "title":"Ancient Behemoth",  "stat_boost":25}],
    "hydra":      [{"emoji":"🐉",   "title":"Greater Hydra",    "stat_boost":15}, {"emoji":"💀", "title":"Ancient Hydra",     "stat_boost":30}],
    "shark":      [{"emoji":"🦈",   "title":"Great White",      "stat_boost":12}, {"emoji":"🦈", "title":"Leviathan-Touched", "stat_boost":25}],
    "jellyfish":  [{"emoji":"🪼",   "title":"Deep Drifter",     "stat_boost":10}, {"emoji":"🌊", "title":"Abyssal Crown",     "stat_boost":22}],
    "butterfly":  [{"emoji":"🦋",   "title":"Chrysalis",        "stat_boost":10}, {"emoji":"🌸", "title":"Moonwing",          "stat_boost":20}],
    "firefly":    [{"emoji":"✨",   "title":"Bright Flame",     "stat_boost":10}, {"emoji":"⚡", "title":"Thunder Sprite",    "stat_boost":20}],
    "sprite":     [{"emoji":"🧚",   "title":"Elder Sprite",     "stat_boost":12}, {"emoji":"⭐", "title":"Arcane Sprite",     "stat_boost":25}],
    "leviathan":  [{"emoji":"🐉",   "title":"Sea Terror",       "stat_boost":18}, {"emoji":"🌊", "title":"World Ender",       "stat_boost":35}],
    "thunderbird":[{"emoji":"⚡",   "title":"Storm Hawk",       "stat_boost":15}, {"emoji":"🌩️","title":"Sky God",           "stat_boost":30}],
}

def check_evolution(species: str, new_level: int) -> dict | None:
    """Returns evolution dict if new_level (25 or 50) triggers one, else None."""
    if new_level not in (25, 50):
        return None
    idx = 0 if new_level == 25 else 1
    evo_list = EVOLUTIONS.get(species)
    if not evo_list:
        cat = SPECIES.get(species, {}).get("category", "mammals")
        evo_list = _CATEGORY_EVO.get(cat, [])
    return evo_list[idx] if idx < len(evo_list) else None

def process_level_up(species: str, current_level: int, current_xp: int,
                     gained_xp: int, current_evo_stage: int) -> dict:
    """
    Calculates the result of gaining XP.
    Returns a dict with leveled_up, new_level, new_xp, evolved, new_evo_stage, evo_info.
    """
    new_xp = current_xp + gained_xp
    if new_xp < xp_for_next_level(current_level):
        return {"leveled_up": False, "new_level": current_level, "new_xp": new_xp,
                "evolved": False, "new_evo_stage": current_evo_stage, "evo_info": None}
    new_level = current_level + 1
    evo_info  = check_evolution(species, new_level)
    new_stage = current_evo_stage + (1 if evo_info else 0)
    return {"leveled_up": True, "new_level": new_level, "new_xp": 0,
            "evolved": bool(evo_info), "new_evo_stage": new_stage, "evo_info": evo_info}

def get_evo_display(species: str, evo_stage: int) -> tuple[str, str]:
    """Returns (emoji, title) for the given evolution stage."""
    base_emoji = SPECIES.get(species, {}).get("emoji", "🐾")
    if evo_stage == 0:
        return base_emoji, "Rookie"
    idx = evo_stage - 1
    evo_list = EVOLUTIONS.get(species)
    if not evo_list:
        cat = SPECIES.get(species, {}).get("category", "mammals")
        evo_list = _CATEGORY_EVO.get(cat, [])
    if evo_list and idx < len(evo_list):
        return evo_list[idx]["emoji"], evo_list[idx]["title"]
    return base_emoji, "Elder"


# ── Hunting loot by element ───────────────────────────────────────────────────

HUNT_LOOT: dict[str, dict] = {
    "Fire": {
        "territory": "Volcanic Plains 🌋",
        "flavor_lines": [
            "scrambled through scorched craters and found buried treasure",
            "sniffed out hot-spring pools where ancient coins had sunk",
            "chased ember sprites across the lava fields",
            "dug through ash pits left by old campfires",
            "scaled a smouldering peak and discovered a hidden cache",
        ],
        "coin_range": {"common": (10,25), "uncommon": (20,45), "rare": (40,80), "jackpot": (80,150)},
        "common":   ["apple", "energy_drink"],
        "uncommon": ["feast", "potion"],
        "rare":     ["energy_drink", "feast"],
        "jackpot":  ["hatch_gem"],
    },
    "Water": {
        "territory": "Ocean Coves & Misty Rivers 🌊",
        "flavor_lines": [
            "dove into crystal coves and found sunken treasure",
            "followed river currents to a hidden grotto",
            "caught fish in moonlit tide pools",
            "swam through kelp forests and found rare pearls",
            "explored a sunken shipwreck full of goodies",
        ],
        "coin_range": {"common": (10,25), "uncommon": (20,45), "rare": (40,80), "jackpot": (80,150)},
        "common":   ["apple", "feast"],
        "uncommon": ["potion", "feast"],
        "rare":     ["potion", "energy_drink"],
        "jackpot":  ["hatch_gem"],
    },
    "Earth": {
        "territory": "Ancient Forests & Mountain Caves 🏔️",
        "flavor_lines": [
            "burrowed through mossy earth and struck a vein of gems",
            "foraged through ancient woodland and gathered rare herbs",
            "tracked a wild trail deep into a misty forest",
            "excavated a forgotten tomb hidden under a mountain",
            "found a hidden meadow full of wild provisions",
        ],
        "coin_range": {"common": (12,28), "uncommon": (22,48), "rare": (45,85), "jackpot": (90,160)},
        "common":   ["apple", "toy"],
        "uncommon": ["feast", "energy_drink"],
        "rare":     ["potion", "feast"],
        "jackpot":  ["hatch_gem"],
    },
    "Lightning": {
        "territory": "Stormy Highlands ⛈️",
        "flavor_lines": [
            "raced through electric storm clouds chasing sparks",
            "surfed a lightning bolt down from the peaks",
            "found a cache of charged crystals in a clifftop cave",
            "outran a thunderstorm and found the prize at its eye",
            "charged through storm-swept fields at blinding speed",
        ],
        "coin_range": {"common": (12,28), "uncommon": (25,50), "rare": (45,85), "jackpot": (90,160)},
        "common":   ["energy_drink", "apple"],
        "uncommon": ["energy_drink", "toy"],
        "rare":     ["potion", "energy_drink"],
        "jackpot":  ["hatch_gem"],
    },
    "Shadow": {
        "territory": "Twilight Ruins & Dark Forests 🌑",
        "flavor_lines": [
            "slipped through shadow portals and returned with strange relics",
            "stalked through haunted ruins under moonlight",
            "phased through the Dark Forest and found hidden vaults",
            "picked pockets of unsuspecting ghosts",
            "lurked at the edge of the Void and snatched rare loot",
        ],
        "coin_range": {"common": (15,30), "uncommon": (28,55), "rare": (50,95), "jackpot": (100,175)},
        "common":   ["apple", "toy"],
        "uncommon": ["potion", "energy_drink"],
        "rare":     ["feast", "potion"],
        "jackpot":  ["hatch_gem"],
    },
    "Ice": {
        "territory": "Frozen Tundra & Ice Caverns ❄️",
        "flavor_lines": [
            "skated across frozen lakes and discovered icy treasure troves",
            "chipped through glacier walls and found ancient artefacts",
            "tracked polar spirits across the tundra",
            "dove into ice caves where ancient hoards slept",
            "caught snowflake crystals that dissolved into rare materials",
        ],
        "coin_range": {"common": (10,25), "uncommon": (20,45), "rare": (40,80), "jackpot": (80,150)},
        "common":   ["apple", "potion"],
        "uncommon": ["feast", "potion"],
        "rare":     ["energy_drink", "potion"],
        "jackpot":  ["hatch_gem"],
    },
    "Wind": {
        "territory": "Sky Islands & Mountain Peaks 🌤️",
        "flavor_lines": [
            "rode the updrafts to a hidden sky island full of loot",
            "chased wind spirits across floating cloud platforms",
            "spiralled through a tornado and emerged with treasures",
            "glided to a forgotten eagle's nest stocked with gems",
            "surfed gale-force winds to a remote mountain summit",
        ],
        "coin_range": {"common": (12,28), "uncommon": (25,50), "rare": (50,90), "jackpot": (100,170)},
        "common":   ["apple", "energy_drink"],
        "uncommon": ["toy", "feast"],
        "rare":     ["energy_drink", "potion"],
        "jackpot":  ["hatch_gem"],
    },
    "Lava": {
        "territory": "Volcanic Islands & Lava Tubes 🌋",
        "flavor_lines": [
            "plunged into a lava tube and emerged with molten gold",
            "wrestled a magma golem for its treasure hoard",
            "surfed rivers of lava to a legendary volcanic forge",
            "cracked open obsidian boulders to find gem cores",
            "survived an eruption and claimed the aftermath riches",
        ],
        "coin_range": {"common": (15,35), "uncommon": (30,60), "rare": (55,100), "jackpot": (110,200)},
        "common":   ["apple", "energy_drink"],
        "uncommon": ["feast", "energy_drink"],
        "rare":     ["potion", "feast"],
        "jackpot":  ["hatch_gem"],
    },
}


# ── /pet command messages ─────────────────────────────────────────────────────

PET_MESSAGES: dict[str, list[str]] = {
    "mammals": [
        "**{name}** nuzzles their head into your hand! 🥰",
        "You scratch **{name}**'s ears — they're in absolute heaven! ✨",
        "**{name}** rolls onto their back and demands belly rubs! 😂",
        "**{name}** leans against you and rumbles contentedly. 💙",
        "You and **{name}** share a quiet moment. So wholesome! 🫶",
        "**{name}** bumps your hand with their nose, asking for more pets! 🐾",
    ],
    "birds": [
        "**{name}** fluffs up their feathers in pure delight! 🪶",
        "**{name}** chirps happily and gently pecks your finger. Adorable! 🐦",
        "You stroke **{name}**'s sleek feathers — they coo softly. 💙",
        "**{name}** bows their head, inviting you to scratch their crown! 👑",
        "**{name}** spreads their wings proudly, showing off for you! 🌟",
    ],
    "reptiles": [
        "**{name}** flicks their tongue at you curiously! 👅",
        "You gently stroke **{name}**'s cool scales. They close their eyes. 💚",
        "**{name}** basks in your warmth and lets out a slow, happy breath. ☀️",
        "**{name}** tilts their head at you with ancient, wise eyes. 🦎",
        "**{name}** slowly climbs up your arm to get closer to you! 🌿",
    ],
    "fish": [
        "You tap the glass and **{name}** swims over excitedly! 🫧",
        "**{name}** blows a series of happy bubbles when they see you! 💭",
        "You watch **{name}** glide gracefully — incredibly relaxing! 🌊",
        "**{name}** does three laps around the tank in excitement! 🐟",
        "**{name}** presses up against the glass near your hand. 💙",
    ],
    "insects": [
        "**{name}** lands gently on your outstretched finger! 🌸",
        "You watch **{name}** flutter and dance in the air just for you! 🌀",
        "**{name}** glows a little brighter when you're nearby. ✨",
        "**{name}** rests on your shoulder and seems perfectly content. 🍃",
        "**{name}** does a little victory dance in your presence! 💫",
    ],
    "amphibians": [
        "**{name}** ribbits happily and leaps into your cupped hands! 🍃",
        "You gently hold **{name}** — they're surprisingly warm! 💚",
        "**{name}** inflates their throat pouch in a joyful display! 🎶",
        "**{name}** blinks their huge eyes at you slowly. Pure trust! 🌿",
        "**{name}** hops in circles around your feet with glee! 🐸",
    ],
    "mythical": [
        "**{name}** emanates a warm magical aura that envelops you! 🌟",
        "The air shimmers as **{name}** gracefully acknowledges you. ✨",
        "**{name}** gazes at you with ancient, knowing eyes. You feel seen. 👁️",
        "**{name}** channels a gentle blessing through your fingertips. 💫",
        "A soft light glows around **{name}** as they nuzzle close. 🌙",
    ],
}
