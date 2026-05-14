import discord
from discord.ext import commands
from discord import app_commands

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


HELP_SECTIONS = {
    "🐾 Pet Care": [
        ("/adopt <name> <species>",  "Adopt a new pet (use /species to browse all 54)"),
        ("/species",                 "Browse all 54 available species with elements & rarities"),
        ("/status",                  "Check your pet's health, hunger, happiness, energy & gear"),
        ("/feed [item]",             "Feed your pet to restore hunger (hand-feed or use an item)"),
        ("/play",                    "Play with your pet — boosts happiness & XP"),
        ("/rest",                    "Let your pet rest to recover energy"),
        ("/train",                   "Train your pet for XP gains (uses energy & hunger)"),
        ("/pet",                     "Give your pet love! +happiness & XP — 30 min cooldown"),
        ("/fly",                     "**Birds only** — fly for coins, XP & found items"),
        ("/hatch",                   "Hatch your egg (24h wait or use a 💎 hatch_gem)"),
        ("/mypets",                  "See all your pets and eggs with their status"),
        ("/release",                 "Release your active pet (permanent — confirm required)"),
        ("/rename <newname>",        "Give your active pet a new name"),
    ],
    "💰 Economy": [
        ("/daily",                   "Claim daily coins (50–120) — 20h cooldown"),
        ("/work",                    "Send your pet to work for coins — 1h cooldown"),
        ("/balance",                 "Check your current coin balance"),
        ("/shop [category]",         "Browse the shop (filter: food, gear, or all)"),
        ("/buy <item>",              "Buy an item from the shop"),
        ("/inventory",               "View everything in your inventory"),
        ("/use <item>",              "Use a consumable item on your pet"),
        ("/equip <slot> <item>",     "Equip a hat / outfit / collar / accessory on your pet"),
        ("/unequip <slot>",          "Remove equipped gear (returns it to inventory)"),
    ],
    "⚔️ Battle": [
        ("/battle @user",            "Challenge another player's pet to an elemental battle!"),
        ("/leaderboard",             "Top 10 pets ranked by level and coins"),
    ],
    "🏹 Quests & Hunting": [
        ("/hunt",                    "Send your pet hunting for loot — 2h cooldown"),
        ("/quests",                  "View your daily & weekly quests and claim rewards"),
    ],
    "🌾 Farm & Breeding": [
        ("/breed @user",             "Request to breed your pet with another player's pet"),
        ("/farm",                    "View your incubating eggs and bred pets"),
    ],
    "🤝 Social": [
        ("/profile [@user]",         "View trainer profile, badges, stats, and active pet"),
        ("/trade @user <petname>",   "Offer to swap one of your pets with another player"),
    ],
    "ℹ️ Info": [
        ("/help",                    "This menu — all commands organized by category"),
    ],
}

EVOLUTION_TIP = (
    "**🌟 Evolution:** Pets evolve at Level 25 and Level 50 — "
    "gaining a new form, title, emoji, and stat boost!\n"
    "**🔥 Elements:** Each species has an element. Fire beats Ice, Water beats Fire, etc. "
    "Elemental advantage gives +50% damage in /battle.\n"
    "**🥚 Eggs:** Non-mammal pets start as eggs and hatch after 24h (or use a 💎 hatch_gem)."
)


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="View all commands, organized by category")
    @app_commands.describe(category="Optional: pet, economy, battle, quests, farm, social")
    async def help(self, interaction: discord.Interaction, category: str = None):
        category = (category or "").lower().strip()

        # Map shorthand category names to section titles
        CAT_MAP = {
            "pet":     "🐾 Pet Care",
            "care":    "🐾 Pet Care",
            "economy": "💰 Economy",
            "shop":    "💰 Economy",
            "battle":  "⚔️ Battle",
            "quests":  "🏹 Quests & Hunting",
            "hunt":    "🏹 Quests & Hunting",
            "farm":    "🌾 Farm & Breeding",
            "breed":   "🌾 Farm & Breeding",
            "social":  "🤝 Social",
            "info":    "ℹ️ Info",
        }
        target_section = CAT_MAP.get(category)

        if target_section and target_section in HELP_SECTIONS:
            # Single section view
            embed = discord.Embed(
                title=f"📖 Commands — {target_section}",
                color=discord.Color.teal()
            )
            cmds = HELP_SECTIONS[target_section]
            lines = [f"`{cmd}` — {desc}" for cmd, desc in cmds]
            embed.description = "\n".join(lines)
            embed.set_footer(text="Use /help to see all categories.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Full help overview
        embed = discord.Embed(
            title="📖 PetWorld — Full Command Reference",
            description="Use `/help <category>` for a focused view (e.g. `/help battle`).",
            color=discord.Color.teal()
        )
        for section, cmds in HELP_SECTIONS.items():
            lines = [f"`{cmd}` — {desc}" for cmd, desc in cmds]
            embed.add_field(name=section, value="\n".join(lines), inline=False)

        embed.add_field(name="💡 Quick Tips", value=EVOLUTION_TIP, inline=False)
        embed.set_footer(text="PetWorld 🐾 — adopt, raise, battle, evolve!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
