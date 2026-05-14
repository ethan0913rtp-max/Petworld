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
WORK_COOLDOWN_HOURS  = 1

_daily_cooldowns: dict[str, datetime] = {}
_work_cooldowns:  dict[str, datetime] = {}


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
        if last and (datetime.utcnow() - last) < timedelta(hours=DAILY_COOLDOWN_HOURS):
            remaining = timedelta(hours=DAILY_COOLDOWN_HOURS) - (datetime.utcnow() - last)
            h, m = divmod(int(remaining.total_seconds()), 3600)
            await interaction.response.send_message(
                f"⏰ Come back in **{h}h {m//60}m** for your next daily!", ephemeral=True
            )
            return

        reward = random.randint(50, 120)
        player = data.get_player(user_id)
        data.update_player(user_id, coins=player["coins"] + reward)
        _daily_cooldowns[user_id] = datetime.utcnow()

        embed = discord.Embed(title="🎁 Daily Reward!", description=f"You received **{reward} coins** 💰", color=discord.Color.yellow())
        embed.add_field(name="Total Coins", value=f"💰 {player['coins'] + reward}", inline=True)
        embed.set_footer(text="Come back tomorrow for more!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="work", description="Send your pet to work for coins")
    async def work(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        self.ensure_player(interaction.user)

        pet = data.get_active_pet(user_id)
        if not pet:
            msg = "🥚 Your pet hasn't hatched yet!" if data.get_active_pet_or_egg(user_id) else "❌ You need a pet first!"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        last = _work_cooldowns.get(user_id)
        if last and (datetime.utcnow() - last) < timedelta(hours=WORK_COOLDOWN_HOURS):
            remaining = timedelta(hours=WORK_COOLDOWN_HOURS) - (datetime.utcnow() - last)
            mins = int(remaining.total_seconds() / 60)
            await interaction.response.send_message(f"⏰ Rest in **{mins}m** before working again.", ephemeral=True)
            return

        pet = pet_lib.apply_time_decay(pet)
        if pet["energy"] < 15:
            await interaction.response.send_message("😴 Your pet has no energy! Use `/rest` first.", ephemeral=True)
            return

        equip        = pet.get("equipment") or {}
        base_pay     = random.randint(15, 40)
        level_bonus  = pet["level"] * 3
        collar_bonus = int((base_pay + level_bonus) * 0.20) if equip.get("collar") == "gold_collar" else 0
        if pet["species"] == "bee":
            collar_bonus += int((base_pay + level_bonus) * 0.15)

        pay         = base_pay + level_bonus + collar_bonus
        energy_cost = random.randint(15, 25)
        player      = data.get_player(user_id)
        data.update_player(user_id, coins=player["coins"] + pay)
        data.update_pet(pet["pet_id"], energy=pet_lib.clamp(pet["energy"] - energy_cost))
        _work_cooldowns[user_id] = datetime.utcnow()

        completed = data.track_quest_action(user_id, "work")

        jobs = [
            f"**{pet['name']}** delivered packages around the city 📦",
            f"**{pet['name']}** helped at a bakery 🥐",
            f"**{pet['name']}** performed street magic 🎩",
            f"**{pet['name']}** guarded a treasure vault 🏛️",
            f"**{pet['name']}** won a talent show 🎤",
        ]
        evo_emoji, _ = pet_lib.get_evo_display(pet["species"], pet.get("evo_stage", 0))
        embed = discord.Embed(title="💼 Work Complete!", description=random.choice(jobs), color=discord.Color.green())
        embed.add_field(name="💰 Earned", value=f"+{pay} coins", inline=True)
        embed.add_field(name="⚡ Energy", value=f"-{energy_cost}", inline=True)
        embed.add_field(name="Total",     value=str(player["coins"] + pay), inline=True)
        if collar_bonus:
            embed.set_footer(text=f"🏅 Collar bonus included: +{collar_bonus} coins!")
        for q in completed:
            embed.add_field(name="✅ Quest Complete!", value=f"**{q['description']}** — `/quests` to claim!", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="balance", description="Check your coin balance")
    async def balance(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        self.ensure_player(interaction.user)
        player = data.get_player(user_id)
        embed  = discord.Embed(
            title=f"💰 {interaction.user.display_name}'s Balance",
            description=f"**{player['coins']} coins**",
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shop", description="Browse the full PetWorld item shop")
    @app_commands.describe(category="Filter: all, food, gear")
    async def shop(self, interaction: discord.Interaction, category: str = "all"):
        category = category.lower()

        def include(idata):
            t = idata.get("type", "consumable")
            if category == "food":  return t == "consumable"
            if category == "gear":  return t in ("hat", "outfit", "collar", "accessory")
            return True

        embed = discord.Embed(
            title="🏪 PetWorld Shop",
            description="Buy with `/buy <item>` · Equip gear with `/equip <slot> <item>`",
            color=discord.Color.teal()
        )
        sections = {
            "🍽️ Food & Consumables": "consumable",
            "🎩 Hats":               "hat",
            "👗 Outfits":            "outfit",
            "📿 Collars":            "collar",
            "💍 Accessories":        "accessory",
        }
        for section_name, section_type in sections.items():
            items_in_section = [(k, v) for k, v in pet_lib.SHOP_ITEMS.items()
                                if v.get("type") == section_type and include(v)]
            if not items_in_section:
                continue
            lines = []
            for item_name, item in items_in_section:
                effects = [f"+{item[s]} {s.capitalize()}" for s in ("hunger","happiness","health","energy") if s in item]
                eff_str = f" → {', '.join(effects)}" if effects else ""
                lines.append(f"{item['emoji']} **{item_name.replace('_',' ').title()}** — {item['cost']}💰{eff_str}\n  _{item['description']}_")
            embed.add_field(name=section_name, value="\n".join(lines), inline=False)
        embed.set_footer(text="Use /shop food or /shop gear to filter.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="Buy an item from the shop")
    @app_commands.describe(item="Item name to buy (e.g. top_hat, armor, apple)")
    async def buy(self, interaction: discord.Interaction, item: str):
        item    = item.lower().replace(" ", "_")
        user_id = str(interaction.user.id)
        self.ensure_player(interaction.user)

        item_data = pet_lib.SHOP_ITEMS.get(item)
        if not item_data:
            await interaction.response.send_message(f"❌ `{item}` not found. Use `/shop` to browse.", ephemeral=True)
            return

        player = data.get_player(user_id)
        if player["coins"] < item_data["cost"]:
            await interaction.response.send_message(
                f"❌ Need **{item_data['cost']}** coins but you have **{player['coins']}**.", ephemeral=True
            )
            return

        data.update_player(user_id, coins=player["coins"] - item_data["cost"])
        data.add_item(user_id, item)

        embed = discord.Embed(
            title=f"🛒 Purchased {item_data['emoji']} {item.replace('_',' ').title()}!",
            description=item_data["description"],
            color=discord.Color.green()
        )
        embed.add_field(name="Cost",            value=f"{item_data['cost']} 💰", inline=True)
        embed.add_field(name="Remaining Coins", value=str(player["coins"] - item_data["cost"]), inline=True)
        if item_data.get("type") in pet_lib.EQUIP_SLOTS:
            embed.set_footer(text=f"Use /equip {item_data['type']} {item} to put it on your pet!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="inventory", description="Check your item inventory")
    async def inventory(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        self.ensure_player(interaction.user)
        inv = data.get_inventory(user_id)
        if not inv:
            await interaction.response.send_message("🎒 Your inventory is empty. Visit `/shop`!", ephemeral=True)
            return

        consumables, gear = [], []
        for item_name, qty in inv.items():
            idata = pet_lib.SHOP_ITEMS.get(item_name, {})
            entry = f"{idata.get('emoji','📦')} **{item_name.replace('_',' ').title()}** ×{qty}"
            (consumables if idata.get("type") == "consumable" else gear).append(entry)

        embed = discord.Embed(title="🎒 Your Inventory", color=discord.Color.blue())
        if consumables:
            embed.add_field(name="🍽️ Consumables", value="\n".join(consumables), inline=False)
        if gear:
            embed.add_field(name="👗 Gear", value="\n".join(gear), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="use", description="Use a consumable item on your pet")
    @app_commands.describe(item="Item to use")
    async def use(self, interaction: discord.Interaction, item: str):
        item    = item.lower().replace(" ", "_")
        user_id = str(interaction.user.id)
        pet     = data.get_active_pet(user_id)
        if not pet:
            msg = "🥚 Your pet hasn't hatched yet!" if data.get_active_pet_or_egg(user_id) else "❌ You need a pet!"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        item_data = pet_lib.SHOP_ITEMS.get(item)
        if not item_data or item_data.get("type") != "consumable":
            await interaction.response.send_message(f"❌ `{item}` isn't a usable consumable. Try `/equip` for gear.", ephemeral=True)
            return
        if item_data.get("hatch"):
            await interaction.response.send_message("💎 Use `/hatch` to use your hatch_gem!", ephemeral=True)
            return
        if not data.remove_item(user_id, item):
            await interaction.response.send_message(f"❌ No `{item}` in inventory.", ephemeral=True)
            return

        pet = pet_lib.apply_time_decay(pet)
        updates, effects = {}, []
        for stat in ("hunger", "happiness", "health", "energy"):
            if stat in item_data:
                new_val = pet_lib.clamp(pet[stat] + item_data[stat])
                updates[stat] = new_val
                effects.append(f"{stat.capitalize()}: +{item_data[stat]} → {new_val}%")
        if updates:
            data.update_pet(pet["pet_id"], **updates)

        embed = discord.Embed(
            title=f"{item_data['emoji']} Used {item.replace('_',' ').title()} on {pet['name']}!",
            description="\n".join(effects),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="equip", description="Equip a clothing or accessory item on your pet")
    @app_commands.describe(slot="Slot: hat, outfit, collar, or accessory", item="Item name to equip")
    async def equip(self, interaction: discord.Interaction, slot: str, item: str):
        slot    = slot.lower()
        item    = item.lower().replace(" ", "_")
        user_id = str(interaction.user.id)

        if slot not in pet_lib.EQUIP_SLOTS:
            await interaction.response.send_message(
                f"❌ Invalid slot. Valid: {', '.join(f'`{s}`' for s in pet_lib.EQUIP_SLOTS)}", ephemeral=True
            )
            return

        pet = data.get_active_pet(user_id)
        if not pet:
            msg = "🥚 Your pet hasn't hatched yet!" if data.get_active_pet_or_egg(user_id) else "❌ You need a hatched pet!"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        item_data = pet_lib.SHOP_ITEMS.get(item)
        if not item_data:
            await interaction.response.send_message(f"❌ Unknown item `{item}`.", ephemeral=True)
            return
        if item_data.get("type") != slot:
            await interaction.response.send_message(
                f"❌ `{item}` is a **{item_data.get('type','?')}**, not a **{slot}**.", ephemeral=True
            )
            return
        if data.get_inventory(user_id).get(item, 0) < 1:
            await interaction.response.send_message(f"❌ You don't own `{item}`. Buy it from `/shop` first!", ephemeral=True)
            return

        equip    = pet.get("equipment") or {}
        old_item = equip.get(slot)
        if old_item:
            data.add_item(user_id, old_item)
        equip[slot] = item
        data.remove_item(user_id, item)
        data.update_pet(pet["pet_id"], equipment=equip)

        embed = discord.Embed(
            title=f"👗 {pet['name']} is now wearing {item_data['emoji']} {item.replace('_',' ').title()}!",
            description=item_data["description"],
            color=discord.Color.from_rgb(255, 182, 193)
        )
        if old_item:
            old_d = pet_lib.SHOP_ITEMS.get(old_item, {})
            embed.set_footer(text=f"Previous {slot} ({old_d.get('emoji','')} {old_item.replace('_',' ').title()}) returned to inventory.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unequip", description="Remove an equipped item from your pet")
    @app_commands.describe(slot="Slot to unequip: hat, outfit, collar, or accessory")
    async def unequip(self, interaction: discord.Interaction, slot: str):
        slot    = slot.lower()
        user_id = str(interaction.user.id)
        if slot not in pet_lib.EQUIP_SLOTS:
            await interaction.response.send_message(
                f"❌ Invalid slot. Valid: {', '.join(f'`{s}`' for s in pet_lib.EQUIP_SLOTS)}", ephemeral=True
            )
            return
        pet = data.get_active_pet(user_id)
        if not pet:
            await interaction.response.send_message("❌ You need a hatched pet!", ephemeral=True)
            return
        equip    = pet.get("equipment") or {}
        old_item = equip.get(slot)
        if not old_item:
            await interaction.response.send_message(f"❌ Nothing equipped in **{slot}**.", ephemeral=True)
            return
        equip.pop(slot)
        data.update_pet(pet["pet_id"], equipment=equip)
        data.add_item(user_id, old_item)
        old_d = pet_lib.SHOP_ITEMS.get(old_item, {})
        await interaction.response.send_message(
            f"✅ Removed {old_d.get('emoji','📦')} **{old_item.replace('_',' ').title()}** from {pet['name']}. Returned to inventory."
        )


async def setup(bot):
    await bot.add_cog(Economy(bot))
