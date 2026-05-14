import discord
from discord.ext import commands
from discord import app_commands
import random

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data
import pets as pet_lib

# Pending trade offers: initiator_id -> {target_id, my_pet_id, target_pet_id}
_pending_trades: dict[str, dict] = {}


class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /setrival ─────────────────────────────────────────────────────────────

    @app_commands.command(name="setrival", description="Declare another player as your rival for bonus battle rewards")
    @app_commands.describe(rival="The player to set as your rival")
    async def setrival(self, interaction: discord.Interaction, rival: discord.Member):
        user_id  = str(interaction.user.id)
        rival_id = str(rival.id)

        if rival.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't set yourself as your rival!", ephemeral=True)
            return
        if rival.bot:
            await interaction.response.send_message("❌ Bots can't be rivals!", ephemeral=True)
            return

        rival_player = data.get_player(rival_id)
        if not rival_player:
            await interaction.response.send_message(
                f"❌ **{rival.display_name}** hasn't started playing PetWorld yet. "
                f"They need to `/adopt` a pet first!", ephemeral=True
            )
            return

        record = data.get_rival_record(user_id)
        changed = record.get("rival_id") and record["rival_id"] != rival_id

        data.set_rival(user_id, rival_id)

        embed = discord.Embed(
            title="⚔️ Rival Declared!",
            description=f"**{interaction.user.display_name}** has set **{rival.display_name}** as their rival!",
            color=discord.Color.red()
        )
        if changed:
            embed.add_field(name="🔄 Changed", value="Your previous rival record has been reset.", inline=False)
        embed.add_field(
            name="🎯 Rival Perks",
            value=(
                "🪙 **+30 bonus coins** every time you win a `/battle` against your rival\n"
                "🗡️ Progress toward the **Rival Slayer** badge (beat them 5 times)\n"
                "📊 Head-to-head record shown in your `/profile`"
            ),
            inline=False
        )
        rival_pet = data.get_active_pet(rival_id)
        if rival_pet:
            s_data = pet_lib.SPECIES.get(rival_pet["species"], {})
            evo_emoji, evo_title = pet_lib.get_evo_display(rival_pet["species"], rival_pet.get("evo_stage", 0))
            embed.add_field(
                name=f"🐾 {rival.display_name}'s Active Pet",
                value=(
                    f"{evo_emoji} **{rival_pet['name']}** — {evo_title}\n"
                    f"{s_data.get('emoji','')} {rival_pet['species'].capitalize()} | "
                    f"Lv.{rival_pet['level']} | "
                    f"{pet_lib.ELEMENT_COLORS.get(s_data.get('element',''),'')} {s_data.get('element','')}"
                ),
                inline=False
            )
        embed.set_footer(text="Use /battle to challenge your rival and earn bonus rewards!")
        await interaction.response.send_message(embed=embed)

    # ── /rename ───────────────────────────────────────────────────────────────

    @app_commands.command(name="rename", description="Give your active pet a new name")
    @app_commands.describe(newname="The new name for your pet (max 32 chars)")
    async def rename(self, interaction: discord.Interaction, newname: str):
        user_id = str(interaction.user.id)
        newname = newname.strip()

        if not newname or len(newname) > 32:
            await interaction.response.send_message("❌ Name must be 1–32 characters.", ephemeral=True)
            return

        pet = data.get_active_pet(user_id)
        if not pet:
            if data.get_active_pet_or_egg(user_id):
                await interaction.response.send_message("🥚 Your egg hasn't hatched yet!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ You don't have a pet to rename.", ephemeral=True)
            return

        old_name = pet["name"]
        data.update_pet(pet["pet_id"], name=newname)

        s_data    = pet_lib.SPECIES.get(pet["species"], {})
        evo_emoji, evo_title = pet_lib.get_evo_display(pet["species"], pet.get("evo_stage", 0))
        embed = discord.Embed(
            title="✏️ Pet Renamed!",
            description=f"**{old_name}** is now known as **{newname}**!",
            color=discord.Color.from_rgb(255, 182, 193)
        )
        embed.add_field(
            name="Pet",
            value=f"{evo_emoji} {s_data.get('emoji','')} {pet['species'].capitalize()} — {evo_title} · Lv.{pet['level']}",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    # ── /trade ────────────────────────────────────────────────────────────────

    @app_commands.command(name="trade", description="Offer to trade one of your pets with another player")
    @app_commands.describe(
        partner="The player you want to trade with",
        petname="The name of YOUR pet you're offering in the trade"
    )
    async def trade(self, interaction: discord.Interaction, partner: discord.Member, petname: str):
        user_id = str(interaction.user.id)
        opp_id  = str(partner.id)

        if partner.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't trade with yourself!", ephemeral=True)
            return
        if partner.bot:
            await interaction.response.send_message("❌ Bots can't trade pets!", ephemeral=True)
            return

        # Block if either player already has a pending trade
        if user_id in _pending_trades:
            await interaction.response.send_message("❌ You already have a pending trade offer! Wait for it to resolve.", ephemeral=True)
            return

        # Find the offered pet by name in the initiator's collection
        all_pets  = data.get_all_pets(user_id)
        my_pet    = next((p for p in all_pets if p["name"].lower() == petname.lower() and not p.get("is_egg")), None)
        if not my_pet:
            await interaction.response.send_message(
                f"❌ No hatched pet named **{petname}** found. Use `/mypets` to see your collection.", ephemeral=True
            )
            return

        # Get target's active pet
        opp_pet = data.get_active_pet(opp_id)
        if not opp_pet:
            await interaction.response.send_message(
                f"❌ **{partner.display_name}** doesn't have an active pet to trade.", ephemeral=True
            )
            return

        # Register pending trade
        _pending_trades[user_id] = {
            "target_id":     opp_id,
            "my_pet_id":     my_pet["pet_id"],
            "target_pet_id": opp_pet["pet_id"],
        }

        my_s   = pet_lib.SPECIES.get(my_pet["species"], {})
        opp_s  = pet_lib.SPECIES.get(opp_pet["species"], {})
        my_evo_emoji,  my_evo_title  = pet_lib.get_evo_display(my_pet["species"],  my_pet.get("evo_stage", 0))
        opp_evo_emoji, opp_evo_title = pet_lib.get_evo_display(opp_pet["species"], opp_pet.get("evo_stage", 0))
        my_rar  = pet_lib.RARITY_EMOJI.get(my_pet.get("rarity",  "common"), "⚪")
        opp_rar = pet_lib.RARITY_EMOJI.get(opp_pet.get("rarity"), "⚪")

        embed = discord.Embed(
            title="🔄 Trade Offer!",
            description=f"{interaction.user.mention} wants to trade with {partner.mention}!",
            color=discord.Color.from_rgb(100, 200, 255)
        )
        embed.add_field(
            name=f"🟦 {interaction.user.display_name} offers:",
            value=(
                f"{my_evo_emoji} **{my_pet['name']}** — {my_evo_title}\n"
                f"{my_s.get('emoji','')} {my_pet['species'].capitalize()} {my_rar} Lv.{my_pet['level']}\n"
                f"{pet_lib.ELEMENT_COLORS.get(my_s.get('element',''),'')} {my_s.get('element','')}"
            ),
            inline=True
        )
        embed.add_field(name="⇄", value="\u200b", inline=True)
        embed.add_field(
            name=f"🟥 {partner.display_name}'s active pet:",
            value=(
                f"{opp_evo_emoji} **{opp_pet['name']}** — {opp_evo_title}\n"
                f"{opp_s.get('emoji','')} {opp_pet['species'].capitalize()} {opp_rar} Lv.{opp_pet['level']}\n"
                f"{pet_lib.ELEMENT_COLORS.get(opp_s.get('element',''),'')} {opp_s.get('element','')}"
            ),
            inline=True
        )
        embed.set_footer(text=f"{partner.display_name}: Accept or Decline below. Offer expires in 2 minutes.")

        view = TradeResponseView(interaction.user, partner, user_id, opp_id, my_pet, opp_pet)
        await interaction.response.send_message(embed=embed, view=view)


class TradeResponseView(discord.ui.View):
    def __init__(self, initiator: discord.Member, target: discord.Member,
                 initiator_id: str, target_id: str, my_pet: dict, opp_pet: dict):
        super().__init__(timeout=120)
        self.initiator    = initiator
        self.target       = target
        self.initiator_id = initiator_id
        self.target_id    = target_id
        self.my_pet       = my_pet
        self.opp_pet      = opp_pet

    async def on_timeout(self):
        _pending_trades.pop(self.initiator_id, None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.target_id:
            await interaction.response.send_message("❌ Only the challenged player can respond to this trade.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="✅ Accept Trade", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        _pending_trades.pop(self.initiator_id, None)

        # Verify pets still exist and belong to correct owners
        my_pet_now  = data.get_pet_by_id(self.my_pet["pet_id"])
        opp_pet_now = data.get_pet_by_id(self.opp_pet["pet_id"])

        if not my_pet_now or str(my_pet_now["user_id"]) != self.initiator_id:
            await interaction.response.edit_message(content="❌ Trade failed — the offered pet is no longer available.", embed=None, view=None)
            return
        if not opp_pet_now or str(opp_pet_now["user_id"]) != self.target_id:
            await interaction.response.edit_message(content="❌ Trade failed — your active pet is no longer available.", embed=None, view=None)
            return

        # Swap ownership
        data.update_pet(self.my_pet["pet_id"],  user_id=self.target_id)
        data.update_pet(self.opp_pet["pet_id"], user_id=self.initiator_id)

        # Make both pets active for their new owners
        data.update_pet(self.my_pet["pet_id"],  is_active=1)
        data.update_pet(self.opp_pet["pet_id"], is_active=1)

        my_s   = pet_lib.SPECIES.get(self.my_pet["species"], {})
        opp_s  = pet_lib.SPECIES.get(self.opp_pet["species"], {})
        my_evo_emoji,  _ = pet_lib.get_evo_display(self.my_pet["species"],  self.my_pet.get("evo_stage", 0))
        opp_evo_emoji, _ = pet_lib.get_evo_display(self.opp_pet["species"], self.opp_pet.get("evo_stage", 0))

        embed = discord.Embed(
            title="✅ Trade Complete!",
            description="The pets have been swapped!",
            color=discord.Color.green()
        )
        embed.add_field(
            name=f"{self.initiator.display_name} received:",
            value=f"{opp_evo_emoji} **{self.opp_pet['name']}** the {opp_s.get('emoji','')} {self.opp_pet['species'].capitalize()}",
            inline=True
        )
        embed.add_field(
            name=f"{self.target.display_name} received:",
            value=f"{my_evo_emoji} **{self.my_pet['name']}** the {my_s.get('emoji','')} {self.my_pet['species'].capitalize()}",
            inline=True
        )
        await interaction.response.edit_message(embed=embed, view=None, content=None)

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        _pending_trades.pop(self.initiator_id, None)
        await interaction.response.edit_message(
            content=f"💔 **{self.target.display_name}** declined the trade offer.", embed=None, view=None
        )


async def setup(bot):
    await bot.add_cog(Social(bot))
