import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random
import json

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data
import pets as pet_lib

_pet_cooldowns: dict[str, datetime] = {}
PET_COOLDOWN_MINUTES = 30


def _add_levelup_fields(embed: discord.Embed, pet: dict, xp_gained: int):
    """Processes a level-up + possible evolution, updates DB, adds embed fields. Returns updated xp."""
    lu = pet_lib.process_level_up(
        pet["species"], pet["level"], pet["xp"], xp_gained, pet.get("evo_stage", 0)
    )
    db_updates = {"xp": lu["new_xp"]}
    if lu["leveled_up"]:
        db_updates["level"] = lu["new_level"]
        if lu["evolved"]:
            db_updates["evo_stage"] = lu["new_evo_stage"]
    data.update_pet(pet["pet_id"], **db_updates)

    if lu["leveled_up"]:
        embed.add_field(
            name="🎊 LEVEL UP!",
            value=f"**{pet['name']}** is now Level **{lu['new_level']}**!",
            inline=False
        )
    if lu["evolved"]:
        evo = lu["evo_info"]
        embed.add_field(
            name="✨ EVOLUTION!",
            value=(
                f"**{pet['name']}** has evolved into **{evo['emoji']} {evo['title']}**!\n"
                f"All stats boosted by **+{evo['stat_boost']}**! 🆙"
            ),
            inline=False
        )
        data.apply_evo_stat_boost(pet["pet_id"], evo["stat_boost"])
    return lu


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
                description="Use `/species` to see all 54 available pets.",
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

        s_data = pet_lib.SPECIES[species]
        is_egg = not s_data["is_mammal"]
        rarity = s_data["rarity"]
        data.create_pet(user_id, name, species, is_egg=is_egg, rarity=rarity)

        elem_e = pet_lib.ELEMENT_COLORS.get(s_data["element"], "")
        rar_e  = pet_lib.RARITY_EMOJI.get(rarity, "⚪")
        new_badges = data.check_and_award_achievements(user_id)

        if is_egg:
            embed = discord.Embed(
                title="🥚 An egg has arrived!",
                description=(
                    f"You adopted a **{s_data['emoji']} {species.capitalize()} egg** named **{name}**!\n"
                    f"It hatches in **24 hours**, or use a 💎 `hatch_gem` to skip the wait."
                ),
                color=discord.Color.from_rgb(255, 223, 100)
            )
        else:
            embed = discord.Embed(
                title="🎉 Welcome to PetWorld!",
                description=f"You adopted **{name}** the {s_data['emoji']} {species.capitalize()}!",
                color=discord.Color.green()
            )
            embed.add_field(name="Starting Stats", value="❤️ 100  🍖 100  😊 100  ⚡ 100", inline=False)

        embed.add_field(name="Element",  value=f"{elem_e} {s_data['element']}", inline=True)
        embed.add_field(name="Rarity",   value=f"{rar_e} {rarity.capitalize()}", inline=True)
        embed.add_field(name="Category", value=s_data["category"].capitalize(), inline=True)
        embed.add_field(name="Trait",    value=s_data["description"], inline=False)
        for badge in new_badges:
            b = data.BADGE_INFO.get(badge, {})
            embed.add_field(name="🏅 Badge Unlocked!", value=f"{b.get('emoji','')} **{b.get('label', badge)}** — _{b.get('desc','')}_", inline=False)
        embed.set_footer(text="Use /status to check on your pet!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="species", description="Browse all available pet species")
    async def species_list(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🐾 All PetWorld Species",
            description=pet_lib.species_list_embed_text(),
            color=discord.Color.teal()
        )
        embed.add_field(
            name="Rarities",
            value=" ".join(f"{e} {r.capitalize()}" for r, e in pet_lib.RARITY_EMOJI.items()),
            inline=False
        )
        embed.set_footer(text="Non-mammals hatch from eggs (24h). Birds unlock /fly. All pets evolve at Lv.25 and Lv.50!")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="status", description="Check on your pet's wellbeing")
    async def status(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet_or_egg(user_id)
        if not pet:
            await interaction.response.send_message("❌ You don't have a pet! Use `/adopt`.", ephemeral=True)
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
                embed.add_field(name="Status", value="✅ **Ready to hatch!** Use `/hatch`!", inline=False)
            else:
                h, m = int(hours_left), int((hours_left % 1) * 60)
                embed.add_field(name="Time Remaining", value=f"⏳ {h}h {m}m\n*(or use a 💎 `hatch_gem`)*", inline=False)
            await interaction.response.send_message(embed=embed)
            return

        pet    = pet_lib.apply_time_decay(pet)
        player = data.get_player(user_id)
        s_data = pet_lib.SPECIES.get(pet["species"], pet_lib.SPECIES["cat"])
        equip  = pet.get("equipment") or {}
        evo_emoji, evo_title = pet_lib.get_evo_display(pet["species"], pet.get("evo_stage", 0))
        elem_e = pet_lib.ELEMENT_COLORS.get(s_data["element"], "")
        rar_e  = pet_lib.RARITY_EMOJI.get(pet.get("rarity", "common"), "⚪")
        xp_need = pet_lib.xp_for_next_level(pet["level"])

        stage_label = f"Stage {pet.get('evo_stage', 0)+1}"
        next_evo = ""
        if pet["level"] < 25:
            next_evo = f" *(evolves at Lv.25)*"
        elif pet["level"] < 50 and pet.get("evo_stage", 0) < 2:
            next_evo = f" *(evolves again at Lv.50)*"

        embed = discord.Embed(
            title=f"{evo_emoji} {pet['name']} — {evo_title} · Level {pet['level']} {pet['species'].capitalize()}",
            color=discord.Color.blue()
        )
        embed.add_field(name="❤️ Health",    value=pet_lib.pet_status_bar(pet["health"]),    inline=False)
        embed.add_field(name="🍖 Hunger",    value=pet_lib.pet_status_bar(pet["hunger"]),    inline=False)
        embed.add_field(name="😊 Happiness", value=pet_lib.pet_status_bar(pet["happiness"]), inline=False)
        embed.add_field(name="⚡ Energy",    value=pet_lib.pet_status_bar(pet["energy"]),    inline=False)
        embed.add_field(name="✨ XP",        value=f"{pet['xp']} / {xp_need}{next_evo}",    inline=True)
        embed.add_field(name="💰 Coins",     value=str(player["coins"]),                     inline=True)
        embed.add_field(name="📅 Age",       value=f"{pet['age_days']} days",                inline=True)
        embed.add_field(name="Element",      value=f"{elem_e} {s_data['element']}",          inline=True)
        embed.add_field(name="Rarity",       value=f"{rar_e} {pet.get('rarity','common').capitalize()}", inline=True)
        embed.add_field(name="Stage",        value=f"{stage_label} — {evo_title}",           inline=True)

        if equip:
            slot_lines = []
            for slot in pet_lib.EQUIP_SLOTS:
                item = equip.get(slot)
                if item:
                    item_data = pet_lib.SHOP_ITEMS.get(item, {})
                    slot_lines.append(f"**{slot.capitalize()}:** {item_data.get('emoji','📦')} {item.replace('_',' ').title()}")
            if slot_lines:
                embed.add_field(name="👗 Equipment", value="\n".join(slot_lines), inline=False)

        embed.set_footer(text="Use /feed /play /rest /train /hunt to care for your pet")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="feed", description="Feed your pet to restore hunger")
    @app_commands.describe(item="Item to use (leave blank to feed by hand)")
    async def feed(self, interaction: discord.Interaction, item: str = None):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            msg = "🥚 Your pet hasn't hatched yet! Use `/hatch`." if data.get_active_pet_or_egg(user_id) else "❌ You don't have a pet!"
            await interaction.response.send_message(msg, ephemeral=True)
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
        data.track_quest_action(user_id, "feed")

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

        now            = datetime.utcnow().isoformat()
        happiness_gain = random.randint(15, 25)
        energy_cost    = random.randint(10, 20)
        xp_gain        = random.randint(5, 10)
        new_happiness  = pet_lib.clamp(pet["happiness"] + happiness_gain)
        new_energy     = pet_lib.clamp(pet["energy"] - energy_cost)
        data.update_pet(pet["pet_id"], happiness=new_happiness, energy=new_energy, last_played=now)

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

        _add_levelup_fields(embed, pet, xp_gain)

        completed = data.track_quest_action(user_id, "play")
        for q in completed:
            embed.add_field(name="✅ Quest Complete!", value=f"**{q['description']}** — `/quests` to claim!", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rest", description="Let your pet rest and recover energy")
    async def rest(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            msg = "🥚 Your pet hasn't hatched yet!" if data.get_active_pet_or_egg(user_id) else "❌ You don't have a pet!"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        pet         = pet_lib.apply_time_decay(pet)
        now         = datetime.utcnow().isoformat()
        energy_gain = random.randint(30, 50)
        new_energy  = pet_lib.clamp(pet["energy"] + energy_gain)
        data.update_pet(pet["pet_id"], energy=new_energy, last_rested=now)

        completed = data.track_quest_action(user_id, "rest")

        embed = discord.Embed(
            title=f"😴 {pet['name']} is resting…",
            description=f"Energy restored by **+{energy_gain}**",
            color=discord.Color.greyple()
        )
        embed.add_field(name="⚡ Energy", value=pet_lib.pet_status_bar(new_energy), inline=False)
        for q in completed:
            embed.add_field(name="✅ Quest Complete!", value=f"**{q['description']}** — `/quests` to claim!", inline=False)
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

        s_data     = pet_lib.SPECIES.get(pet["species"], pet_lib.SPECIES["cat"])
        xp_gain    = int(random.randint(20, 35) * s_data["xp_mult"])
        e_cost     = random.randint(20, 30)
        h_cost     = random.randint(10, 20)
        now        = datetime.utcnow().isoformat()
        new_energy = pet_lib.clamp(pet["energy"] - e_cost)
        new_hunger = pet_lib.clamp(pet["hunger"] - h_cost)
        data.update_pet(pet["pet_id"], energy=new_energy, hunger=new_hunger, last_trained=now)

        sessions = [
            f"**{pet['name']}** ran an obstacle course! 🏃",
            f"**{pet['name']}** meditated under a waterfall! 💧",
            f"**{pet['name']}** sparred with a training dummy! 🪆",
            f"**{pet['name']}** climbed a mountain! ⛰️",
            f"**{pet['name']}** practiced **{s_data['element']}** techniques! {pet_lib.ELEMENT_COLORS.get(s_data['element'],'✨')}",
        ]
        embed = discord.Embed(title="💪 Training Complete!", description=random.choice(sessions), color=discord.Color.gold())
        embed.add_field(name="✨ XP Gained", value=f"+{xp_gain} (×{s_data['xp_mult']} {s_data['element']} bonus)", inline=True)
        embed.add_field(name="⚡ Energy",    value=f"-{e_cost}", inline=True)
        embed.add_field(name="🍖 Hunger",    value=f"-{h_cost}", inline=True)

        lu = _add_levelup_fields(embed, pet, xp_gain)
        if not lu["leveled_up"]:
            xp_now  = pet["xp"] + xp_gain
            xp_need = pet_lib.xp_for_next_level(pet["level"])
            embed.add_field(name="Progress", value=f"{xp_now}/{xp_need} XP to next level", inline=False)

        completed = data.track_quest_action(user_id, "train")
        for q in completed:
            embed.add_field(name="✅ Quest Complete!", value=f"**{q['description']}** — `/quests` to claim!", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pet", description="Give your pet some love! (30 min cooldown)")
    async def pet_cmd(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        pet = data.get_active_pet(user_id)
        if not pet:
            msg = "🥚 Your pet hasn't hatched yet!" if data.get_active_pet_or_egg(user_id) else "❌ You don't have a pet!"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        last = _pet_cooldowns.get(user_id)
        if last and (datetime.utcnow() - last) < timedelta(minutes=PET_COOLDOWN_MINUTES):
            remaining = timedelta(minutes=PET_COOLDOWN_MINUTES) - (datetime.utcnow() - last)
            mins = int(remaining.total_seconds() / 60)
            await interaction.response.send_message(
                f"💙 **{pet['name']}** needs a little space first! Come back in **{mins}m**.", ephemeral=True
            )
            return

        _pet_cooldowns[user_id] = datetime.utcnow()

        s_data   = pet_lib.SPECIES.get(pet["species"], pet_lib.SPECIES["cat"])
        category = s_data.get("category", "mammals")
        messages = pet_lib.PET_MESSAGES.get(category, pet_lib.PET_MESSAGES["mammals"])
        msg      = random.choice(messages).format(name=pet["name"])

        happiness_gain = random.randint(10, 20)
        xp_gain        = random.randint(5, 10)
        new_happiness  = pet_lib.clamp(pet["happiness"] + happiness_gain)
        data.update_pet(pet["pet_id"], happiness=new_happiness)

        evo_emoji, _ = pet_lib.get_evo_display(pet["species"], pet.get("evo_stage", 0))
        embed = discord.Embed(
            title=f"🖐️ You petted {evo_emoji} {pet['name']}!",
            description=msg,
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.add_field(name="😊 Happiness", value=f"+{happiness_gain} → {new_happiness}%", inline=True)
        embed.add_field(name="✨ XP",        value=f"+{xp_gain}",                            inline=True)
        embed.set_footer(text=f"Next pet in {PET_COOLDOWN_MINUTES} minutes.")

        _add_levelup_fields(embed, pet, xp_gain)

        completed = data.track_quest_action(user_id, "pet_action")
        for q in completed:
            embed.add_field(name="✅ Quest Complete!", value=f"**{q['description']}** — `/quests` to claim!", inline=False)

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
                f"🚫 Only **birds** can fly! **{pet['name']}** is a {pet['species']}.\n"
                f"Bird species include: `parrot`, `owl`, `eagle`, `flamingo`, `penguin`, `phoenix`, `griffin`, `thunderbird` and more.",
                ephemeral=True
            )
            return

        pet = pet_lib.apply_time_decay(pet)
        if pet["energy"] < 15:
            await interaction.response.send_message(f"😴 **{pet['name']}** is too tired to fly!", ephemeral=True)
            return

        equip       = pet.get("equipment") or {}
        wings_bonus = 1.3 if equip.get("accessory") == "wings" else 1.0
        xp_gain     = int(random.randint(25, 45) * s_data["xp_mult"] * wings_bonus)
        coin_gain   = int(random.randint(20, 60) * wings_bonus)
        energy_cost = random.randint(20, 30)
        found_item  = None

        if random.random() < 0.25:
            found_item = random.choice(["potion", "toy", "energy_drink"])
            data.add_item(user_id, found_item)

        player    = data.get_player(user_id)
        new_coins = player["coins"] + coin_gain
        new_energy = pet_lib.clamp(pet["energy"] - energy_cost)
        data.update_player(user_id, coins=new_coins)
        data.update_pet(pet["pet_id"], energy=new_energy, last_played=datetime.utcnow().isoformat())

        adventures = [
            f"**{pet['name']}** soared above the clouds and found buried treasure! ☁️",
            f"**{pet['name']}** rode a storm front across the sky! ⛈️",
            f"**{pet['name']}** discovered a hidden sky island! 🏝️",
            f"**{pet['name']}** raced the wind and came back victorious! 💨",
            f"**{pet['name']}** flew to the moon and back! 🌙",
        ]
        evo_emoji, _ = pet_lib.get_evo_display(pet["species"], pet.get("evo_stage", 0))
        embed = discord.Embed(
            title=f"🪽 Flight Adventure — {evo_emoji} {pet['name']}!",
            description=random.choice(adventures),
            color=discord.Color.from_rgb(135, 206, 235)
        )
        embed.add_field(name="💰 Coins",  value=f"+{coin_gain}", inline=True)
        embed.add_field(name="✨ XP",     value=f"+{xp_gain}",   inline=True)
        embed.add_field(name="⚡ Energy", value=f"-{energy_cost}", inline=True)
        if found_item:
            fi = pet_lib.SHOP_ITEMS.get(found_item, {})
            embed.add_field(name="🎁 Found!", value=f"{fi.get('emoji','📦')} {found_item.replace('_',' ').title()} added!", inline=False)
        if wings_bonus > 1.0:
            embed.set_footer(text="🪽 Wings equipped — +30% rewards!")

        _add_levelup_fields(embed, pet, xp_gain)

        completed = data.track_quest_action(user_id, "fly")
        for q in completed:
            embed.add_field(name="✅ Quest Complete!", value=f"**{q['description']}** — `/quests` to claim!", inline=False)

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
        user_id  = str(interaction.user.id)
        all_pets = data.get_all_pets(user_id)
        if not all_pets:
            await interaction.response.send_message("❌ You have no pets! Use `/adopt`.", ephemeral=True)
            return

        embed = discord.Embed(title="🐾 Your Pets", color=discord.Color.blue())
        for p in all_pets:
            s      = pet_lib.SPECIES.get(p["species"], {})
            rar_e  = pet_lib.RARITY_EMOJI.get(p.get("rarity", "common"), "⚪")
            elem_e = pet_lib.ELEMENT_COLORS.get(s.get("element", ""), "")
            evo_emoji, evo_title = pet_lib.get_evo_display(p["species"], p.get("evo_stage", 0))

            if p.get("is_egg"):
                hrs_left = pet_lib.egg_hours_remaining(p["created_at"])
                status = f"🥚 Egg — {int(hrs_left)}h remaining" if hrs_left > 0 else "🥚 Ready to hatch!"
            elif p["is_active"]:
                status = f"✅ Active · {evo_title} · Lv.{p['level']}"
            else:
                status = f"💤 Retired · Lv.{p['level']}"

            embed.add_field(
                name=f"{evo_emoji} {p['name']} — {p['species'].capitalize()} {rar_e} {elem_e}",
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
