import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data
import pets as pet_lib
import quests as quest_lib


class Quests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="quests", description="View your daily and weekly quests and claim completed rewards")
    async def quests(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        pet = data.get_active_pet(user_id)
        if not pet:
            if data.get_active_pet_or_egg(user_id):
                await interaction.response.send_message("🥚 Hatch your egg first to receive quests!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ You need a pet to receive quests! Use `/adopt`.", ephemeral=True)
            return

        species_data = pet_lib.SPECIES.get(pet["species"], pet_lib.SPECIES["cat"])
        element      = species_data["element"]
        elem_emoji   = pet_lib.ELEMENT_COLORS.get(element, "")

        # Generate new quests if needed
        active_quests = data.ensure_user_quests(user_id, element)

        if not active_quests:
            await interaction.response.send_message("❌ No quests available. Try again shortly.", ephemeral=True)
            return

        daily_qs  = [q for q in active_quests if q["quest_type"] == "daily"]
        weekly_qs = [q for q in active_quests if q["quest_type"] == "weekly"]

        embed = discord.Embed(
            title=f"📋 Quests — {elem_emoji} {element} Element",
            description=f"Quests for **{pet['name']}** the {species_data['emoji']} {pet['species'].capitalize()}",
            color=discord.Color.from_rgb(255, 200, 50)
        )

        def quest_line(q: dict) -> str:
            status = q["status"]
            progress = q["progress"]
            target   = q["target"]
            bar_filled = int(progress / target * 8)
            bar = "█" * bar_filled + "░" * (8 - bar_filled)
            rewards = f"💰{q['reward_coins']} ✨{q['reward_xp']}"
            if q.get("reward_item"):
                item_d = pet_lib.SHOP_ITEMS.get(q["reward_item"], {})
                rewards += f" {item_d.get('emoji','📦')}{q['reward_item'].replace('_',' ').title()}"
            if status == "completed":
                prefix = "✅ **DONE** — use the button below to claim!"
            elif status == "claimed":
                prefix = "🎁 Claimed"
            else:
                prefix = f"[{bar}] {progress}/{target}"
            # Time remaining
            try:
                expires = datetime.fromisoformat(q["expires_at"])
                remaining = expires - datetime.utcnow()
                if remaining.total_seconds() > 0:
                    h = int(remaining.total_seconds() // 3600)
                    m = int((remaining.total_seconds() % 3600) // 60)
                    time_str = f"⏳ {h}h {m}m left"
                else:
                    time_str = "⌛ Expired"
            except Exception:
                time_str = ""
            return f"{prefix}\n*Reward: {rewards}* | {time_str}"

        if daily_qs:
            embed.add_field(name="📅 Daily Quests", value="\u200b", inline=False)
            for q in daily_qs:
                embed.add_field(
                    name=f"{'✅' if q['status']=='completed' else ('🎁' if q['status']=='claimed' else '🔵')} {q['description']}",
                    value=quest_line(q),
                    inline=False
                )

        if weekly_qs:
            embed.add_field(name="📆 Weekly Quest", value="\u200b", inline=False)
            for q in weekly_qs:
                embed.add_field(
                    name=f"{'✅' if q['status']=='completed' else ('🎁' if q['status']=='claimed' else '🟡')} {q['description']}",
                    value=quest_line(q),
                    inline=False
                )

        # Check for claimable quests
        claimable = [q for q in active_quests if q["status"] == "completed"]
        view = None
        if claimable:
            view = ClaimQuestsView(claimable, pet)
            embed.set_footer(text="You have completed quests! Click Claim Rewards below.")
        else:
            embed.set_footer(text="Complete actions to make progress. Quests reset daily/weekly.")

        await interaction.response.send_message(embed=embed, view=view)


class ClaimQuestsView(discord.ui.View):
    def __init__(self, claimable: list, pet: dict):
        super().__init__(timeout=60)
        self.claimable = claimable
        self.pet = pet

    @discord.ui.button(label="🎁 Claim All Rewards", style=discord.ButtonStyle.success)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id     = str(interaction.user.id)
        player      = data.get_player(user_id)
        total_coins = 0
        total_xp    = 0
        items_got   = []

        for q in self.claimable:
            if q["status"] != "completed":
                continue
            data.claim_quest(q["id"])
            total_coins += q["reward_coins"]
            total_xp    += q["reward_xp"]
            if q.get("reward_item"):
                data.add_item(user_id, q["reward_item"])
                items_got.append(q["reward_item"])

        if total_coins:
            data.update_player(user_id, coins=player["coins"] + total_coins)

        daily_count = sum(1 for q in self.claimable if q.get("quest_type") == "daily")
        if daily_count:
            data.increment_stat(user_id, "total_daily_quests_done", daily_count)

        pet_fresh = data.get_active_pet(user_id)
        level_msg = ""
        if pet_fresh and total_xp:
            lu = pet_lib.process_level_up(
                pet_fresh["species"], pet_fresh["level"],
                pet_fresh["xp"], total_xp,
                pet_fresh.get("evo_stage", 0)
            )
            data.update_pet(pet_fresh["pet_id"], xp=lu["new_xp"])
            if lu["leveled_up"]:
                data.update_pet(pet_fresh["pet_id"], level=lu["new_level"])
                if lu["evolved"]:
                    data.update_pet(pet_fresh["pet_id"], evo_stage=lu["new_evo_stage"])
                level_msg = f"\n🎊 **{pet_fresh['name']}** levelled up to **{lu['new_level']}**!"
                if lu["evolved"]:
                    evo = lu["evo_info"]
                    level_msg += f"\n✨ **EVOLUTION!** → {evo['emoji']} **{evo['title']}** (+{evo['stat_boost']} to all stats!)"
                    data.apply_evo_stat_boost(pet_fresh["pet_id"], evo["stat_boost"])

        new_badges = data.check_and_award_achievements(user_id)

        embed = discord.Embed(
            title="🎁 Quest Rewards Claimed!",
            description=f"💰 **+{total_coins} coins** | ✨ **+{total_xp} XP**{level_msg}",
            color=discord.Color.gold()
        )
        if items_got:
            item_lines = []
            for item_name in items_got:
                item_d = pet_lib.SHOP_ITEMS.get(item_name, {})
                item_lines.append(f"{item_d.get('emoji','📦')} {item_name.replace('_',' ').title()}")
            embed.add_field(name="📦 Items Received", value="\n".join(item_lines), inline=False)
        for badge in new_badges:
            b = data.BADGE_INFO.get(badge, {})
            embed.add_field(name="🏅 Badge Unlocked!", value=f"{b.get('emoji','')} **{b.get('label', badge)}** — _{b.get('desc','')}_", inline=False)
        embed.set_footer(text="New quests will be available after your current ones expire.")
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot):
    await bot.add_cog(Quests(bot))
