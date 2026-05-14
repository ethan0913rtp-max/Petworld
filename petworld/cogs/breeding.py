import discord
from discord.ext import commands
from discord import app_commands
import random

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import data
import pets as pet_lib


# In-memory pending requests: requester_id → target_id  (simple; replaced by DB record)
_pending: dict[str, str] = {}


class Breeding(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="breed", description="Request to breed your pet with another player's pet")
    @app_commands.describe(partner="The player whose pet you want to breed with")
    async def breed(self, interaction: discord.Interaction, partner: discord.Member):
        user_id = str(interaction.user.id)
        opp_id  = str(partner.id)

        if partner.id == interaction.user.id:
            await interaction.response.send_message("❌ You can't breed with yourself!", ephemeral=True)
            return
        if partner.bot:
            await interaction.response.send_message("❌ Bots can't breed pets!", ephemeral=True)
            return

        my_pet  = data.get_active_pet(user_id)
        opp_pet = data.get_active_pet(opp_id)

        if not my_pet:
            await interaction.response.send_message("❌ You need a hatched pet to breed. Use `/adopt` or `/hatch`.", ephemeral=True)
            return
        if not opp_pet:
            await interaction.response.send_message(f"❌ **{partner.display_name}** doesn't have a hatched pet.", ephemeral=True)
            return

        if my_pet["level"] < 3:
            await interaction.response.send_message(f"❌ **{my_pet['name']}** must be at least **Level 3** to breed.", ephemeral=True)
            return
        if opp_pet["level"] < 3:
            await interaction.response.send_message(f"❌ **{opp_pet['name']}** must be at least **Level 3** to breed.", ephemeral=True)
            return

        # Save request to DB
        data.create_breed_request(user_id, opp_id, my_pet["pet_id"], opp_pet["pet_id"])

        my_s   = pet_lib.SPECIES.get(my_pet["species"], {})
        opp_s  = pet_lib.SPECIES.get(opp_pet["species"], {})
        my_rar  = pet_lib.RARITY_EMOJI.get(my_pet.get("rarity","common"),"⚪")
        opp_rar = pet_lib.RARITY_EMOJI.get(opp_pet.get("rarity","common"),"⚪")

        embed = discord.Embed(
            title="💞 Breed Request Sent!",
            description=f"{interaction.user.mention} wants to breed with {partner.mention}!",
            color=discord.Color.pink()
        )
        embed.add_field(
            name=f"{my_s.get('emoji','')} {my_pet['name']} (Lv.{my_pet['level']}) {my_rar}",
            value=f"{pet_lib.ELEMENT_COLORS.get(my_s.get('element',''),'')} {my_s.get('element','')} | {my_pet.get('rarity','common').capitalize()}",
            inline=True
        )
        embed.add_field(name="💞", value="×", inline=True)
        embed.add_field(
            name=f"{opp_s.get('emoji','')} {opp_pet['name']} (Lv.{opp_pet['level']}) {opp_rar}",
            value=f"{pet_lib.ELEMENT_COLORS.get(opp_s.get('element',''),'')} {opp_s.get('element','')} | {opp_pet.get('rarity','common').capitalize()}",
            inline=True
        )
        embed.set_footer(text=f"{partner.display_name}: use /breed_accept or /breed_decline to respond.")

        view = BreedResponseView(partner, user_id, opp_id, my_pet, opp_pet)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="farm", description="View your eggs and bred pets")
    async def farm(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        all_pets = data.get_all_pets(user_id)

        eggs    = [p for p in all_pets if p.get("is_egg")]
        bred    = [p for p in all_pets if not p.get("is_egg") and (p.get("parent1_id") or p.get("parent2_id"))]

        embed = discord.Embed(title="🌾 Your Breed Farm", color=discord.Color.from_rgb(180, 220, 130))

        if eggs:
            embed.add_field(name="🥚 Eggs in Incubation", value="\u200b", inline=False)
            for e in eggs:
                s     = pet_lib.SPECIES.get(e["species"], {})
                hrs   = pet_lib.egg_hours_remaining(e["created_at"])
                rar_e = pet_lib.RARITY_EMOJI.get(e.get("rarity","common"),"⚪")
                if hrs <= 0:
                    status = "✅ **Ready to hatch!** Use `/hatch`"
                else:
                    h, m = int(hrs), int((hrs - int(hrs)) * 60)
                    status = f"⏳ {h}h {m}m remaining"
                parents = ""
                if e.get("parent1_id") and e.get("parent2_id"):
                    p1 = data.get_pet_by_id(e["parent1_id"])
                    p2 = data.get_pet_by_id(e["parent2_id"])
                    if p1 and p2:
                        parents = f"\nParents: {p1['name']} × {p2['name']}"
                embed.add_field(
                    name=f"{s.get('emoji','🥚')} {e['name']} — {e['species'].capitalize()} {rar_e}",
                    value=f"{status}{parents}",
                    inline=False
                )
        else:
            embed.add_field(name="🥚 Eggs", value="No eggs incubating. Use `/breed` to create one!", inline=False)

        if bred:
            embed.add_field(name="🧬 Bred Pets", value="\u200b", inline=False)
            for p in bred:
                s     = pet_lib.SPECIES.get(p["species"], {})
                rar_e = pet_lib.RARITY_EMOJI.get(p.get("rarity","common"),"⚪")
                p1    = data.get_pet_by_id(p["parent1_id"]) if p.get("parent1_id") else None
                p2    = data.get_pet_by_id(p["parent2_id"]) if p.get("parent2_id") else None
                parents = f"Parents: {p1['name']} × {p2['name']}" if p1 and p2 else ""
                status  = "✅ Active" if p["is_active"] else "💤 Retired"
                embed.add_field(
                    name=f"{s.get('emoji','🐾')} {p['name']} Lv.{p['level']} {rar_e}",
                    value=f"{status}\n{parents}",
                    inline=True
                )

        if not eggs and not bred:
            embed.description = "Your farm is empty! Use `/breed @user` to start breeding pets."

        await interaction.response.send_message(embed=embed)


class BreedResponseView(discord.ui.View):
    def __init__(self, target: discord.Member, requester_id: str, target_id: str, pet1: dict, pet2: dict):
        super().__init__(timeout=120)
        self.target       = target
        self.requester_id = requester_id
        self.target_id    = target_id
        self.pet1         = pet1
        self.pet2         = pet2

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.target_id:
            await interaction.response.send_message("❌ Only the challenged player can respond.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="💞 Accept Breed", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._do_breed(interaction)

    @discord.ui.button(label="❌ Decline", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content=f"💔 {interaction.user.mention} declined the breed request.", embed=None, view=None
        )

    async def _do_breed(self, interaction: discord.Interaction):
        r1 = self.pet1.get("rarity", "common")
        r2 = self.pet2.get("rarity", "common")

        # Determine offspring rarity & species
        offspring_rarity   = pet_lib.get_breed_rarity(r1, r2)
        offspring_species  = pet_lib.get_random_species_of_rarity(offspring_rarity, exclude_mammals=False)

        # Egg name blends parent names
        p1n = self.pet1["name"]
        p2n = self.pet2["name"]
        blend_name = p1n[:max(1, len(p1n)//2)] + p2n[max(0, len(p2n)//2):]

        s_data = pet_lib.SPECIES[offspring_species]
        is_egg = not s_data["is_mammal"]

        data.create_pet(
            self.requester_id, blend_name, offspring_species,
            is_egg=is_egg, rarity=offspring_rarity,
            parent1_id=self.pet1["pet_id"], parent2_id=self.pet2["pet_id"]
        )

        rar_e  = pet_lib.RARITY_EMOJI.get(offspring_rarity, "⚪")
        elem_e = pet_lib.ELEMENT_COLORS.get(s_data["element"], "")

        embed = discord.Embed(
            title="🧬 Breeding Successful!",
            description=f"**{self.pet1['name']}** × **{self.pet2['name']}** produced an offspring!",
            color=discord.Color.from_rgb(255, 150, 200)
        )
        embed.add_field(name="🐾 Offspring",  value=f"**{blend_name}** the {s_data['emoji']} {offspring_species.capitalize()}", inline=True)
        embed.add_field(name="Rarity",        value=f"{rar_e} {offspring_rarity.capitalize()}", inline=True)
        embed.add_field(name="Element",       value=f"{elem_e} {s_data['element']}", inline=True)
        if is_egg:
            embed.add_field(name="Status", value="🥚 It's an egg! Use `/hatch` in 24h (or use a 💎 `hatch_gem`).", inline=False)
        else:
            embed.add_field(name="Status", value="✅ Born and ready to play!", inline=False)
        embed.set_footer(text="Use /farm to view all your bred pets and eggs.")

        await interaction.response.edit_message(embed=embed, view=None, content=None)


async def setup(bot):
    await bot.add_cog(Breeding(bot))
