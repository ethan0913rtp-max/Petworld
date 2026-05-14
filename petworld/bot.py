import os
import asyncio
import discord
from discord.ext import commands, tasks
from datetime import datetime
import logging

import data

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
    bot = PetWorldBot()
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
