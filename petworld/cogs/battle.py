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


def _handle_levelup(embed: discord.Embed, pet: dict, xp_reward: int):
    lu = pet_lib.process_level_up(
        pet["species"], pet["level"], pet["xp"], xp_reward, pet.get("evo_stage", 0)
    )
    db_updates = {"xp": lu["new_xp"]}
    if lu["leveled_up"]:
        db_updates["level"] = lu["new_level"]
        if lu["evolved"]:
            db_updates["evo_stage"] = lu["new_evo_stage"]
    data.update_pet(pet["pet_id"], **db_updates)

    if lu["leveled_up"]:
        embed.add_field(name="🎊 Level Up!", value=f"**{pet['name']}** reached Level **{lu['new_level']}**!", inline=False)
    if lu["evolved"]:
        evo = lu["evo_info"]
        embed.add_field(
            name="✨ EVOLUTION!",
            value=f"**{pet['name']}** evolved into **{evo['emoji']} {evo['title']}**! (+{evo['stat_boost']} all stats)",
            inline=False
        )
        data.apply_evo_stat_boost(pet["pet_id"], evo["stat_boost"])


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
            await interaction.response.send_message(f"⏰ Battle cooldown: **{mins}m** remaining.", ephemeral=True)
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

        my_score  = int(pet_lib.battle_score(my_pet,  my_equip)  * elem_mult)  + random.randint(-10, 10)
        opp_score = int(pet_lib.battle_score(opp_pet, opp_equip) * opp_mult)   + random.randint(-10, 10)

        my_evo_emoji,  _ = pet_lib.get_evo_display(my_pet["species"],  my_pet.get("evo_stage", 0))
        opp_evo_emoji, _ = pet_lib.get_evo_display(opp_pet["species"], opp_pet.get("evo_stage", 0))
        my_elem_e  = pet_lib.ELEMENT_COLORS.get(my_elem, "")
        opp_elem_e = pet_lib.ELEMENT_COLORS.get(opp_elem, "")

        _battle_cooldowns[user_id] = datetime.utcnow()

        my_player  = data.get_player(user_id)
        opp_player = data.get_player(opp_id)

        if elem_mult > 1.0:
            elem_note = f"⚡ **{my_elem}** is strong vs **{opp_elem}**! (+50% dmg)"
        elif elem_mult < 1.0:
            elem_note = f"🛡️ **{opp_elem}** resists **{my_elem}**! (-35% dmg)"
        else:
            elem_note = "⚖️ Neutral matchup."

        embed = discord.Embed(
            title="⚔️ Elemental Pet Battle!",
            description=(
                f"{my_evo_emoji} **{my_pet['name']}** ({my_elem_e}{my_elem}, Lv.{my_pet['level']}) "
                f"vs {opp_evo_emoji} **{opp_pet['name']}** ({opp_elem_e}{opp_elem}, Lv.{opp_pet['level']})"
            ),
            color=discord.Color.red()
        )
        embed.add_field(name="🌊 Element Matchup", value=elem_note, inline=False)

        rounds = []
        for i in range(3):
            r_my  = random.randint(1, 6) + my_pet["level"]  + (2 if elem_mult > 1.0 else 0)
            r_opp = random.randint(1, 6) + opp_pet["level"] + (2 if opp_mult  > 1.0 else 0)
            if r_my > r_opp:
                rounds.append(f"Round {i+1}: {my_evo_emoji} **{my_pet['name']}** strikes! ✅")
            elif r_opp > r_my:
                rounds.append(f"Round {i+1}: {opp_evo_emoji} **{opp_pet['name']}** counters! ✅")
            else:
                rounds.append(f"Round {i+1}: 🤝 Simultaneous hit!")

        embed.add_field(name="⚔️ Battle Log", value="\n".join(rounds), inline=False)

        if my_score > opp_score:
            result, outcome_msg = "win",  f"🏆 **{my_pet['name']}** wins!"
        elif opp_score > my_score:
            result, outcome_msg = "lose", f"💔 **{my_pet['name']}** lost!"
        else:
            result, outcome_msg = "draw", "🤝 It's a draw!"

        opp_result  = {"win":"lose","lose":"win","draw":"draw"}[result]
        rewards     = dict(pet_lib.BATTLE_REWARDS[result])
        opp_rewards = dict(pet_lib.BATTLE_REWARDS[opp_result])

        # Fox/kitsune coin bonus
        if my_pet["species"]  in ("fox", "kitsune"): rewards["coins"]     = int(rewards["coins"]     * 1.25)
        if opp_pet["species"] in ("fox", "kitsune"): opp_rewards["coins"] = int(opp_rewards["coins"] * 1.25)

        data.update_player(user_id, coins=my_player["coins"]  + rewards["coins"])
        data.update_player(opp_id,  coins=opp_player["coins"] + opp_rewards["coins"])

        embed.add_field(
            name="🏅 Result",
            value=(
                f"{outcome_msg}\n"
                f"{my_evo_emoji} **{my_pet['name']}**: +{rewards['coins']} 💰  +{rewards['xp']} XP\n"
                f"{opp_evo_emoji} **{opp_pet['name']}**: +{opp_rewards['coins']} 💰  +{opp_rewards['xp']} XP"
            ),
            inline=False
        )

        _handle_levelup(embed, my_pet,  rewards["xp"])
        _handle_levelup(embed, opp_pet, opp_rewards["xp"])

        # Rival bonus
        record = data.get_rival_record(user_id)
        rival_id_set = str(record.get("rival_id") or "")
        if rival_id_set == opp_id:
            if result == "win":
                rival_bonus = 30
                winner_now  = data.get_player(user_id)
                data.update_player(user_id, coins=winner_now["coins"] + rival_bonus)
                data.increment_stat(user_id, "rival_wins")
                embed.add_field(
                    name="🗡️ Rival Defeated!",
                    value=f"⚔️ You beat your rival! **+{rival_bonus} bonus coins**",
                    inline=False
                )
            elif result == "lose":
                data.increment_stat(user_id, "rival_losses")

        # Quest + achievement tracking
        data.track_quest_action(user_id, "battle")
        if result == "win":
            data.increment_stat(user_id, "total_battles_won")
            completed = data.track_quest_action(user_id, "win_battle")
            for q in completed:
                embed.add_field(name="✅ Quest Complete!", value=f"**{q['description']}** — `/quests` to claim!", inline=False)

        new_badges = data.check_and_award_achievements(user_id)
        for badge in new_badges:
            b = data.BADGE_INFO.get(badge, {})
            embed.add_field(name="🏅 Badge Unlocked!", value=f"{b.get('emoji','')} **{b.get('label', badge)}** — _{b.get('desc','')}_", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the top pets in PetWorld")
    async def leaderboard(self, interaction: discord.Interaction):
        rows  = data.get_leaderboard(10)
        embed = discord.Embed(title="🏆 PetWorld Leaderboard", color=discord.Color.gold())
        medals = ["🥇", "🥈", "🥉"]

        for i, row in enumerate(rows):
            medal    = medals[i] if i < 3 else f"{i+1}."
            species  = row.get("species") or "cat"
            s        = pet_lib.SPECIES.get(species, {})
            evo_emoji, evo_title = pet_lib.get_evo_display(species, row.get("evo_stage", 0) or 0)
            rar_e    = pet_lib.RARITY_EMOJI.get(row.get("rarity", "common"), "⚪")
            elem_e   = pet_lib.ELEMENT_COLORS.get(s.get("element", ""), "")
            pet_name = row.get("pet_name") or "No Pet"
            embed.add_field(
                name=f"{medal} {row['username']}",
                value=f"{evo_emoji} **{pet_name}** {evo_title} Lv.{row.get('level',0)} {rar_e}{elem_e} | 💰 {row['coins']}",
                inline=False
            )

        if not rows:
            embed.description = "No players yet! Use `/adopt` to start."
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Battle(bot))
