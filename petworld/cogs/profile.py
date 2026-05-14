import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data
import pets as pet_lib

TRAINER_LEVELS = [
    (8, "🌟 Legendary Trainer"),
    (6, "🏆 Master Trainer"),
    (4, "💎 Expert Trainer"),
    (2, "⚔️ Apprentice Trainer"),
    (1, "🛡️ Rookie Trainer"),
    (0, "🌱 Novice Trainer"),
]

def trainer_title(badge_count: int) -> tuple[int, str]:
    for min_b, title in TRAINER_LEVELS:
        if badge_count >= min_b:
            level = TRAINER_LEVELS.index((min_b, title)) + 1
            return len(TRAINER_LEVELS) - TRAINER_LEVELS.index((min_b, title)), title
    return 1, "🌱 Novice Trainer"


class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="View your trainer profile, badges, and stats")
    @app_commands.describe(user="Player to view (leave blank for yourself)")
    async def profile(self, interaction: discord.Interaction, user: discord.Member = None):
        target      = user or interaction.user
        user_id     = str(target.id)
        player      = data.get_player(user_id)

        if not player:
            who = "You haven't" if target == interaction.user else f"**{target.display_name}** hasn't"
            await interaction.response.send_message(f"❌ {who} started playing yet! Use `/adopt` to begin.", ephemeral=True)
            return

        # Gather stats
        stats    = data.get_player_stats(user_id)
        badges   = data.get_achievements(user_id)
        # Check for any newly earned badges
        data.check_and_award_achievements(user_id)
        badges   = data.get_achievements(user_id)

        badge_count           = len(badges)
        trainer_lvl, t_title  = trainer_title(badge_count)
        active_pet            = data.get_active_pet(user_id)
        all_pets_count        = stats.get("total_pets", 0)

        # Pet info
        if active_pet:
            s_data    = pet_lib.SPECIES.get(active_pet["species"], {})
            evo_emoji, evo_title = pet_lib.get_evo_display(active_pet["species"], active_pet.get("evo_stage", 0))
            elem_e    = pet_lib.ELEMENT_COLORS.get(s_data.get("element", ""), "")
            rar_e     = pet_lib.RARITY_EMOJI.get(active_pet.get("rarity", "common"), "⚪")
            pet_str   = (
                f"{evo_emoji} **{active_pet['name']}** — {evo_title}\n"
                f"{s_data.get('species', active_pet['species']).capitalize() if False else active_pet['species'].capitalize()} "
                f"{rar_e} {elem_e} | Lv.{active_pet['level']} | "
                f"XP: {active_pet['xp']}/{pet_lib.xp_for_next_level(active_pet['level'])}"
            )
        else:
            pet_str = "*No active pet*"

        # Badge display
        badge_lines = []
        for badge_id in badges:
            info = data.BADGE_INFO.get(badge_id, {})
            badge_lines.append(f"{info.get('emoji','🏅')} **{info.get('label', badge_id)}** — _{info.get('desc', '')}_")

        # Member duration
        joined_str = ""
        try:
            created = datetime.fromisoformat(player["created_at"])
            days    = (datetime.utcnow() - created).days
            joined_str = f"{days} day{'s' if days != 1 else ''} ago"
        except Exception:
            pass

        color = discord.Color.from_rgb(100, 149, 237)
        embed = discord.Embed(
            title=f"🧑‍🎓 {target.display_name}'s Trainer Profile",
            color=color
        )
        embed.add_field(name="🎖️ Trainer Level", value=f"**{trainer_lvl}** — {t_title}", inline=True)
        embed.add_field(name="💰 Coins",          value=f"**{player['coins']}**",         inline=True)
        embed.add_field(name="🐾 Pets Owned",     value=f"**{all_pets_count}**",          inline=True)
        embed.add_field(name="📊 Stats",
            value=(
                f"Battles Won: **{stats.get('total_battles_won', 0)}**\n"
                f"Eggs Hatched: **{stats.get('total_eggs_hatched', 0)}**\n"
                f"Pets Bred: **{stats.get('total_pets_bred', 0)}**\n"
                f"Daily Quests Done: **{stats.get('total_daily_quests_done', 0)}**"
            ),
            inline=True
        )
        if joined_str:
            embed.add_field(name="📅 Playing For", value=joined_str, inline=True)

        embed.add_field(name="\u200b", value="\u200b", inline=True)

        embed.add_field(name=f"🐾 Active Pet", value=pet_str, inline=False)

        if badge_lines:
            embed.add_field(
                name=f"🏅 Badges ({badge_count}/{len(data.BADGE_INFO)})",
                value="\n".join(badge_lines),
                inline=False
            )
        else:
            locked_preview = "\n".join(
                f"🔒 {info.get('emoji','🏅')} {info.get('label','?')} — _{info.get('desc','')}_"
                for info in data.BADGE_INFO.values()
            )
            embed.add_field(
                name=f"🏅 Badges (0/{len(data.BADGE_INFO)})",
                value=f"No badges yet! Here's what you can earn:\n{locked_preview}",
                inline=False
            )

        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text="Use /quests, /battle, /hunt and more to earn badges!")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Profile(bot))
