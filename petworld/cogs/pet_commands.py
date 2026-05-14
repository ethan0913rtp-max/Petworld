import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import random

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data
import pets as pet_lib


class PetCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def ensure_player(self, user: discord.User):
        if not data.get_player(str(user.id)):
            data.create_player(str(user.id), user.name)

    @app_commands.command(name="adopt", description="Adopt a new pet and start your journey!")
    @app_commands.describe(name="Name your pet", species="Choose a species: dragon, bunny, cat, fox, penguin, wolf")
    async def adopt(self, interaction: discord.Interaction, name: str, species: str):
        species = species.lower()
        if species not in pet_lib.SPECIES:
            species_list = ", ".join(f"`{s}`" for s in pet_lib.SPECIES)
            await interaction.response.send_message(
                f"❌ Unknown species! Choose from: {species_list}", ephemeral=True
            )
            return

        self.ensure_player(interaction.user)
        user_id = str(interaction.user.id)
        existing = data.get_active_pet(user_id)
        if existing:
            await interaction.response.send_message(
                f"❌ You already have **{existing['name']}**! Use `/release` first to adopt a new pet.",
                ephemeral=True
            )
            return

        data.create_pet(user_id, name, species)
        info = pet_lib.SPECIES[species]
        embed = discord.Embed(
            title=f"🎉 Welcome to PetWorld!",
            description=f"You adopted **{name}** the {info['emoji']} {species.capitalize()}!",
            color=discord.Color.green()
        )
        embed.add_field(name="Species", value=f"{info['emoji']} {species.capitalize()}", inline=True)
        embed.add_field(name="Trait", value=info["description"], inline=False)
        embed.add_field(name="Starting Stats", value="❤️ Health: 100\n🍖 Hunger: 100\n😊 Happiness: 100\n⚡ Energy: 100", inline=False)
        embed.set_footer(text="Use /status to check on your pet, /feed to feed it, and /play to bond!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="status", description="Check on your pet's wellbeing")
    async def status(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            await interaction.response.send_message("❌ You don't have a pet! Use `/adopt` to get one.", ephemeral=True)
            return

        pet = pet_lib.apply_time_decay(pet)
        player = data.get_player(user_id)
        species_info = pet_lib.SPECIES.get(pet["species"], pet_lib.SPECIES["cat"])
        emoji = species_info["emoji"]
        xp_needed = pet_lib.xp_for_next_level(pet["level"])

        embed = discord.Embed(
            title=f"{emoji} {pet['name']} — Level {pet['level']} {pet['species'].capitalize()}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="❤️ Health",
            value=pet_lib.pet_status_bar(pet["health"]),
            inline=False
        )
        embed.add_field(
            name="🍖 Hunger",
            value=pet_lib.pet_status_bar(pet["hunger"]),
            inline=False
        )
        embed.add_field(
            name="😊 Happiness",
            value=pet_lib.pet_status_bar(pet["happiness"]),
            inline=False
        )
        embed.add_field(
            name="⚡ Energy",
            value=pet_lib.pet_status_bar(pet["energy"]),
            inline=False
        )
        embed.add_field(
            name="✨ XP",
            value=f"{pet['xp']} / {xp_needed}",
            inline=True
        )
        embed.add_field(name="💰 Coins", value=str(player["coins"]), inline=True)
        embed.set_footer(text=f"Age: {pet['age_days']} days | Use /feed, /play, /rest, /train to care for your pet")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="feed", description="Feed your pet to restore hunger")
    @app_commands.describe(item="Item to use (leave blank to feed by hand for free)")
    async def feed(self, interaction: discord.Interaction, item: str = None):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            await interaction.response.send_message("❌ You don't have a pet! Use `/adopt` to get one.", ephemeral=True)
            return

        pet = pet_lib.apply_time_decay(pet)
        now = datetime.utcnow().isoformat()
        hunger_gain = 15
        msg = ""

        if item:
            item = item.lower()
            item_data = pet_lib.SHOP_ITEMS.get(item)
            if not item_data or "hunger" not in item_data:
                await interaction.response.send_message(f"❌ `{item}` isn't a food item. Check `/shop`.", ephemeral=True)
                return
            if not data.remove_item(user_id, item):
                await interaction.response.send_message(f"❌ You don't have any `{item}` in your inventory.", ephemeral=True)
                return
            hunger_gain = item_data["hunger"]
            msg = f" with a {item_data['emoji']} {item}"
        
        new_hunger = pet_lib.clamp(pet["hunger"] + hunger_gain)
        data.update_pet(pet["pet_id"], hunger=new_hunger, last_fed=now)

        embed = discord.Embed(
            title=f"🍖 Fed {pet['name']}{msg}!",
            description=f"Hunger restored by **+{hunger_gain}**",
            color=discord.Color.orange()
        )
        embed.add_field(name="Hunger", value=pet_lib.pet_status_bar(new_hunger), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="play", description="Play with your pet to boost happiness")
    async def play(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            await interaction.response.send_message("❌ You don't have a pet!", ephemeral=True)
            return

        pet = pet_lib.apply_time_decay(pet)
        if pet["energy"] < 10:
            await interaction.response.send_message(f"😴 **{pet['name']}** is too tired to play! Use `/rest` first.", ephemeral=True)
            return

        now = datetime.utcnow().isoformat()
        happiness_gain = random.randint(15, 25)
        energy_cost = random.randint(10, 20)
        xp_gain = random.randint(5, 10)

        new_happiness = pet_lib.clamp(pet["happiness"] + happiness_gain)
        new_energy = pet_lib.clamp(pet["energy"] - energy_cost)
        new_xp = pet["xp"] + xp_gain

        data.update_pet(pet["pet_id"], happiness=new_happiness, energy=new_energy, xp=new_xp, last_played=now)

        actions = [
            f"**{pet['name']}** chased a ball of yarn! 🧶",
            f"**{pet['name']}** went for a walk in the park! 🌳",
            f"**{pet['name']}** played hide and seek! 👀",
            f"**{pet['name']}** splashed in some puddles! 💦",
            f"**{pet['name']}** learned a new trick! 🎪",
        ]

        embed = discord.Embed(
            title="🎮 Playtime!",
            description=random.choice(actions),
            color=discord.Color.purple()
        )
        embed.add_field(name="😊 Happiness", value=f"+{happiness_gain} → {new_happiness}%", inline=True)
        embed.add_field(name="⚡ Energy", value=f"-{energy_cost} → {new_energy}%", inline=True)
        embed.add_field(name="✨ XP", value=f"+{xp_gain}", inline=True)

        level, leveled_up = pet_lib.check_level_up({"level": pet["level"], "xp": new_xp})
        if leveled_up:
            data.update_pet(pet["pet_id"], level=level, xp=0)
            embed.add_field(name="🎊 LEVEL UP!", value=f"**{pet['name']}** is now Level **{level}**!", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rest", description="Let your pet rest to recover energy")
    async def rest(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            await interaction.response.send_message("❌ You don't have a pet!", ephemeral=True)
            return

        pet = pet_lib.apply_time_decay(pet)
        now = datetime.utcnow().isoformat()
        energy_gain = random.randint(30, 50)
        new_energy = pet_lib.clamp(pet["energy"] + energy_gain)
        data.update_pet(pet["pet_id"], energy=new_energy, last_rested=now)

        embed = discord.Embed(
            title=f"😴 {pet['name']} is resting...",
            description=f"Energy restored by **+{energy_gain}**",
            color=discord.Color.greyple()
        )
        embed.add_field(name="⚡ Energy", value=pet_lib.pet_status_bar(new_energy), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="train", description="Train your pet to gain XP and level up!")
    async def train(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            await interaction.response.send_message("❌ You don't have a pet!", ephemeral=True)
            return

        pet = pet_lib.apply_time_decay(pet)
        if pet["energy"] < 20:
            await interaction.response.send_message(f"😴 **{pet['name']}** needs more energy to train! Use `/rest`.", ephemeral=True)
            return
        if pet["hunger"] < 20:
            await interaction.response.send_message(f"🍖 **{pet['name']}** is too hungry to train! Feed it first.", ephemeral=True)
            return

        species_info = pet_lib.SPECIES.get(pet["species"], pet_lib.SPECIES["cat"])
        xp_mult = species_info["xp_mult"]
        base_xp = random.randint(20, 35)
        xp_gain = int(base_xp * xp_mult)
        energy_cost = random.randint(20, 30)
        hunger_cost = random.randint(10, 20)
        now = datetime.utcnow().isoformat()

        new_xp = pet["xp"] + xp_gain
        new_energy = pet_lib.clamp(pet["energy"] - energy_cost)
        new_hunger = pet_lib.clamp(pet["hunger"] - hunger_cost)

        data.update_pet(pet["pet_id"], xp=new_xp, energy=new_energy, hunger=new_hunger, last_trained=now)

        sessions = [
            f"**{pet['name']}** practiced elemental techniques! 🔥",
            f"**{pet['name']}** ran an obstacle course! 🏃",
            f"**{pet['name']}** meditated under a waterfall! 💧",
            f"**{pet['name']}** sparred with a training dummy! 🪆",
            f"**{pet['name']}** climbed a mountain! ⛰️",
        ]

        embed = discord.Embed(
            title="💪 Training Complete!",
            description=random.choice(sessions),
            color=discord.Color.gold()
        )
        embed.add_field(name="✨ XP Gained", value=f"+{xp_gain} (x{xp_mult} species bonus)", inline=True)
        embed.add_field(name="⚡ Energy", value=f"-{energy_cost}", inline=True)
        embed.add_field(name="🍖 Hunger", value=f"-{hunger_cost}", inline=True)

        level, leveled_up = pet_lib.check_level_up({"level": pet["level"], "xp": new_xp})
        if leveled_up:
            data.update_pet(pet["pet_id"], level=level, xp=0)
            embed.add_field(name="🎊 LEVEL UP!", value=f"**{pet['name']}** reached Level **{level}**!", inline=False)
        else:
            xp_needed = pet_lib.xp_for_next_level(pet["level"])
            embed.add_field(name="Progress", value=f"{new_xp}/{xp_needed} XP to next level", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="release", description="Release your pet (permanent!)")
    async def release(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            await interaction.response.send_message("❌ You don't have a pet to release.", ephemeral=True)
            return

        view = ConfirmReleaseView(pet["name"], pet["pet_id"])
        await interaction.response.send_message(
            f"⚠️ Are you sure you want to release **{pet['name']}**? This cannot be undone.",
            view=view,
            ephemeral=True
        )

    @app_commands.command(name="mypets", description="View all your pets")
    async def mypets(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        all_pets = data.get_all_pets(user_id)
        if not all_pets:
            await interaction.response.send_message("❌ You have no pets! Use `/adopt` to get one.", ephemeral=True)
            return

        embed = discord.Embed(title="🐾 Your Pets", color=discord.Color.blue())
        for p in all_pets:
            emoji = pet_lib.get_species_emoji(p["species"])
            status = "✅ Active" if p["is_active"] else "💤 Retired"
            embed.add_field(
                name=f"{emoji} {p['name']} — Lv.{p['level']} {p['species'].capitalize()}",
                value=f"{status} | XP: {p['xp']}/{pet_lib.xp_for_next_level(p['level'])}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)


class ConfirmReleaseView(discord.ui.View):
    def __init__(self, pet_name: str, pet_id: int):
        super().__init__(timeout=30)
        self.pet_name = pet_name
        self.pet_id = pet_id

    @discord.ui.button(label="Yes, release", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        data.update_pet(self.pet_id, is_active=0)
        await interaction.response.edit_message(
            content=f"👋 You released **{self.pet_name}**. Farewell!", view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Cancelled.", view=None)


async def setup(bot):
    await bot.add_cog(PetCommands(bot))
