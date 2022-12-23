import os
import discord
from discord import app_commands
from discord.ext import commands
import json
import asyncio

jsonFile = "configuration.json"
isFile = os.path.isfile(jsonFile)

if (not isFile):
    with open(jsonFile, "w") as config:
        dump = {"token": "TOKEN", "prefix": "#", "application_id": "APP ID", "guild_id": "GUILD ID"}
        json.dump(dump, config, indent=4)
        raise Exception("configuration.json has been created, please fill in the required information.")
else:
    with open("configuration.json", "r") as config:
        data = json.load(config)
        token = data["token"]
        prefix = data["prefix"]
        application_id = data["application_id"]
        guild_id = data["guild_id"]

intents = discord.Intents.all()

bot = commands.Bot(prefix, intents=intents, application_id=application_id)
tree = bot.tree

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            cogName = filename[:-3]
            await bot.load_extension(f"cogs.{cogName}")
            
async def main():
    async with bot:
        await load_extensions()
        await bot.start(token)
    
@tree.context_menu(name = "Sync", guild=discord.Object(guild_id))
async def sync(interaction: discord.Interaction, message: discord.Message):
        ctx = await bot.get_context(interaction)
        fmt = await ctx.bot.tree.sync(guild=interaction.guild)
        await interaction.response.send_message(f"{interaction.user.mention} Synced {len(fmt)} commands")

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{bot.command_prefix}help"))
    print(discord.__version__)

asyncio.run(main())