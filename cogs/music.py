import discord
from discord import app_commands
from discord.ext import commands
import youtube_dl
import asyncio
import json

with open("configuration.json", "r") as config:
    data = json.load(config)
    guild_id = data["guild_id"]

guild_object = discord.Object(guild_id)

youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name = "join", description="Joins a voice channel", with_app_command=True)
    @app_commands.guilds(guild_object)
    async def join(self, ctx: commands.Context):
        """Joins a voice channel"""
        if ctx.author.voice:
                await ctx.reply("Joining voice channel")
                await ctx.author.voice.channel.connect()
        else:
                await ctx.reply("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")

    @commands.hybrid_command(name = "play", description="Plays a song from a url", with_app_command=True)
    @app_commands.guilds(guild_object)
    async def play(self, ctx: commands.Context, *, url):
        """Plays a song from a url"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.reply(f'Now playing: {player.title}')

    @commands.hybrid_command(name = "volume", description="Changes the player's volume", with_app_command=True)
    @app_commands.guilds(guild_object)
    async def volume(self, ctx: commands.Context, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @commands.hybrid_command(name = "stop", description="Stops and disconnects the bot from voice", with_app_command=True)
    @app_commands.guilds(guild_object)
    async def stop(self, ctx: commands.Context):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded")

async def setup(bot:commands.Bot):
    await bot.add_cog(Music(bot), guilds=[guild_object])