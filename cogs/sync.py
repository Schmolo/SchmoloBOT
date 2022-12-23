import discord
from discord import app_commands
from discord.ext import commands
import json

with open("configuration.json", "r") as config:
    data = json.load(config)
    guild_id = data["guild_id"]

guild_object = discord.Object(guild_id)

class Sync(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @app_commands.command(name = "sync", description="sync new commands")
    async def sync(self, interaction: discord.Interaction):
        ctx = await self.bot.get_context(interaction)
        fmt = await ctx.bot.tree.sync(guild=interaction.guild)
        await interaction.response.send_message(f"{interaction.user.mention} Synced {len(fmt)} commands")
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded")
        
async def setup(bot:commands.Bot):
    await bot.add_cog(Sync(bot), guilds=[guild_object])