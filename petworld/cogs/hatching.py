import discord
from discord.ext import commands
from discord import app_commands

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data
import pets as pet_lib


class Hatching(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hatch", description="Hatch your egg! Requires 24 hours or a hatch_gem.")
    async def hatch(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        # Find the oldest ready egg or an unhatched egg
        eggs = data.get_all_eggs(user_id)
        if not eggs:
            # Maybe their active pet is already hatched
            pet = data.get_active_pet(user_id)
            if pet:
                await interaction.response.send_message(
                    f"🐾 **{pet['name']}** is already hatched and active!", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ You don't have any eggs to hatch. Use `/adopt` to get a pet!", ephemeral=True
                )
            return

        # Prioritise eggs that are ready
        ready_eggs = [e for e in eggs if pet_lib.egg_hours_remaining(e["created_at"]) <= 0]
        waiting_eggs = [e for e in eggs if pet_lib.egg_hours_remaining(e["created_at"]) > 0]

        egg = ready_eggs[0] if ready_eggs else waiting_eggs[0]
        hrs_left = pet_lib.egg_hours_remaining(egg["created_at"])

        if hrs_left > 0:
            # Check if player has a hatch_gem
            inv = data.get_inventory(user_id)
            if inv.get("hatch_gem", 0) > 0:
                view = HatchGemView(egg, hrs_left)
                h = int(hrs_left)
                m = int((hrs_left - h) * 60)
                await interaction.response.send_message(
                    f"🥚 **{egg['name']}** still needs **{h}h {m}m** to hatch.\n"
                    f"You have a 💎 **hatch_gem** — use it to hatch instantly?",
                    view=view, ephemeral=True
                )
            else:
                h = int(hrs_left)
                m = int((hrs_left - h) * 60)
                await interaction.response.send_message(
                    f"⏳ **{egg['name']}** needs **{h}h {m}m** more to hatch.\n"
                    f"Buy a 💎 `hatch_gem` from `/shop` to skip the wait!",
                    ephemeral=True
                )
            return

        await _do_hatch(interaction, egg, used_gem=False)


async def _do_hatch(interaction: discord.Interaction, egg: dict, used_gem: bool):
    user_id = str(interaction.user.id)

    if used_gem:
        if not data.remove_item(user_id, "hatch_gem"):
            await interaction.response.send_message("❌ Could not use hatch_gem — item not found.", ephemeral=True)
            return

    # Hatch the egg: set is_egg=0 and reset timestamps
    from datetime import datetime
    now = datetime.utcnow().isoformat()
    data.update_pet(egg["pet_id"], is_egg=0, last_fed=now, last_played=now, last_rested=now, last_trained=now)
    data.increment_stat(user_id, "total_eggs_hatched")

    s_data  = pet_lib.SPECIES.get(egg["species"], {})
    elem_e  = pet_lib.ELEMENT_COLORS.get(s_data.get("element", ""), "")
    rar_e   = pet_lib.RARITY_EMOJI.get(egg.get("rarity", "common"), "⚪")

    embed = discord.Embed(
        title=f"🎊 {egg['name']} has hatched!",
        description=f"Your {s_data.get('emoji','🐾')} **{egg['species'].capitalize()}** is ready to adventure!",
        color=discord.Color.green()
    )
    embed.add_field(name="Element",  value=f"{elem_e} {s_data.get('element', '?')}", inline=True)
    embed.add_field(name="Rarity",   value=f"{rar_e} {egg.get('rarity','common').capitalize()}", inline=True)
    embed.add_field(name="Trait",    value=s_data.get("description", ""), inline=False)

    new_badges = data.check_and_award_achievements(user_id)
    for badge in new_badges:
        b = data.BADGE_INFO.get(badge, {})
        embed.add_field(name="🏅 Badge Unlocked!", value=f"{b.get('emoji','')} **{b.get('label', badge)}** — _{b.get('desc','')}_", inline=False)

    if used_gem:
        embed.set_footer(text="💎 Hatch Gem used!")
    else:
        embed.set_footer(text="Use /status to check on your new pet!")

    if interaction.response.is_done():
        await interaction.followup.send(embed=embed)
    else:
        await interaction.response.send_message(embed=embed)


class HatchGemView(discord.ui.View):
    def __init__(self, egg: dict, hrs_left: float):
        super().__init__(timeout=30)
        self.egg      = egg
        self.hrs_left = hrs_left

    @discord.ui.button(label="💎 Use Hatch Gem", style=discord.ButtonStyle.success)
    async def use_gem(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Hatching…", view=None)
        await _do_hatch(interaction, self.egg, used_gem=True)

    @discord.ui.button(label="Wait it out", style=discord.ButtonStyle.secondary)
    async def wait(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="OK! Come back when the egg is ready.", view=None)


async def setup(bot):
    await bot.add_cog(Hatching(bot))
