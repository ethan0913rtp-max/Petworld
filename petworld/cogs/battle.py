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

    @app_commands.command(name="battle", description="Challenge another player's pet to a battle!")
    @app_commands.describe(opponent="The user to challenge")
    async def battle(self, interaction: discord.Interaction, opponent: discord.Member):
        user_id = str(interaction.user.id)
        opp_id = str(opponent.id)

        if opponent.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't battle yourself!", ephemeral=True)
            return
        if opponent.bot:
            await interaction.response.send_message("❌ You can't battle a bot!", ephemeral=True)
            return

        last = _battle_cooldowns.get(user_id)
        if last:
            diff = datetime.utcnow() - last
            if diff < timedelta(minutes=BATTLE_COOLDOWN_MINUTES):
                remaining = int((timedelta(minutes=BATTLE_COOLDOWN_MINUTES) - diff).total_seconds() / 60)
                await interaction.response.send_message(
                    f"⏰ Your pet needs to recover! Battle again in **{remaining}m**.", ephemeral=True
                )
                return

        my_pet = data.get_active_pet(user_id)
        opp_pet = data.get_active_pet(opp_id)

        if not my_pet:
            await interaction.response.send_message("❌ You don't have a pet! Use `/adopt` first.", ephemeral=True)
            return
        if not opp_pet:
            await interaction.response.send_message(f"❌ **{opponent.display_name}** doesn't have a pet!", ephemeral=True)
            return

        my_pet = pet_lib.apply_time_decay(my_pet)
        opp_pet = pet_lib.apply_time_decay(opp_pet)

        my_score = pet_lib.battle_score(my_pet) + random.randint(-10, 10)
        opp_score = pet_lib.battle_score(opp_pet) + random.randint(-10, 10)

        my_emoji = pet_lib.get_species_emoji(my_pet["species"])
        opp_emoji = pet_lib.get_species_emoji(opp_pet["species"])

        _battle_cooldowns[user_id] = datetime.utcnow()

        my_player = data.get_player(user_id)
        opp_player = data.get_player(opp_id)

        embed = discord.Embed(
            title="⚔️ Pet Battle!",
            description=f"{my_emoji} **{my_pet['name']}** (Lv.{my_pet['level']}) vs {opp_emoji} **{opp_pet['name']}** (Lv.{opp_pet['level']})",
            color=discord.Color.red()
        )

        rounds = []
        for i in range(3):
            r_my = random.randint(1, 6) + my_pet["level"]
            r_opp = random.randint(1, 6) + opp_pet["level"]
            if r_my > r_opp:
                rounds.append(f"Round {i+1}: {my_emoji} **{my_pet['name']}** wins! ✅")
            elif r_opp > r_my:
                rounds.append(f"Round {i+1}: {opp_emoji} **{opp_pet['name']}** wins! ✅")
            else:
                rounds.append(f"Round {i+1}: 🤝 Draw!")

        embed.add_field(name="Battle Log", value="\n".join(rounds), inline=False)

        if my_score > opp_score:
            result = "win"
            outcome_msg = f"🏆 **{my_pet['name']}** wins!"
        elif opp_score > my_score:
            result = "lose"
            outcome_msg = f"💔 **{my_pet['name']}** lost!"
        else:
            result = "draw"
            outcome_msg = "🤝 It's a draw!"

        rewards = pet_lib.BATTLE_REWARDS[result]
        opp_result = "lose" if result == "win" else ("win" if result == "lose" else "draw")
        opp_rewards = pet_lib.BATTLE_REWARDS[opp_result]

        data.update_player(user_id, coins=my_player["coins"] + rewards["coins"])
        data.update_pet(my_pet["pet_id"], xp=my_pet["xp"] + rewards["xp"])
        data.update_player(opp_id, coins=opp_player["coins"] + opp_rewards["coins"])
        data.update_pet(opp_pet["pet_id"], xp=opp_pet["xp"] + opp_rewards["xp"])

        embed.add_field(
            name="Result",
            value=f"{outcome_msg}\n"
                  f"{my_emoji} **{my_pet['name']}**: +{rewards['coins']} 💰 +{rewards['xp']} XP\n"
                  f"{opp_emoji} **{opp_pet['name']}**: +{opp_rewards['coins']} 💰 +{opp_rewards['xp']} XP",
            inline=False
        )

        my_level, my_leveled = pet_lib.check_level_up({"level": my_pet["level"], "xp": my_pet["xp"] + rewards["xp"]})
        if my_leveled:
            data.update_pet(my_pet["pet_id"], level=my_level, xp=0)
            embed.add_field(name="🎊 Level Up!", value=f"**{my_pet['name']}** is now Level {my_level}!", inline=False)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the top pets in PetWorld")
    async def leaderboard(self, interaction: discord.Interaction):
        rows = data.get_leaderboard(10)
        embed = discord.Embed(title="🏆 PetWorld Leaderboard", color=discord.Color.gold())

        medals = ["🥇", "🥈", "🥉"]
        for i, row in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i+1}."
            emoji = pet_lib.get_species_emoji(row.get("species") or "cat")
            pet_name = row.get("pet_name") or "No Pet"
            level = row.get("level") or 0
            embed.add_field(
                name=f"{medal} {row['username']}",
                value=f"{emoji} **{pet_name}** — Level {level} | 💰 {row['coins']} coins",
                inline=False
            )

        if not rows:
            embed.description = "No players yet! Use `/adopt` to start playing."

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Battle(bot))
