import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import random
import json

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
    @app_commands.describe(name="Name your pet", species="Species name (use /species to browse all 54 options)")
    async def adopt(self, interaction: discord.Interaction, name: str, species: str):
        species = species.lower().strip()
        if species not in pet_lib.SPECIES:
            embed = discord.Embed(
                title="❌ Unknown species!",
                description=f"Use `/species` to see all available pets, or try one of these:\n"
                            f"`dragon`, `cat`, `wolf`, `phoenix`, `unicorn`, `shark`, `butterfly` …",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        self.ensure_player(interaction.user)
        user_id = str(interaction.user.id)

        existing = data.get_active_pet_or_egg(user_id)
        if existing:
            label = "egg" if existing.get("is_egg") else existing["name"]
            await interaction.response.send_message(
                f"❌ You already have **{label}**! Use `/release` first.", ephemeral=True
            )
            return

        s_data  = pet_lib.SPECIES[species]
        is_egg  = not s_data["is_mammal"]
        rarity  = s_data["rarity"]
        data.create_pet(user_id, name, species, is_egg=is_egg, rarity=rarity)

        elem_e  = pet_lib.ELEMENT_COLORS.get(s_data["element"], "")
        rar_e   = pet_lib.RARITY_EMOJI.get(rarity, "⚪")

        if is_egg:
            embed = discord.Embed(
                title=f"🥚 An egg has arrived!",
                description=f"You adopted a **{s_data['emoji']} {species.capitalize()} egg** named **{name}**!\n"
                            f"It will hatch in **24 hours**, or use a 💎 `hatch_gem` to hatch it instantly.",
                color=discord.Color.from_rgb(255, 223, 100)
            )
        else:
            embed = discord.Embed(
                title=f"🎉 Welcome to PetWorld!",
                description=f"You adopted **{name}** the {s_data['emoji']} {species.capitalize()}!",
                color=discord.Color.green()
            )
            embed.add_field(name="Starting Stats", value="❤️ Health: 100\n🍖 Hunger: 100\n😊 Happiness: 100\n⚡ Energy: 100", inline=False)

        embed.add_field(name="Element",  value=f"{elem_e} {s_data['element']}", inline=True)
        embed.add_field(name="Rarity",   value=f"{rar_e} {rarity.capitalize()}", inline=True)
        embed.add_field(name="Category", value=s_data["category"].capitalize(), inline=True)
        embed.add_field(name="Trait",    value=s_data["description"], inline=False)
        embed.set_footer(text="Use /status to check on your pet!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="species", description="Browse all available pet species")
    async def species_list(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🐾 All PetWorld Species (54 total)",
            description=pet_lib.species_list_embed_text(),
            color=discord.Color.teal()
        )
        embed.add_field(
            name="Rarities",
            value=" ".join(f"{e} {r.capitalize()}" for r, e in pet_lib.RARITY_EMOJI.items()),
            inline=False
        )
        embed.set_footer(text="Non-mammal species hatch from eggs (24h or use a hatch_gem). Birds unlock /fly!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="status", description="Check on your pet's wellbeing")
    async def status(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet_or_egg(user_id)
        if not pet:
            await interaction.response.send_message("❌ You don't have a pet! Use `/adopt` to get one.", ephemeral=True)
            return

        if pet.get("is_egg"):
            hours_left = pet_lib.egg_hours_remaining(pet["created_at"])
            s_data = pet_lib.SPECIES.get(pet["species"], {})
            embed = discord.Embed(
                title=f"🥚 {pet['name']}'s Egg",
                description=f"A **{s_data.get('emoji','🥚')} {pet['species'].capitalize()}** egg is incubating…",
                color=discord.Color.from_rgb(255, 223, 100)
            )
            if hours_left <= 0:
                embed.add_field(name="Status", value="✅ **Ready to hatch!** Use `/hatch` now!", inline=False)
            else:
                h = int(hours_left)
                m = int((hours_left - h) * 60)
                embed.add_field(name="Time Remaining", value=f"⏳ {h}h {m}m\n*(or use a 💎 `hatch_gem` to skip)*", inline=False)
            await interaction.response.send_message(embed=embed)
            return

        pet     = pet_lib.apply_time_decay(pet)
        player  = data.get_player(user_id)
        s_data  = pet_lib.SPECIES.get(pet["species"], pet_lib.SPECIES["cat"])
        equip   = pet.get("equipment") or {}
        xp_need = pet_lib.xp_for_next_level(pet["level"])
        elem_e  = pet_lib.ELEMENT_COLORS.get(s_data["element"], "")
        rar_e   = pet_lib.RARITY_EMOJI.get(pet.get("rarity", "common"), "⚪")

        embed = discord.Embed(
            title=f"{s_data['emoji']} {pet['name']} — Level {pet['level']} {pet['species'].capitalize()}",
            color=discord.Color.blue()
        )
        embed.add_field(name="❤️ Health",    value=pet_lib.pet_status_bar(pet["health"]),    inline=False)
        embed.add_field(name="🍖 Hunger",    value=pet_lib.pet_status_bar(pet["hunger"]),    inline=False)
        embed.add_field(name="😊 Happiness", value=pet_lib.pet_status_bar(pet["happiness"]), inline=False)
        embed.add_field(name="⚡ Energy",    value=pet_lib.pet_status_bar(pet["energy"]),    inline=False)
        embed.add_field(name="✨ XP",        value=f"{pet['xp']} / {xp_need}", inline=True)
        embed.add_field(name="💰 Coins",     value=str(player["coins"]),        inline=True)
        embed.add_field(name="📅 Age",       value=f"{pet['age_days']} days",   inline=True)
        embed.add_field(name="Element",      value=f"{elem_e} {s_data['element']}", inline=True)
        embed.add_field(name="Rarity",       value=f"{rar_e} {pet.get('rarity','common').capitalize()}", inline=True)

        if equip:
            slot_lines = []
            for slot in pet_lib.EQUIP_SLOTS:
                item = equip.get(slot)
                if item:
                    item_data = pet_lib.SHOP_ITEMS.get(item, {})
                    slot_lines.append(f"**{slot.capitalize()}:** {item_data.get('emoji','📦')} {item.replace('_',' ').title()}")
            if slot_lines:
                embed.add_field(name="👗 Equipment", value="\n".join(slot_lines), inline=False)

        embed.set_footer(text="Use /feed /play /rest /train to care for your pet")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="feed", description="Feed your pet to restore hunger")
    @app_commands.describe(item="Item to use (leave blank to feed by hand)")
    async def feed(self, interaction: discord.Interaction, item: str = None):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            if data.get_active_pet_or_egg(user_id):
                await interaction.response.send_message("🥚 Your pet hasn't hatched yet! Use `/hatch` first.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ You don't have a pet! Use `/adopt`.", ephemeral=True)
            return

        pet  = pet_lib.apply_time_decay(pet)
        now  = datetime.utcnow().isoformat()
        gain = 15
        msg  = ""

        if item:
            item      = item.lower()
            item_data = pet_lib.SHOP_ITEMS.get(item)
            if not item_data or "hunger" not in item_data:
                await interaction.response.send_message(f"❌ `{item}` isn't a food item.", ephemeral=True)
                return
            if not data.remove_item(user_id, item):
                await interaction.response.send_message(f"❌ You don't have any `{item}`.", ephemeral=True)
                return
            gain = item_data["hunger"]
            msg  = f" with a {item_data['emoji']} {item}"

        new_hunger = pet_lib.clamp(pet["hunger"] + gain)
        data.update_pet(pet["pet_id"], hunger=new_hunger, last_fed=now)

        embed = discord.Embed(
            title=f"🍖 Fed {pet['name']}{msg}!",
            description=f"Hunger restored by **+{gain}**",
            color=discord.Color.orange()
        )
        embed.add_field(name="Hunger", value=pet_lib.pet_status_bar(new_hunger), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="play", description="Play with your pet to boost happiness")
    async def play(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            msg = "🥚 Your pet hasn't hatched yet!" if data.get_active_pet_or_egg(user_id) else "❌ You don't have a pet!"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        pet = pet_lib.apply_time_decay(pet)
        if pet["energy"] < 10:
            await interaction.response.send_message(f"😴 **{pet['name']}** is too tired! Use `/rest` first.", ephemeral=True)
            return

        now           = datetime.utcnow().isoformat()
        happiness_gain = random.randint(15, 25)
        energy_cost   = random.randint(10, 20)
        xp_gain       = random.randint(5, 10)
        new_happiness = pet_lib.clamp(pet["happiness"] + happiness_gain)
        new_energy    = pet_lib.clamp(pet["energy"] - energy_cost)
        new_xp        = pet["xp"] + xp_gain
        data.update_pet(pet["pet_id"], happiness=new_happiness, energy=new_energy, xp=new_xp, last_played=now)

        actions = [
            f"**{pet['name']}** chased a ball of yarn! 🧶",
            f"**{pet['name']}** went for a walk in the park! 🌳",
            f"**{pet['name']}** played hide and seek! 👀",
            f"**{pet['name']}** splashed in some puddles! 💦",
            f"**{pet['name']}** learned a new trick! 🎪",
        ]
        embed = discord.Embed(title="🎮 Playtime!", description=random.choice(actions), color=discord.Color.purple())
        embed.add_field(name="😊 Happiness", value=f"+{happiness_gain} → {new_happiness}%", inline=True)
        embed.add_field(name="⚡ Energy",    value=f"-{energy_cost} → {new_energy}%",       inline=True)
        embed.add_field(name="✨ XP",        value=f"+{xp_gain}",                            inline=True)

        level, leveled_up = pet_lib.check_level_up({"level": pet["level"], "xp": new_xp})
        if leveled_up:
            data.update_pet(pet["pet_id"], level=level, xp=0)
            embed.add_field(name="🎊 LEVEL UP!", value=f"**{pet['name']}** is now Level **{level}**!", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rest", description="Let your pet rest and recover energy")
    async def rest(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            msg = "🥚 Your pet hasn't hatched yet!" if data.get_active_pet_or_egg(user_id) else "❌ You don't have a pet!"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        pet        = pet_lib.apply_time_decay(pet)
        now        = datetime.utcnow().isoformat()
        energy_gain = random.randint(30, 50)
        new_energy  = pet_lib.clamp(pet["energy"] + energy_gain)
        data.update_pet(pet["pet_id"], energy=new_energy, last_rested=now)

        embed = discord.Embed(
            title=f"😴 {pet['name']} is resting…",
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
            msg = "🥚 Your pet hasn't hatched yet!" if data.get_active_pet_or_egg(user_id) else "❌ You don't have a pet!"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        pet = pet_lib.apply_time_decay(pet)
        if pet["energy"] < 20:
            await interaction.response.send_message(f"😴 **{pet['name']}** needs more energy! Use `/rest`.", ephemeral=True)
            return
        if pet["hunger"] < 20:
            await interaction.response.send_message(f"🍖 **{pet['name']}** is too hungry! Feed it first.", ephemeral=True)
            return

        s_data    = pet_lib.SPECIES.get(pet["species"], pet_lib.SPECIES["cat"])
        xp_gain   = int(random.randint(20, 35) * s_data["xp_mult"])
        e_cost    = random.randint(20, 30)
        h_cost    = random.randint(10, 20)
        now       = datetime.utcnow().isoformat()
        new_xp    = pet["xp"] + xp_gain
        new_energy = pet_lib.clamp(pet["energy"] - e_cost)
        new_hunger = pet_lib.clamp(pet["hunger"] - h_cost)
        data.update_pet(pet["pet_id"], xp=new_xp, energy=new_energy, hunger=new_hunger, last_trained=now)

        sessions = [
            f"**{pet['name']}** ran an obstacle course! 🏃",
            f"**{pet['name']}** meditated under a waterfall! 💧",
            f"**{pet['name']}** sparred with a training dummy! 🪆",
            f"**{pet['name']}** climbed a mountain! ⛰️",
            f"**{pet['name']}** practiced elemental techniques! {pet_lib.ELEMENT_COLORS.get(s_data['element'],'✨')}",
        ]
        embed = discord.Embed(title="💪 Training Complete!", description=random.choice(sessions), color=discord.Color.gold())
        embed.add_field(name="✨ XP Gained", value=f"+{xp_gain} (×{s_data['xp_mult']} {s_data['element']} bonus)", inline=True)
        embed.add_field(name="⚡ Energy",    value=f"-{e_cost}", inline=True)
        embed.add_field(name="🍖 Hunger",    value=f"-{h_cost}", inline=True)

        level, leveled_up = pet_lib.check_level_up({"level": pet["level"], "xp": new_xp})
        if leveled_up:
            data.update_pet(pet["pet_id"], level=level, xp=0)
            embed.add_field(name="🎊 LEVEL UP!", value=f"**{pet['name']}** reached Level **{level}**!", inline=False)
        else:
            xp_need = pet_lib.xp_for_next_level(pet["level"])
            embed.add_field(name="Progress", value=f"{new_xp}/{xp_need} XP to next level", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="fly", description="Take your bird pet on a flight for unique rewards!")
    async def fly(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            msg = "🥚 Your pet hasn't hatched yet!" if data.get_active_pet_or_egg(user_id) else "❌ You don't have a pet!"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        s_data = pet_lib.SPECIES.get(pet["species"], {})
        if not s_data.get("is_bird"):
            await interaction.response.send_message(
                f"🚫 Only **birds** can fly! **{pet['name']}** is a {pet['species']} — not a bird.\n"
                f"Bird species: `parrot`, `owl`, `eagle`, `flamingo`, `toucan`, `peacock`, `crow`, "
                f"`penguin`, `hummingbird`, `phoenix`, `griffin`, `thunderbird`",
                ephemeral=True
            )
            return

        pet = pet_lib.apply_time_decay(pet)
        if pet["energy"] < 15:
            await interaction.response.send_message(f"😴 **{pet['name']}** is too tired to fly! Rest first.", ephemeral=True)
            return

        equip = pet.get("equipment") or {}
        wings_bonus = 1.3 if equip.get("accessory") == "wings" else 1.0

        # Flying rewards — not available to land pets
        xp_gain      = int(random.randint(25, 45) * s_data["xp_mult"] * wings_bonus)
        coin_gain    = int(random.randint(20, 60) * wings_bonus)
        energy_cost  = random.randint(20, 30)
        found_item   = None

        # 25% chance to find a rare item while flying
        if random.random() < 0.25:
            found_item = random.choice(["potion", "toy", "energy_drink", "feather_token"])
            data.add_item(user_id, found_item)

        player   = data.get_player(user_id)
        new_coins = player["coins"] + coin_gain
        new_xp    = pet["xp"] + xp_gain
        new_energy = pet_lib.clamp(pet["energy"] - energy_cost)
        data.update_player(user_id, coins=new_coins)
        data.update_pet(pet["pet_id"], xp=new_xp, energy=new_energy, last_played=datetime.utcnow().isoformat())

        adventures = [
            f"**{pet['name']}** soared above the clouds and found buried treasure! ☁️",
            f"**{pet['name']}** rode a storm front across the sky! ⛈️",
            f"**{pet['name']}** discovered a hidden sky island! 🏝️",
            f"**{pet['name']}** raced the wind and came back victorious! 💨",
            f"**{pet['name']}** dive-bombed into a gold mine! 💰",
            f"**{pet['name']}** flew to the moon and back for a snack! 🌙",
        ]
        embed = discord.Embed(
            title=f"🪽 Flight Adventure — {s_data['emoji']} {pet['name']}!",
            description=random.choice(adventures),
            color=discord.Color.from_rgb(135, 206, 235)
        )
        embed.add_field(name="💰 Coins",  value=f"+{coin_gain}", inline=True)
        embed.add_field(name="✨ XP",     value=f"+{xp_gain}",   inline=True)
        embed.add_field(name="⚡ Energy", value=f"-{energy_cost}", inline=True)
        if found_item:
            fi = pet_lib.SHOP_ITEMS.get(found_item, {})
            embed.add_field(name="🎁 Found Item!", value=f"{fi.get('emoji','📦')} {found_item.replace('_',' ').title()} added to inventory!", inline=False)
        if wings_bonus > 1.0:
            embed.set_footer(text="🪽 Wings equipped — rewards boosted by 30%!")

        level, leveled_up = pet_lib.check_level_up({"level": pet["level"], "xp": new_xp})
        if leveled_up:
            data.update_pet(pet["pet_id"], level=level, xp=0)
            embed.add_field(name="🎊 LEVEL UP!", value=f"**{pet['name']}** reached Level **{level}**!", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="release", description="Release your current pet (permanent!)")
    async def release(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet_or_egg(user_id)
        if not pet:
            await interaction.response.send_message("❌ You don't have a pet to release.", ephemeral=True)
            return

        view = ConfirmReleaseView(pet["name"], pet["pet_id"])
        await interaction.response.send_message(
            f"⚠️ Are you sure you want to release **{pet['name']}**? This cannot be undone.",
            view=view, ephemeral=True
        )

    @app_commands.command(name="mypets", description="View all your pets and eggs")
    async def mypets(self, interaction: discord.Interaction):
        user_id   = str(interaction.user.id)
        all_pets  = data.get_all_pets(user_id)
        if not all_pets:
            await interaction.response.send_message("❌ You have no pets! Use `/adopt` to get one.", ephemeral=True)
            return

        embed = discord.Embed(title="🐾 Your Pets", color=discord.Color.blue())
        for p in all_pets:
            s   = pet_lib.SPECIES.get(p["species"], {})
            emoji = s.get("emoji", "🐾")
            rar_e = pet_lib.RARITY_EMOJI.get(p.get("rarity", "common"), "⚪")
            elem_e = pet_lib.ELEMENT_COLORS.get(s.get("element", ""), "")
            if p.get("is_egg"):
                hrs_left = pet_lib.egg_hours_remaining(p["created_at"])
                status = f"🥚 Egg — {int(hrs_left)}h remaining" if hrs_left > 0 else "🥚 Ready to hatch!"
            elif p["is_active"]:
                status = f"✅ Active | Lv.{p['level']}"
            else:
                status = f"💤 Retired | Lv.{p['level']}"
            embed.add_field(
                name=f"{emoji} {p['name']} — {p['species'].capitalize()} {rar_e} {elem_e}",
                value=f"{status} | XP: {p['xp']}/{pet_lib.xp_for_next_level(p['level'])}",
                inline=False
            )
        await interaction.response.send_message(embed=embed)


class ConfirmReleaseView(discord.ui.View):
    def __init__(self, pet_name: str, pet_id: int):
        super().__init__(timeout=30)
        self.pet_name = pet_name
        self.pet_id   = pet_id

    @discord.ui.button(label="Yes, release", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        data.update_pet(self.pet_id, is_active=0)
        await interaction.response.edit_message(content=f"👋 You released **{self.pet_name}**. Farewell!", view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="Cancelled.", view=None)


async def setup(bot):
    await bot.add_cog(PetCommands(bot))
