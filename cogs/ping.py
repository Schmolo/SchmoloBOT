import discord
from discord import app_commands
from discord.ext import commands
import json

with open("configuration.json", "r") as config:
    data = json.load(config)
    guild_id = data["guild_id"]

guild_object = discord.Object(guild_id)

class Ping(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name = "ping", description="Pong!", with_app_command=True)
    @app_commands.guilds(guild_object)
    async def ping(self, ctx:commands.Context):
        await ctx.reply("Pong!")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded")

async def setup(bot:commands.Bot):
    await bot.add_cog(Ping(bot), guilds=[guild_object])