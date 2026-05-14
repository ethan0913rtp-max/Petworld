import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "petworld.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            coins INTEGER DEFAULT 100,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            pet_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            name TEXT,
            species TEXT,
            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,
            hunger INTEGER DEFAULT 100,
            happiness INTEGER DEFAULT 100,
            health INTEGER DEFAULT 100,
            energy INTEGER DEFAULT 100,
            age_days INTEGER DEFAULT 0,
            last_fed TEXT,
            last_played TEXT,
            last_rested TEXT,
            last_trained TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES players(user_id)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            item_name TEXT,
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES players(user_id)
        )
    """)
    conn.commit()
    conn.close()

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
        (user_id, username, 100, now)
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

def get_active_pet(user_id: str):
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM pets WHERE user_id=? AND is_active=1 ORDER BY pet_id DESC LIMIT 1",
        (user_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_pets(user_id: str):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM pets WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_pet(user_id: str, name: str, species: str):
    conn = get_conn()
    now = datetime.utcnow().isoformat()
    conn.execute(
        """INSERT INTO pets (user_id, name, species, level, xp, hunger, happiness, health, energy,
           age_days, last_fed, last_played, last_rested, last_trained, is_active, created_at)
           VALUES (?,?,?,1,0,100,100,100,100,0,?,?,?,?,1,?)""",
        (user_id, name, species, now, now, now, now, now)
    )
    conn.commit()
    conn.close()

def update_pet(pet_id: int, **kwargs):
    if not kwargs:
        return
    fields = ", ".join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) + [pet_id]
    conn = get_conn()
    conn.execute(f"UPDATE pets SET {fields} WHERE pet_id=?", values)
    conn.commit()
    conn.close()

def get_inventory(user_id: str):
    conn = get_conn()
    rows = conn.execute(
        "SELECT item_name, quantity FROM inventory WHERE user_id=? AND quantity > 0",
        (user_id,)
    ).fetchall()
    conn.close()
    return {r["item_name"]: r["quantity"] for r in rows}

def add_item(user_id: str, item_name: str, quantity: int = 1):
    conn = get_conn()
    existing = conn.execute(
        "SELECT id, quantity FROM inventory WHERE user_id=? AND item_name=?",
        (user_id, item_name)
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE inventory SET quantity=? WHERE id=?",
            (existing["quantity"] + quantity, existing["id"])
        )
    else:
        conn.execute(
            "INSERT INTO inventory (user_id, item_name, quantity) VALUES (?,?,?)",
            (user_id, item_name, quantity)
        )
    conn.commit()
    conn.close()

def remove_item(user_id: str, item_name: str, quantity: int = 1) -> bool:
    conn = get_conn()
    existing = conn.execute(
        "SELECT id, quantity FROM inventory WHERE user_id=? AND item_name=?",
        (user_id, item_name)
    ).fetchone()
    if not existing or existing["quantity"] < quantity:
        conn.close()
        return False
    conn.execute(
        "UPDATE inventory SET quantity=? WHERE id=?",
        (existing["quantity"] - quantity, existing["id"])
    )
    conn.commit()
    conn.close()
    return True

def get_leaderboard(limit: int = 10):
    conn = get_conn()
    rows = conn.execute(
        """SELECT p.username, p.coins, pet.name as pet_name, pet.level, pet.species
           FROM players p
           LEFT JOIN pets pet ON pet.user_id = p.user_id AND pet.is_active = 1
           ORDER BY pet.level DESC, p.coins DESC
           LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
