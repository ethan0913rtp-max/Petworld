import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data
import pets as pet_lib

_hunt_cooldowns: dict[str, datetime] = {}
HUNT_COOLDOWN_HOURS = 2


class Hunting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hunt", description="Send your pet hunting for food and rare items! (2h cooldown)")
    async def hunt(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)

        if not pet:
            msg = "🥚 Your pet hasn't hatched yet! Use `/hatch` first." if data.get_active_pet_or_egg(user_id) else "❌ You don't have a pet! Use `/adopt`."
            await interaction.response.send_message(msg, ephemeral=True)
            return

        last = _hunt_cooldowns.get(user_id)
        if last and (datetime.utcnow() - last) < timedelta(hours=HUNT_COOLDOWN_HOURS):
            remaining = timedelta(hours=HUNT_COOLDOWN_HOURS) - (datetime.utcnow() - last)
            h  = int(remaining.total_seconds() // 3600)
            m  = int((remaining.total_seconds() % 3600) // 60)
            await interaction.response.send_message(
                f"⏰ **{pet['name']}** is still resting from the last hunt! Ready in **{h}h {m}m**.",
                ephemeral=True
            )
            return

        pet = pet_lib.apply_time_decay(pet)
        if pet["energy"] < 15:
            await interaction.response.send_message(f"😴 **{pet['name']}** has no energy to hunt! Use `/rest` first.", ephemeral=True)
            return

        _hunt_cooldowns[user_id] = datetime.utcnow()

        species_data = pet_lib.SPECIES.get(pet["species"], pet_lib.SPECIES["cat"])
        element      = species_data["element"]
        level        = pet["level"]
        loot_data    = pet_lib.HUNT_LOOT.get(element, pet_lib.HUNT_LOOT["Fire"])

        # Determine rarity tier (higher level improves chances)
        jackpot_chance  = min(0.05 + level * 0.005, 0.15)
        rare_chance     = min(0.15 + level * 0.01,  0.35)
        uncommon_chance = min(0.35 + level * 0.01,  0.55)

        roll = random.random()
        if roll < jackpot_chance:
            tier, tier_label = "jackpot", "💎 JACKPOT"
            tier_color = discord.Color.from_rgb(255, 215, 0)
        elif roll < jackpot_chance + rare_chance:
            tier, tier_label = "rare", "🔵 Rare Find"
            tier_color = discord.Color.blue()
        elif roll < jackpot_chance + rare_chance + uncommon_chance:
            tier, tier_label = "uncommon", "🟢 Good Haul"
            tier_color = discord.Color.green()
        else:
            tier, tier_label = "common", "⚪ Basic Haul"
            tier_color = discord.Color.greyple()

        found_items  = []
        coin_gain    = random.randint(*loot_data["coin_range"][tier]) + level * 2
        energy_cost  = random.randint(15, 25)

        item_pool = loot_data[tier]
        if item_pool:
            n_items = 2 if tier in ("rare", "jackpot") else 1
            for _ in range(n_items):
                item = random.choice(item_pool)
                data.add_item(user_id, item)
                found_items.append(item)

        player = data.get_player(user_id)
        data.update_player(user_id, coins=player["coins"] + coin_gain)
        data.update_pet(pet["pet_id"], energy=pet_lib.clamp(pet["energy"] - energy_cost))

        # Quest tracking
        completed = data.track_quest_action(user_id, "hunt")

        elem_emoji = pet_lib.ELEMENT_COLORS.get(element, "")
        adventure  = random.choice(loot_data["flavor_lines"])

        embed = discord.Embed(
            title=f"🏹 {tier_label} — {species_data['emoji']} {pet['name']} went hunting!",
            description=f"*{adventure}*",
            color=tier_color
        )
        embed.add_field(name=f"{elem_emoji} Territory", value=loot_data["territory"], inline=True)
        embed.add_field(name="💰 Coins",  value=f"+{coin_gain}", inline=True)
        embed.add_field(name="⚡ Energy", value=f"-{energy_cost}", inline=True)

        if found_items:
            item_lines = []
            for item_name in found_items:
                item_d = pet_lib.SHOP_ITEMS.get(item_name, {})
                item_lines.append(f"{item_d.get('emoji','📦')} {item_name.replace('_',' ').title()}")
            embed.add_field(name="🎒 Items Found", value="\n".join(item_lines), inline=False)
        else:
            embed.add_field(name="🎒 Items Found", value="Nothing this time…", inline=False)

        for quest in completed:
            embed.add_field(
                name="✅ Quest Complete!",
                value=f"**{quest['description']}** — use `/quests` to claim your reward!",
                inline=False
            )

        embed.set_footer(text=f"Next hunt available in {HUNT_COOLDOWN_HOURS}h")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Hunting(bot))
