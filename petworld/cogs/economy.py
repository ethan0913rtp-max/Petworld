import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data
import pets as pet_lib


DAILY_COOLDOWN_HOURS = 20
WORK_COOLDOWN_HOURS = 1

# Track cooldowns in-memory (resets on restart; use DB for persistence in prod)
_daily_cooldowns: dict[str, datetime] = {}
_work_cooldowns: dict[str, datetime] = {}


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def ensure_player(self, user: discord.User):
        if not data.get_player(str(user.id)):
            data.create_player(str(user.id), user.name)

    @app_commands.command(name="daily", description="Claim your daily coin reward!")
    async def daily(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        self.ensure_player(interaction.user)

        last = _daily_cooldowns.get(user_id)
        if last:
            diff = datetime.utcnow() - last
            if diff < timedelta(hours=DAILY_COOLDOWN_HOURS):
                remaining = timedelta(hours=DAILY_COOLDOWN_HOURS) - diff
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes = remainder // 60
                await interaction.response.send_message(
                    f"⏰ You already claimed today's reward! Come back in **{hours}h {minutes}m**.",
                    ephemeral=True
                )
                return

        reward = random.randint(50, 120)
        player = data.get_player(user_id)
        new_coins = player["coins"] + reward
        data.update_player(user_id, coins=new_coins)
        _daily_cooldowns[user_id] = datetime.utcnow()

        embed = discord.Embed(
            title="🎁 Daily Reward Claimed!",
            description=f"You received **{reward} coins** 💰",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Total Coins", value=f"💰 {new_coins}", inline=True)
        embed.set_footer(text="Come back tomorrow for more!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Send your pet to work for coins")
    async def work(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        self.ensure_player(interaction.user)

        pet = data.get_active_pet(user_id)
        if not pet:
            await interaction.response.send_message("❌ You need a pet to work! Use `/adopt`.", ephemeral=True)
            return

        last = _work_cooldowns.get(user_id)
        if last:
            diff = datetime.utcnow() - last
            if diff < timedelta(hours=WORK_COOLDOWN_HOURS):
                remaining = timedelta(hours=WORK_COOLDOWN_HOURS) - diff
                minutes = int(remaining.total_seconds() / 60)
                await interaction.response.send_message(
                    f"⏰ Your pet is still tired from working! Rest in **{minutes}m**.", ephemeral=True
                )
                return

        pet = pet_lib.apply_time_decay(pet)
        if pet["energy"] < 15:
            await interaction.response.send_message("😴 Your pet has no energy to work! Use `/rest` first.", ephemeral=True)
            return

        base_pay = random.randint(15, 40)
        level_bonus = pet["level"] * 3
        pay = base_pay + level_bonus
        energy_cost = random.randint(15, 25)

        player = data.get_player(user_id)
        new_coins = player["coins"] + pay
        new_energy = pet_lib.clamp(pet["energy"] - energy_cost)
        data.update_player(user_id, coins=new_coins)
        data.update_pet(pet["pet_id"], energy=new_energy)
        _work_cooldowns[user_id] = datetime.utcnow()

        jobs = [
            f"**{pet['name']}** delivered packages around the city 📦",
            f"**{pet['name']}** helped at a bakery 🥐",
            f"**{pet['name']}** performed street magic 🎩",
            f"**{pet['name']}** guarded a treasure vault 🏛️",
            f"**{pet['name']}** won a talent show 🎤",
        ]

        embed = discord.Embed(
            title="💼 Work Complete!",
            description=random.choice(jobs),
            color=discord.Color.green()
        )
        embed.add_field(name="💰 Earned", value=f"+{pay} coins (Level {pet['level']} bonus: +{level_bonus})", inline=False)
        embed.add_field(name="⚡ Energy", value=f"-{energy_cost}", inline=True)
        embed.add_field(name="Total Coins", value=str(new_coins), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="balance", description="Check your coin balance")
    async def balance(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        self.ensure_player(interaction.user)
        player = data.get_player(user_id)
        embed = discord.Embed(
            title=f"💰 {interaction.user.display_name}'s Balance",
            description=f"**{player['coins']} coins**",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shop", description="Browse the item shop")
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🏪 PetWorld Shop",
            description="Use `/buy <item>` to purchase! Items are used with `/feed` or `/use`.",
            color=discord.Color.teal()
        )
        for item_name, item in pet_lib.SHOP_ITEMS.items():
            effects = []
            if "hunger" in item:
                effects.append(f"+{item['hunger']} Hunger")
            if "happiness" in item:
                effects.append(f"+{item['happiness']} Happiness")
            if "health" in item:
                effects.append(f"+{item['health']} Health")
            if "energy" in item:
                effects.append(f"+{item['energy']} Energy")
            embed.add_field(
                name=f"{item['emoji']} {item_name.replace('_', ' ').title()} — {item['cost']} 💰",
                value=f"{item['description']}\nEffect: {', '.join(effects)}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item="Item name to buy")
    async def buy(self, interaction: discord.Interaction, item: str):
        item = item.lower().replace(" ", "_")
        user_id = str(interaction.user.id)
        self.ensure_player(interaction.user)

        item_data = pet_lib.SHOP_ITEMS.get(item)
        if not item_data:
            await interaction.response.send_message(f"❌ `{item}` not found in shop. Use `/shop` to browse.", ephemeral=True)
            return

        player = data.get_player(user_id)
        if player["coins"] < item_data["cost"]:
            await interaction.response.send_message(
                f"❌ Not enough coins! You have **{player['coins']}** but need **{item_data['cost']}**.",
                ephemeral=True
            )
            return

        data.update_player(user_id, coins=player["coins"] - item_data["cost"])
        data.add_item(user_id, item)

        embed = discord.Embed(
            title=f"🛒 Purchased {item_data['emoji']} {item.replace('_', ' ').title()}!",
            description=f"Spent **{item_data['cost']} coins**",
            color=discord.Color.green()
        )
        embed.add_field(name="Remaining Coins", value=str(player["coins"] - item_data["cost"]), inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="inventory", description="Check your item inventory")
    async def inventory(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        self.ensure_player(interaction.user)
        inv = data.get_inventory(user_id)

        if not inv:
            await interaction.response.send_message("🎒 Your inventory is empty. Visit `/shop` to buy items!", ephemeral=True)
            return

        embed = discord.Embed(title="🎒 Your Inventory", color=discord.Color.blue())
        for item_name, qty in inv.items():
            item_data = pet_lib.SHOP_ITEMS.get(item_name, {})
            emoji = item_data.get("emoji", "📦")
            embed.add_field(
                name=f"{emoji} {item_name.replace('_', ' ').title()}",
                value=f"Quantity: {qty}",
                inline=True
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="use", description="Use an item from your inventory on your pet")
    @app_commands.describe(item="Item to use")
    async def use(self, interaction: discord.Interaction, item: str):
        item = item.lower().replace(" ", "_")
        user_id = str(interaction.user.id)

        pet = data.get_active_pet(user_id)
        if not pet:
            await interaction.response.send_message("❌ You need a pet first! Use `/adopt`.", ephemeral=True)
            return

        item_data = pet_lib.SHOP_ITEMS.get(item)
        if not item_data:
            await interaction.response.send_message(f"❌ Unknown item `{item}`.", ephemeral=True)
            return

        if not data.remove_item(user_id, item):
            await interaction.response.send_message(f"❌ You don't have any `{item}` in your inventory.", ephemeral=True)
            return

        pet = pet_lib.apply_time_decay(pet)
        updates = {}
        effects = []

        for stat in ["hunger", "happiness", "health", "energy"]:
            if stat in item_data:
                old = pet[stat]
                new = pet_lib.clamp(old + item_data[stat])
                updates[stat] = new
                effects.append(f"{stat.capitalize()}: +{item_data[stat]} → {new}%")

        if updates:
            data.update_pet(pet["pet_id"], **updates)

        embed = discord.Embed(
            title=f"{item_data['emoji']} Used {item.replace('_', ' ').title()} on {pet['name']}!",
            description="\n".join(effects),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))
