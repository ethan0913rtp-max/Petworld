import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data
import pets as pet_lib


_battle_cooldowns: dict[str, datetime] = {}
BATTLE_COOLDOWN_MINUTES = 10


class Battle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="battle", description="Challenge another player's pet to an elemental battle!")
    @app_commands.describe(opponent="The user to challenge")
    async def battle(self, interaction: discord.Interaction, opponent: discord.Member):
        user_id = str(interaction.user.id)
        opp_id  = str(opponent.id)

        if opponent.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't battle yourself!", ephemeral=True)
            return
        if opponent.bot:
            await interaction.response.send_message("❌ You can't battle a bot!", ephemeral=True)
            return

        last = _battle_cooldowns.get(user_id)
        if last and (datetime.utcnow() - last) < timedelta(minutes=BATTLE_COOLDOWN_MINUTES):
            mins = int((timedelta(minutes=BATTLE_COOLDOWN_MINUTES) - (datetime.utcnow() - last)).total_seconds() / 60)
            await interaction.response.send_message(f"⏰ Your pet needs to recover! Battle again in **{mins}m**.", ephemeral=True)
            return

        my_pet  = data.get_active_pet(user_id)
        opp_pet = data.get_active_pet(opp_id)

        if not my_pet:
            msg = "🥚 Your pet hasn't hatched!" if data.get_active_pet_or_egg(user_id) else "❌ You don't have a pet!"
            await interaction.response.send_message(msg, ephemeral=True)
            return
        if not opp_pet:
            await interaction.response.send_message(f"❌ **{opponent.display_name}** doesn't have a hatched pet!", ephemeral=True)
            return

        my_pet  = pet_lib.apply_time_decay(my_pet)
        opp_pet = pet_lib.apply_time_decay(opp_pet)

        my_s   = pet_lib.SPECIES.get(my_pet["species"],  pet_lib.SPECIES["cat"])
        opp_s  = pet_lib.SPECIES.get(opp_pet["species"], pet_lib.SPECIES["cat"])
        my_elem   = my_s["element"]
        opp_elem  = opp_s["element"]
        elem_mult = pet_lib.element_multiplier(my_elem, opp_elem)
        opp_mult  = pet_lib.element_multiplier(opp_elem, my_elem)

        my_equip  = my_pet.get("equipment") or {}
        opp_equip = opp_pet.get("equipment") or {}

        my_base  = pet_lib.battle_score(my_pet,  my_equip)
        opp_base = pet_lib.battle_score(opp_pet, opp_equip)

        my_score  = int(my_base  * elem_mult)  + random.randint(-10, 10)
        opp_score = int(opp_base * opp_mult)   + random.randint(-10, 10)

        my_emoji  = my_s["emoji"]
        opp_emoji = opp_s["emoji"]
        my_elem_e  = pet_lib.ELEMENT_COLORS.get(my_elem,  "")
        opp_elem_e = pet_lib.ELEMENT_COLORS.get(opp_elem, "")

        _battle_cooldowns[user_id] = datetime.utcnow()

        my_player  = data.get_player(user_id)
        opp_player = data.get_player(opp_id)

        # Build elemental flavour note
        if elem_mult > 1.0:
            elem_note = f"⚡ **{my_elem}** is strong against **{opp_elem}**! ({my_pet['name']} +50% dmg)"
        elif elem_mult < 1.0:
            elem_note = f"🛡️ **{opp_elem}** resists **{my_elem}**! ({my_pet['name']} -35% dmg)"
        else:
            elem_note = f"⚖️ Neutral elements — no advantage either way."

        embed = discord.Embed(
            title="⚔️ Elemental Pet Battle!",
            description=(
                f"{my_emoji} **{my_pet['name']}** ({my_elem_e}{my_elem}, Lv.{my_pet['level']}) "
                f"vs {opp_emoji} **{opp_pet['name']}** ({opp_elem_e}{opp_elem}, Lv.{opp_pet['level']})"
            ),
            color=discord.Color.red()
        )
        embed.add_field(name="🌊 Element Matchup", value=elem_note, inline=False)

        # Battle rounds
        rounds = []
        my_wins = opp_wins = 0
        for i in range(3):
            r_my  = random.randint(1, 6) + my_pet["level"] + (2 if elem_mult > 1.0 else 0)
            r_opp = random.randint(1, 6) + opp_pet["level"] + (2 if opp_mult > 1.0 else 0)
            if r_my > r_opp:
                rounds.append(f"Round {i+1}: {my_emoji} **{my_pet['name']}** strikes! ✅")
                my_wins += 1
            elif r_opp > r_my:
                rounds.append(f"Round {i+1}: {opp_emoji} **{opp_pet['name']}** counters! ✅")
                opp_wins += 1
            else:
                rounds.append(f"Round {i+1}: 🤝 Both hit simultaneously!")

        embed.add_field(name="⚔️ Battle Log", value="\n".join(rounds), inline=False)

        if my_score > opp_score:
            result, outcome_msg = "win",  f"🏆 **{my_pet['name']}** wins!"
        elif opp_score > my_score:
            result, outcome_msg = "lose", f"💔 **{my_pet['name']}** lost!"
        else:
            result, outcome_msg = "draw", "🤝 It's a draw!"

        opp_result = {"win":"lose","lose":"win","draw":"draw"}[result]
        rewards      = pet_lib.BATTLE_REWARDS[result]
        opp_rewards  = pet_lib.BATTLE_REWARDS[opp_result]

        # Fox species coin bonus
        if my_pet["species"] in ("fox", "kitsune"):
            rewards = dict(rewards); rewards["coins"] = int(rewards["coins"] * 1.25)
        if opp_pet["species"] in ("fox", "kitsune"):
            opp_rewards = dict(opp_rewards); opp_rewards["coins"] = int(opp_rewards["coins"] * 1.25)

        data.update_player(user_id, coins=my_player["coins"]   + rewards["coins"])
        data.update_player(opp_id,  coins=opp_player["coins"]  + opp_rewards["coins"])
        data.update_pet(my_pet["pet_id"],  xp=my_pet["xp"]   + rewards["xp"])
        data.update_pet(opp_pet["pet_id"], xp=opp_pet["xp"]  + opp_rewards["xp"])

        embed.add_field(
            name="🏅 Result",
            value=(
                f"{outcome_msg}\n"
                f"{my_emoji} **{my_pet['name']}**: +{rewards['coins']} 💰  +{rewards['xp']} XP\n"
                f"{opp_emoji} **{opp_pet['name']}**: +{opp_rewards['coins']} 💰  +{opp_rewards['xp']} XP"
            ),
            inline=False
        )

        # Level-ups
        my_level, my_leveled = pet_lib.check_level_up({"level": my_pet["level"], "xp": my_pet["xp"] + rewards["xp"]})
        if my_leveled:
            data.update_pet(my_pet["pet_id"], level=my_level, xp=0)
            embed.add_field(name="🎊 Level Up!", value=f"**{my_pet['name']}** is now Level {my_level}!", inline=False)

        opp_level, opp_leveled = pet_lib.check_level_up({"level": opp_pet["level"], "xp": opp_pet["xp"] + opp_rewards["xp"]})
        if opp_leveled:
            data.update_pet(opp_pet["pet_id"], level=opp_level, xp=0)
            embed.add_field(name="🎊 Level Up!", value=f"**{opp_pet['name']}** is now Level {opp_level}!", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the top pets in PetWorld")
    async def leaderboard(self, interaction: discord.Interaction):
        rows   = data.get_leaderboard(10)
        embed  = discord.Embed(title="🏆 PetWorld Leaderboard", color=discord.Color.gold())
        medals = ["🥇", "🥈", "🥉"]

        for i, row in enumerate(rows):
            medal    = medals[i] if i < 3 else f"{i+1}."
            emoji    = pet_lib.get_species_emoji(row.get("species") or "cat")
            pet_name = row.get("pet_name") or "No Pet"
            level    = row.get("level") or 0
            rar_e    = pet_lib.RARITY_EMOJI.get(row.get("rarity","common"),"⚪")
            s        = pet_lib.SPECIES.get(row.get("species",""), {})
            elem_e   = pet_lib.ELEMENT_COLORS.get(s.get("element",""), "")
            embed.add_field(
                name=f"{medal} {row['username']}",
                value=f"{emoji} **{pet_name}** Lv.{level} {rar_e}{elem_e} | 💰 {row['coins']}",
                inline=False
            )

        if not rows:
            embed.description = "No players yet! Use `/adopt` to start."

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Battle(bot))
