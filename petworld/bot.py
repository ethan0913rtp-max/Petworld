import os
import asyncio
import discord
from discord.ext import commands, tasks
from datetime import datetime
import logging

import data
from keep_alive import keep_alive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("petworld")

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN environment variable is not set!")

COGS = [
    "cogs.pet_commands",
    "cogs.economy",
    "cogs.battle",
    "cogs.hatching",
    "cogs.breeding",
    "cogs.hunting",
    "cogs.quests_cog",
    "cogs.profile",
    "cogs.social",
    "cogs.help_cmd",
]


class PetWorldBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = False
        intents.members = False
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        for cog in COGS:
            try:
                await self.load_extension(cog)
                log.info(f"Loaded cog: {cog}")
            except Exception as e:
                log.error(f"Failed to load cog {cog}: {e}", exc_info=True)

        log.info("Syncing slash commands globally…")
        await self.tree.sync()
        log.info("Slash commands synced.")
        self.age_pets_task.start()

    async def on_ready(self):
        log.info(f"PetWorld online as {self.user} (ID: {self.user.id})")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing,
                name="PetWorld RPG 🐾 | /adopt to start!"
            )
        )

    async def on_guild_join(self, guild: discord.Guild):
        """Send a welcome embed when the bot is added to a new server."""
        channel = None
        # Prefer a channel named general/welcome/bot-commands; fall back to first writable channel
        preferred = ("general", "welcome", "bot-commands", "bot", "bots")
        for name in preferred:
            ch = discord.utils.get(guild.text_channels, name=name)
            if ch and ch.permissions_for(guild.me).send_messages:
                channel = ch
                break
        if channel is None:
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    channel = ch
                    break
        if channel is None:
            return

        embed = discord.Embed(
            title="🐾 Welcome to PetWorld!",
            description=(
                "PetWorld is a pet-raising RPG that lives entirely inside Discord.\n"
                "Adopt a pet, raise it, battle other trainers, evolve, breed, hunt for treasure — all via slash commands!"
            ),
            color=discord.Color.from_rgb(100, 200, 150)
        )
        embed.add_field(
            name="🚀 Getting Started",
            value=(
                "`/adopt <name> <species>` — Adopt your first pet\n"
                "`/species` — Browse all 54 available species\n"
                "`/status` — Check your pet's stats\n"
                "`/help` — Full command reference"
            ),
            inline=False
        )
        embed.add_field(
            name="⚔️ Core Gameplay",
            value=(
                "`/feed` `/play` `/rest` `/train` — Care for your pet daily\n"
                "`/battle @user` — Challenge other trainers\n"
                "`/hunt` — Send your pet on a 2h treasure hunt\n"
                "`/quests` — Daily & weekly quests for big rewards"
            ),
            inline=False
        )
        embed.add_field(
            name="🌱 Advanced",
            value=(
                "`/breed @user` — Breed rare pets with other players\n"
                "`/hatch` — Hatch eggs into powerful creatures\n"
                "`/shop` — Gear up with hats, outfits & power items\n"
                "`/profile` — View badges, stats & rival record"
            ),
            inline=False
        )
        embed.add_field(
            name="🐉 54 Species · 8 Elements · Evolutions at Lv.25 & 50",
            value="Every species has a unique element, rarity, and evolution path. Which will you choose?",
            inline=False
        )
        embed.set_footer(text="Use /adopt to begin your journey! Good luck, Trainer 🎮")
        try:
            await channel.send(embed=embed)
            log.info(f"Sent welcome message to #{channel.name} in {guild.name}")
        except Exception as e:
            log.warning(f"Could not send welcome to {guild.name}: {e}")

    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        log.error(f"Command error in {interaction.command}: {error}", exc_info=True)
        if not interaction.response.is_done():
            await interaction.response.send_message("❌ An error occurred. Please try again!", ephemeral=True)

    @tasks.loop(hours=24)
    async def age_pets_task(self):
        conn = data.get_conn()
        conn.execute("UPDATE pets SET age_days = age_days + 1 WHERE is_active = 1 AND is_egg = 0")
        conn.commit()
        conn.close()
        log.info("Pet ages incremented.")

    @age_pets_task.before_loop
    async def before_age_task(self):
        await self.wait_until_ready()


async def main():
    data.init_db()
    log.info("Database initialised.")
    keep_alive(port=5000)
    bot = PetWorldBot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
