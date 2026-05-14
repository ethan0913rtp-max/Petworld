"""Quest templates and generation logic for PetWorld."""
import random
from datetime import datetime, timedelta

# ── Templates ─────────────────────────────────────────────────────────────────
# Each element has 3 daily options (2 picked) and 2 weekly options (1 picked).
# action must match strings used in data.track_quest_action().

QUEST_TEMPLATES = {
    "Fire": {
        "daily": [
            {"id":"fire_d1","desc":"Win 2 battles ⚔️","action":"win_battle","target":2,"coins":80,"xp":60},
            {"id":"fire_d2","desc":"Train 3 times 💪","action":"train","target":3,"coins":60,"xp":80},
            {"id":"fire_d3","desc":"Go hunting twice 🏹","action":"hunt","target":2,"coins":70,"xp":55},
        ],
        "weekly": [
            {"id":"fire_w1","desc":"Win 8 battles 🏆","action":"win_battle","target":8,"coins":350,"xp":250,"item":"energy_drink"},
            {"id":"fire_w2","desc":"Train 12 times 🔥","action":"train","target":12,"coins":300,"xp":300,"item":"feast"},
        ],
    },
    "Water": {
        "daily": [
            {"id":"water_d1","desc":"Go hunting 3 times 🏹","action":"hunt","target":3,"coins":75,"xp":55},
            {"id":"water_d2","desc":"Feed your pet 3 times 🍖","action":"feed","target":3,"coins":50,"xp":50},
            {"id":"water_d3","desc":"Rest 2 times 😴","action":"rest","target":2,"coins":60,"xp":45},
        ],
        "weekly": [
            {"id":"water_w1","desc":"Hunt 10 times 🌊","action":"hunt","target":10,"coins":350,"xp":250,"item":"potion"},
            {"id":"water_w2","desc":"Feed your pet 12 times 🍖","action":"feed","target":12,"coins":300,"xp":280,"item":"feast"},
        ],
    },
    "Earth": {
        "daily": [
            {"id":"earth_d1","desc":"Work 2 times 💼","action":"work","target":2,"coins":65,"xp":55},
            {"id":"earth_d2","desc":"Rest 3 times 🌿","action":"rest","target":3,"coins":55,"xp":60},
            {"id":"earth_d3","desc":"Go hunting twice 🏕️","action":"hunt","target":2,"coins":70,"xp":55},
        ],
        "weekly": [
            {"id":"earth_w1","desc":"Work 8 times 🏔️","action":"work","target":8,"coins":320,"xp":240,"item":"feast"},
            {"id":"earth_w2","desc":"Rest 12 times 🌱","action":"rest","target":12,"coins":280,"xp":280,"item":"energy_drink"},
        ],
    },
    "Lightning": {
        "daily": [
            {"id":"light_d1","desc":"Battle 3 times ⚡","action":"battle","target":3,"coins":70,"xp":65},
            {"id":"light_d2","desc":"Play 4 times 🎮","action":"play","target":4,"coins":55,"xp":70},
            {"id":"light_d3","desc":"Train twice 💪","action":"train","target":2,"coins":60,"xp":60},
        ],
        "weekly": [
            {"id":"light_w1","desc":"Battle 10 times ⚡","action":"battle","target":10,"coins":330,"xp":260,"item":"energy_drink"},
            {"id":"light_w2","desc":"Play 15 times 🎮","action":"play","target":15,"coins":290,"xp":300,"item":"toy"},
        ],
    },
    "Shadow": {
        "daily": [
            {"id":"shadow_d1","desc":"Go hunting 3 times 🌑","action":"hunt","target":3,"coins":80,"xp":60},
            {"id":"shadow_d2","desc":"Win a battle ⚔️","action":"win_battle","target":1,"coins":70,"xp":70},
            {"id":"shadow_d3","desc":"Pet your companion 2 times 🖐️","action":"pet_action","target":2,"coins":50,"xp":50},
        ],
        "weekly": [
            {"id":"shadow_w1","desc":"Hunt 10 times 🌘","action":"hunt","target":10,"coins":360,"xp":260,"item":"potion"},
            {"id":"shadow_w2","desc":"Win 6 battles 🌑","action":"win_battle","target":6,"coins":340,"xp":280,"item":"energy_drink"},
        ],
    },
    "Ice": {
        "daily": [
            {"id":"ice_d1","desc":"Rest 3 times ❄️","action":"rest","target":3,"coins":55,"xp":55},
            {"id":"ice_d2","desc":"Feed your pet 4 times 🍎","action":"feed","target":4,"coins":60,"xp":50},
            {"id":"ice_d3","desc":"Pet your companion 3 times 🖐️","action":"pet_action","target":3,"coins":55,"xp":60},
        ],
        "weekly": [
            {"id":"ice_w1","desc":"Rest 12 times ❄️","action":"rest","target":12,"coins":300,"xp":240,"item":"potion"},
            {"id":"ice_w2","desc":"Feed your pet 15 times 🥶","action":"feed","target":15,"coins":290,"xp":270,"item":"feast"},
        ],
    },
    "Wind": {
        "daily": [
            {"id":"wind_d1","desc":"Fly 2 times (bird only) 🪽","action":"fly","target":2,"coins":90,"xp":65},
            {"id":"wind_d2","desc":"Play 4 times 🌪️","action":"play","target":4,"coins":60,"xp":70},
            {"id":"wind_d3","desc":"Train twice 💨","action":"train","target":2,"coins":60,"xp":60},
        ],
        "weekly": [
            {"id":"wind_w1","desc":"Fly 8 times 🌬️","action":"fly","target":8,"coins":380,"xp":280,"item":"wings"},
            {"id":"wind_w2","desc":"Play 15 times 🌪️","action":"play","target":15,"coins":300,"xp":300,"item":"toy"},
        ],
    },
    "Lava": {
        "daily": [
            {"id":"lava_d1","desc":"Train 3 times 🌋","action":"train","target":3,"coins":75,"xp":75},
            {"id":"lava_d2","desc":"Go hunting twice 🏹","action":"hunt","target":2,"coins":70,"xp":60},
            {"id":"lava_d3","desc":"Win a battle ⚔️","action":"win_battle","target":1,"coins":80,"xp":70},
        ],
        "weekly": [
            {"id":"lava_w1","desc":"Train 12 times 🌋","action":"train","target":12,"coins":370,"xp":300,"item":"energy_drink"},
            {"id":"lava_w2","desc":"Hunt 8 times 🔥","action":"hunt","target":8,"coins":340,"xp":260,"item":"potion"},
        ],
    },
}

FALLBACK_ELEMENT = "Fire"

def _now():
    return datetime.utcnow()

def _daily_expires():
    return (_now() + timedelta(hours=24)).isoformat()

def _weekly_expires():
    return (_now() + timedelta(days=7)).isoformat()

def generate_new_quests(user_id: str, element: str) -> list[dict]:
    """
    Returns a list of quest dicts ready to be inserted into the DB.
    2 daily quests + 1 weekly quest.
    """
    templates = QUEST_TEMPLATES.get(element, QUEST_TEMPLATES[FALLBACK_ELEMENT])
    daily_picks  = random.sample(templates["daily"],  min(2, len(templates["daily"])))
    weekly_pick  = [random.choice(templates["weekly"])]
    now_str      = _now().isoformat()
    rows = []
    for t in daily_picks:
        rows.append({
            "user_id": user_id, "quest_type": "daily", "element": element,
            "template_id": t["id"], "description": t["desc"],
            "action": t["action"], "target": t["target"], "progress": 0,
            "status": "active",
            "reward_coins": t["coins"], "reward_xp": t["xp"],
            "reward_item": t.get("item"),
            "created_at": now_str, "expires_at": _daily_expires(),
        })
    for t in weekly_pick:
        rows.append({
            "user_id": user_id, "quest_type": "weekly", "element": element,
            "template_id": t["id"], "description": t["desc"],
            "action": t["action"], "target": t["target"], "progress": 0,
            "status": "active",
            "reward_coins": t["coins"], "reward_xp": t["xp"],
            "reward_item": t.get("item"),
            "created_at": now_str, "expires_at": _weekly_expires(),
        })
    return rows

def is_expired(expires_at: str) -> bool:
    try:
        return datetime.fromisoformat(expires_at) < _now()
    except Exception:
        return True
