# PetWorld Discord Bot

A Discord pet raising RPG bot where all gameplay happens through slash commands. Players adopt pets, raise them, battle others, and earn coins.

## Run & Operate

- `cd petworld && python bot.py` — run the Discord bot
- Workflow: `PetWorld Bot` (console output)
- Required env: `DISCORD_BOT_TOKEN` — Discord bot token (stored as secret)

## Stack

- Python 3.11
- discord.py 2.3.2
- SQLite (via Python's built-in `sqlite3`)
- Slash commands via discord.py app_commands

## Where things live

- `petworld/bot.py` — bot entry point, cog loader, lifecycle tasks
- `petworld/data.py` — all database access (SQLite via `petworld.db`)
- `petworld/pets.py` — game constants: species, shop items, battle formulas
- `petworld/cogs/pet_commands.py` — adopt, status, feed, play, rest, train, release, mypets
- `petworld/cogs/economy.py` — daily, work, balance, shop, buy, inventory, use
- `petworld/cogs/battle.py` — battle, leaderboard
- `petworld/petworld.db` — SQLite database (auto-created on first run)

## Slash Commands

| Command | Description |
|---|---|
| `/adopt <name> <species>` | Adopt a new pet (dragon, bunny, cat, fox, penguin, wolf) |
| `/status` | Check your pet's health, hunger, happiness, energy, XP |
| `/feed [item]` | Feed your pet (free hand-feed or use an item) |
| `/play` | Play with your pet for happiness + XP |
| `/rest` | Let your pet recover energy |
| `/train` | Train your pet for XP (uses energy + hunger) |
| `/release` | Release your current pet |
| `/mypets` | View all your pets |
| `/daily` | Claim daily coin reward (20h cooldown) |
| `/work` | Send pet to work for coins (1h cooldown) |
| `/balance` | Check coin balance |
| `/shop` | Browse the item shop |
| `/buy <item>` | Buy an item |
| `/inventory` | View your items |
| `/use <item>` | Use an item on your pet |
| `/battle @user` | Battle another player's pet (10m cooldown) |
| `/leaderboard` | View top pets |

## Pet Species

- 🐉 Dragon — high XP gain, eats more food
- 🐰 Bunny — gains happiness easily
- 🐱 Cat — balanced, all-round
- 🦊 Fox — earns more coins from battles
- 🐧 Penguin — resilient, slow to tire
- 🐺 Wolf — trains fastest of all species

## Architecture decisions

- SQLite chosen for zero-config persistence; all data saved across restarts
- Time-decay system: pet stats degrade based on real hours since last action
- Slash commands only (no prefix commands needed for gameplay)
- Cogs split by domain: pet care, economy, battle
- Battle cooldowns held in-memory per session (resets on restart — acceptable tradeoff)

## User preferences

- Python + discord.py for the bot
- SQLite for data persistence
- All gameplay via slash commands

## Gotchas

- `message_content` privileged intent is disabled — bot uses slash commands only, no prefix commands
- PyNaCl warning in logs is harmless — voice features not needed
- Slash commands sync globally on startup (may take up to 1 hour to appear in all servers on first invite)
