import sqlite3
import json
import os
import random
from datetime import datetime

# ── Badge definitions (used by profile, achievements, cogs) ───────────────────
BADGE_INFO: dict[str, dict] = {
    "first_pet":    {"emoji": "🐾", "label": "First Steps",       "desc": "Adopted your first pet"},
    "first_win":    {"emoji": "⚔️", "label": "First Victory",     "desc": "Won your first battle"},
    "first_evo":    {"emoji": "✨", "label": "Evolved",           "desc": "Your pet evolved for the first time"},
    "level_50":     {"emoji": "🏆", "label": "Level 50 Master",   "desc": "Raised a pet to Level 50"},
    "hatch_5":      {"emoji": "🥚", "label": "Egg Hatcher",       "desc": "Hatched 5 eggs"},
    "breed_3":      {"emoji": "🧬", "label": "Breeder",           "desc": "Bred 3 pets"},
    "win_10":       {"emoji": "👑", "label": "Battle Champion",   "desc": "Won 10 battles"},
    "quest_7":      {"emoji": "📋", "label": "Quest Legend",      "desc": "Completed 7 daily quests"},
    "rival_slayer": {"emoji": "🗡️", "label": "Rival Slayer",      "desc": "Defeated your declared rival 5 times"},
}

DB_PATH = os.path.join(os.path.dirname(__file__), "petworld.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _add_column_if_missing(cursor, table: str, column: str, col_def: str):
    cursor.execute(f"PRAGMA table_info({table})")
    existing = {row["name"] for row in cursor.fetchall()}
    if column not in existing:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id    TEXT PRIMARY KEY,
            username   TEXT,
            coins      INTEGER DEFAULT 100,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            pet_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     TEXT,
            name        TEXT,
            species     TEXT,
            level       INTEGER DEFAULT 1,
            xp          INTEGER DEFAULT 0,
            hunger      INTEGER DEFAULT 100,
            happiness   INTEGER DEFAULT 100,
            health      INTEGER DEFAULT 100,
            energy      INTEGER DEFAULT 100,
            age_days    INTEGER DEFAULT 0,
            last_fed    TEXT,
            last_played TEXT,
            last_rested TEXT,
            last_trained TEXT,
            is_active   INTEGER DEFAULT 1,
            created_at  TEXT,
            is_egg      INTEGER DEFAULT 0,
            equipment   TEXT DEFAULT '{}',
            rarity      TEXT DEFAULT 'common',
            parent1_id  INTEGER DEFAULT NULL,
            parent2_id  INTEGER DEFAULT NULL,
            FOREIGN KEY(user_id) REFERENCES players(user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   TEXT,
            item_name TEXT,
            quantity  INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES players(user_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS breed_requests (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            requester   TEXT,
            target      TEXT,
            pet1_id     INTEGER,
            pet2_id     INTEGER,
            created_at  TEXT,
            status      TEXT DEFAULT 'pending'
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    TEXT,
            badge_id   TEXT,
            earned_at  TEXT,
            UNIQUE(user_id, badge_id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS quests (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       TEXT,
            quest_type    TEXT,
            element       TEXT,
            template_id   TEXT,
            description   TEXT,
            action        TEXT,
            progress      INTEGER DEFAULT 0,
            target        INTEGER,
            status        TEXT DEFAULT 'active',
            reward_coins  INTEGER DEFAULT 0,
            reward_xp     INTEGER DEFAULT 0,
            reward_item   TEXT,
            created_at    TEXT,
            expires_at    TEXT
        )
    """)

    # Migrations for existing DBs
    for col, defn in [
        ("is_egg",     "INTEGER DEFAULT 0"),
        ("equipment",  "TEXT DEFAULT '{}'"),
        ("rarity",     "TEXT DEFAULT 'common'"),
        ("parent1_id", "INTEGER DEFAULT NULL"),
        ("parent2_id", "INTEGER DEFAULT NULL"),
        ("evo_stage",  "INTEGER DEFAULT 0"),
        ("variant",    "INTEGER DEFAULT 1"),
    ]:
        _add_column_if_missing(c, "pets", col, defn)

    for col, defn in [
        ("total_battles_won",       "INTEGER DEFAULT 0"),
        ("total_eggs_hatched",      "INTEGER DEFAULT 0"),
        ("total_daily_quests_done", "INTEGER DEFAULT 0"),
        ("rival_id",                "TEXT DEFAULT NULL"),
        ("rival_wins",              "INTEGER DEFAULT 0"),
        ("rival_losses",            "INTEGER DEFAULT 0"),
    ]:
        _add_column_if_missing(c, "players", col, defn)

    conn.commit()
    conn.close()

# ── Players ───────────────────────────────────────────────────────────────────

def get_player(user_id: str):
    conn = get_conn()
    row = conn.execute("SELECT * FROM players WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_player(user_id: str, username: str):
    conn = get_conn()
    now = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT OR IGNORE INTO players (user_id, username, coins, created_at) VALUES (?,?,?,?)",
        (user_id, username, 100, now),
    )
    conn.commit()
    conn.close()

def update_player(user_id: str, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [user_id]
    conn = get_conn()
    conn.execute(f"UPDATE players SET {fields} WHERE user_id=?", values)
    conn.commit()
    conn.close()

# ── Pets ─────────────────────────────────────────────────────────────────────

def get_active_pet(user_id: str):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM pets WHERE user_id=? AND is_active=1 AND is_egg=0 ORDER BY pet_id DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return _parse_pet(dict(row)) if row else None

def get_active_pet_or_egg(user_id: str):
    """Returns the active pet (hatched or egg) for the user."""
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM pets WHERE user_id=? AND is_active=1 ORDER BY pet_id DESC LIMIT 1",
        (user_id,),
    ).fetchone()
    conn.close()
    return _parse_pet(dict(row)) if row else None

def get_all_pets(user_id: str):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM pets WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return [_parse_pet(dict(r)) for r in rows]

def get_all_eggs(user_id: str):
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM pets WHERE user_id=? AND is_egg=1", (user_id,)
    ).fetchall()
    conn.close()
    return [_parse_pet(dict(r)) for r in rows]

def _parse_pet(pet: dict) -> dict:
    if isinstance(pet.get("equipment"), str):
        try:
            pet["equipment"] = json.loads(pet["equipment"] or "{}")
        except Exception:
            pet["equipment"] = {}
    return pet

def create_pet(user_id: str, name: str, species: str, is_egg: bool = False, rarity: str = "common",
               parent1_id: int = None, parent2_id: int = None):
    from pets import SPECIES
    conn = get_conn()
    now = datetime.utcnow().isoformat()
    s_data = SPECIES.get(species, {})
    actual_rarity = rarity or s_data.get("rarity", "common")
    variant = random.randint(1, 50)
    conn.execute(
        """INSERT INTO pets (user_id, name, species, level, xp, hunger, happiness, health, energy,
           age_days, last_fed, last_played, last_rested, last_trained, is_active, created_at,
           is_egg, equipment, rarity, parent1_id, parent2_id, variant)
           VALUES (?,?,?,1,0,100,100,100,100,0,?,?,?,?,1,?,?,?,?,?,?,?)""",
        (user_id, name, species, now, now, now, now, now, is_egg, "{}",
         actual_rarity, parent1_id, parent2_id, variant),
    )
    conn.commit()
    conn.close()

def update_pet(pet_id: int, **kwargs):
    if not kwargs:
        return
    if "equipment" in kwargs and isinstance(kwargs["equipment"], dict):
        kwargs["equipment"] = json.dumps(kwargs["equipment"])
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [pet_id]
    conn = get_conn()
    conn.execute(f"UPDATE pets SET {fields} WHERE pet_id=?", values)
    conn.commit()
    conn.close()

# ── Inventory ─────────────────────────────────────────────────────────────────

def get_inventory(user_id: str):
    conn = get_conn()
    rows = conn.execute(
        "SELECT item_name, quantity FROM inventory WHERE user_id=? AND quantity > 0",
        (user_id,),
    ).fetchall()
    conn.close()
    return {r["item_name"]: r["quantity"] for r in rows}

def add_item(user_id: str, item_name: str, quantity: int = 1):
    conn = get_conn()
    existing = conn.execute(
        "SELECT id, quantity FROM inventory WHERE user_id=? AND item_name=?",
        (user_id, item_name),
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE inventory SET quantity=? WHERE id=?",
            (existing["quantity"] + quantity, existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO inventory (user_id, item_name, quantity) VALUES (?,?,?)",
            (user_id, item_name, quantity),
        )
    conn.commit()
    conn.close()

def remove_item(user_id: str, item_name: str, quantity: int = 1) -> bool:
    conn = get_conn()
    existing = conn.execute(
        "SELECT id, quantity FROM inventory WHERE user_id=? AND item_name=?",
        (user_id, item_name),
    ).fetchone()
    if not existing or existing["quantity"] < quantity:
        conn.close()
        return False
    conn.execute(
        "UPDATE inventory SET quantity=? WHERE id=?",
        (existing["quantity"] - quantity, existing["id"]),
    )
    conn.commit()
    conn.close()
    return True

# ── Breed requests ────────────────────────────────────────────────────────────

def create_breed_request(requester: str, target: str, pet1_id: int, pet2_id: int):
    conn = get_conn()
    now = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO breed_requests (requester, target, pet1_id, pet2_id, created_at, status) VALUES (?,?,?,?,?,?)",
        (requester, target, pet1_id, pet2_id, now, "pending"),
    )
    conn.commit()
    conn.close()

def get_pending_breed_request(target: str):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM breed_requests WHERE target=? AND status='pending' ORDER BY id DESC LIMIT 1",
        (target,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def update_breed_request(req_id: int, status: str):
    conn = get_conn()
    conn.execute("UPDATE breed_requests SET status=? WHERE id=?", (status, req_id))
    conn.commit()
    conn.close()

def get_pet_by_id(pet_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM pets WHERE pet_id=?", (pet_id,)).fetchone()
    conn.close()
    return _parse_pet(dict(row)) if row else None

# ── Leaderboard ───────────────────────────────────────────────────────────────

def get_leaderboard(limit: int = 10):
    conn = get_conn()
    rows = conn.execute(
        """SELECT p.username, p.coins, pet.name as pet_name, pet.level, pet.species,
                  pet.rarity, COALESCE(pet.evo_stage,0) as evo_stage
           FROM players p
           LEFT JOIN pets pet ON pet.user_id = p.user_id AND pet.is_active = 1 AND pet.is_egg = 0
           ORDER BY pet.level DESC, p.coins DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Evolution ─────────────────────────────────────────────────────────────────

def apply_evo_stat_boost(pet_id: int, boost: int):
    """Increase a pet's current stats by the evolution boost amount (capped at 100)."""
    conn = get_conn()
    row  = conn.execute("SELECT health, hunger, happiness, energy FROM pets WHERE pet_id=?", (pet_id,)).fetchone()
    if row:
        new_health    = min(100, row["health"]    + boost)
        new_hunger    = min(100, row["hunger"]    + boost)
        new_happiness = min(100, row["happiness"] + boost)
        new_energy    = min(100, row["energy"]    + boost)
        conn.execute(
            "UPDATE pets SET health=?, hunger=?, happiness=?, energy=? WHERE pet_id=?",
            (new_health, new_hunger, new_happiness, new_energy, pet_id),
        )
        conn.commit()
    conn.close()


# ── Quests ────────────────────────────────────────────────────────────────────

def ensure_user_quests(user_id: str, element: str) -> list[dict]:
    """
    Returns a user's active quests, generating new ones if all have expired or none exist.
    """
    import quests as quest_lib

    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM quests WHERE user_id=? AND status != 'claimed' ORDER BY id",
        (user_id,),
    ).fetchall()
    conn.close()

    existing = [dict(r) for r in rows]

    # Remove expired active quests
    now_str = datetime.utcnow().isoformat()
    for q in existing:
        if q["status"] == "active" and quest_lib.is_expired(q["expires_at"]):
            _expire_quest(q["id"])

    # Refresh list after expiry
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM quests WHERE user_id=? AND status != 'claimed'",
        (user_id,),
    ).fetchall()
    conn.close()
    live = [dict(r) for r in rows]

    active_or_complete = [q for q in live if q["status"] in ("active", "completed")]
    if active_or_complete:
        return active_or_complete

    # Generate fresh quests
    new_quests = quest_lib.generate_new_quests(user_id, element)
    conn = get_conn()
    for q in new_quests:
        conn.execute(
            """INSERT INTO quests
               (user_id, quest_type, element, template_id, description, action,
                progress, target, status, reward_coins, reward_xp, reward_item, created_at, expires_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (q["user_id"], q["quest_type"], q["element"], q["template_id"],
             q["description"], q["action"], q["progress"], q["target"],
             q["status"], q["reward_coins"], q["reward_xp"], q.get("reward_item"),
             q["created_at"], q["expires_at"]),
        )
    conn.commit()
    rows = conn.execute(
        "SELECT * FROM quests WHERE user_id=? AND status='active'",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _expire_quest(quest_id: int):
    conn = get_conn()
    conn.execute("UPDATE quests SET status='claimed' WHERE id=?", (quest_id,))
    conn.commit()
    conn.close()


def track_quest_action(user_id: str, action: str) -> list[dict]:
    """
    Increments progress for all active quests matching the action.
    Returns a list of quests that were just completed (progress hit target).
    """
    conn   = get_conn()
    rows   = conn.execute(
        "SELECT * FROM quests WHERE user_id=? AND action=? AND status='active'",
        (user_id, action),
    ).fetchall()
    newly_completed = []
    for row in rows:
        q           = dict(row)
        new_progress = q["progress"] + 1
        if new_progress >= q["target"]:
            conn.execute("UPDATE quests SET progress=?, status='completed' WHERE id=?", (q["target"], q["id"]))
            q["progress"] = q["target"]
            q["status"]   = "completed"
            newly_completed.append(q)
        else:
            conn.execute("UPDATE quests SET progress=? WHERE id=?", (new_progress, q["id"]))
    conn.commit()
    conn.close()
    return newly_completed


def claim_quest(quest_id: int):
    """Mark a completed quest as claimed."""
    conn = get_conn()
    conn.execute("UPDATE quests SET status='claimed' WHERE id=? AND status='completed'", (quest_id,))
    conn.commit()
    conn.close()


# ── Achievement system ────────────────────────────────────────────────────────

def get_all_eggs(user_id: str) -> list:
    """Return all active, unhatched eggs for a user."""
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM pets WHERE user_id=? AND is_egg=1 AND is_active=1 ORDER BY created_at",
        (user_id,),
    ).fetchall()
    conn.close()
    return [_parse_pet(dict(r)) for r in rows]

def set_rival(user_id: str, rival_id: str):
    """Declare a new rival, resetting the head-to-head record."""
    conn = get_conn()
    conn.execute(
        "UPDATE players SET rival_id=?, rival_wins=0, rival_losses=0 WHERE user_id=?",
        (rival_id, user_id),
    )
    conn.commit()
    conn.close()

def get_rival_record(user_id: str) -> dict:
    """Return rival_id, rival_wins, rival_losses for a player."""
    conn = get_conn()
    row  = conn.execute(
        "SELECT rival_id, rival_wins, rival_losses FROM players WHERE user_id=?", (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else {}

def increment_stat(user_id: str, stat: str, amount: int = 1):
    """Safely increment a counter column on the players table."""
    conn = get_conn()
    conn.execute(f"UPDATE players SET {stat} = COALESCE({stat}, 0) + ? WHERE user_id=?", (amount, user_id))
    conn.commit()
    conn.close()

def get_achievements(user_id: str) -> list[str]:
    """Return list of badge_ids already earned by the user."""
    conn  = get_conn()
    rows  = conn.execute("SELECT badge_id FROM achievements WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return [r["badge_id"] for r in rows]

def get_player_stats(user_id: str) -> dict:
    """Return a merged dict of player row + computed pet stats for achievement checks."""
    conn = get_conn()
    player = conn.execute("SELECT * FROM players WHERE user_id=?", (user_id,)).fetchone()
    if not player:
        conn.close()
        return {}
    stats = dict(player)

    stats["total_pets"] = conn.execute(
        "SELECT COUNT(*) FROM pets WHERE user_id=?", (user_id,)
    ).fetchone()[0]
    stats["max_pet_level"] = conn.execute(
        "SELECT COALESCE(MAX(level),0) FROM pets WHERE user_id=?", (user_id,)
    ).fetchone()[0]
    stats["total_pets_bred"] = conn.execute(
        "SELECT COUNT(*) FROM pets WHERE user_id=? AND parent1_id IS NOT NULL", (user_id,)
    ).fetchone()[0]
    stats["total_evolutions"] = conn.execute(
        "SELECT COUNT(*) FROM pets WHERE user_id=? AND evo_stage > 0", (user_id,)
    ).fetchone()[0]
    conn.close()
    return stats

def check_and_award_achievements(user_id: str) -> list[str]:
    """
    Evaluates all badge conditions and inserts any newly earned badges.
    Returns the list of newly awarded badge IDs.
    """
    stats   = get_player_stats(user_id)
    if not stats:
        return []
    earned  = set(get_achievements(user_id))

    conditions: dict[str, bool] = {
        "first_pet":    stats["total_pets"] >= 1,
        "first_win":    stats.get("total_battles_won", 0) >= 1,
        "first_evo":    stats.get("total_evolutions", 0) >= 1,
        "level_50":     stats.get("max_pet_level", 0) >= 50,
        "hatch_5":      stats.get("total_eggs_hatched", 0) >= 5,
        "breed_3":      stats.get("total_pets_bred", 0) >= 3,
        "win_10":       stats.get("total_battles_won", 0) >= 10,
        "quest_7":      stats.get("total_daily_quests_done", 0) >= 7,
        "rival_slayer": stats.get("rival_wins", 0) >= 5,
    }

    new_badges = []
    conn = get_conn()
    now  = datetime.utcnow().isoformat()
    for badge_id, met in conditions.items():
        if met and badge_id not in earned:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO achievements (user_id, badge_id, earned_at) VALUES (?,?,?)",
                    (user_id, badge_id, now),
                )
                new_badges.append(badge_id)
            except Exception:
                pass
    conn.commit()
    conn.close()
    return new_badges
