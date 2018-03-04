import random
import shutil
import asyncio
from operator import itemgetter

import discord
import youtube_dl
from discord.ext import commands

from config import logger
from models import SoundDatabase
from utils.paginator import Pages


ytdl_format_options = {
    "format": "bestaudio/best", "extractaudio": True, "audioformat": "mp3",
    "noplaylist": True, "nocheckcertificate": True, "ignoreerrors": False,
    "logtostderr": False, "quiet": True, "no_warnings": True,
    "default_search": "auto", "source_address": "0.0.0.0",
    "preferredcodec": "libmp3lame"
}


def get_ytdl(id):
    format = ytdl_format_options
    format['outtmpl'] = "commands/sounds/{}/%(id)s.mp3".format(id)
    return youtube_dl.YoutubeDL(format)


class OpusLoader:
    def __init__(self):
        self.opus_libs = ['libopus-0.x86.dll', 'libopus-0.x64.dll',
                          'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib',
                          'opus']
        self.load_opus()
        logger.info(f"Opus Library Loaded: {discord.opus.is_loaded()}")

    def load_opus(self):
        for opus_lib in self.opus_libs:
            try:
                discord.opus.load_opus(opus_lib)
            except OSError:
                pass


class VoiceConnection:
    """
    Represents a discord voice client
    """
    def __init__(self, bot, guild):
        self.bot = bot
        self.voice = None
        self.guild = guild
        self.bot.loop.create_task(self.clear_data())

    async def clear_data(self, id=None):
        await self.bot.wait_until_ready()
        counter = 0
        while not self.bot.is_closed():
            try:
                if id is None:
                    shutil.rmtree('commands/sounds')
                else:
                    shutil.rmtree(f"commands/sounds/{id}")
                counter += 1
                logger.info(f"CLEARED YOUTUBE DATA: {counter}")
            except FileNotFoundError:
                logger.info(f"No Youtube Data Detected")
            await asyncio.sleep(60*60)  # 1 Hour


class Sounds:
    """
    Sound Command Cog
    """
    # Cooldown parameters
    rate = 1
    per = 4.0

    def __init__(self, bot):
        OpusLoader()
        self.bot = bot
        self.voice_states = {}
        self.greetings = ['https://www.youtube.com/watch?v=evtmNulZAj0',
                          'https://www.youtube.com/watch?v=9SL35HaJ2Ys',
                          'https://youtu.be/B7lgrFKI_L8']

    @staticmethod
    def download_video(id, url):
        ytdl = get_ytdl(id)
        data = ytdl.extract_info(url, download=True)

        if "entries" in data:
            data = data['entries'][0]

        _id = data['id']

        path = f"commands/sounds/{id}"
        fp = f"{path}/{_id}.mp3"
        audio = discord.FFmpegPCMAudio(fp, executable="avconv")

        return audio

    def get_voice_state(self, guild):
        state = self.voice_states.get(guild.id)
        if state is None:
            state = VoiceConnection(self.bot, guild)
            self.voice_states[guild.id] = state
        return state

    async def create_voice_client(self, channel):
        voice = await channel.connect(reconnect=True)
        state = self.get_voice_state(channel.guild)
        state.voice = voice

    async def on_voice_state_update(self, member, before, after):
        """
        Automatically greets a user who joins the voice channel
        """
        timmy = {
            142914172089401344: 'https://www.youtube.com/watch?v=EDrMco4g8ng'
            }
        state = self.get_voice_state(member.guild)
        try:
            if state.voice.channel == member.voice.channel:
                if before.channel != state.voice.channel:
                    if member.id in timmy:
                        audio = self.download_video(member.guild.id, timmy[member.id])
                        state.voice.play(audio)
                    else:
                        url = random.choice(self.greetings)
                        audio = self.download_video(member.guild.id, url)
                        state.voice.play(audio)
        except AttributeError:
            logger.info("Skipping Initial Voice Check")

    def play_sound(self, ctx, url):
        state = self.get_voice_state(ctx.guild)
        audio = self.download_video(ctx.guild.id, url)
        state.voice.play(audio)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def join(self, ctx, *, channel: commands.VoiceChannelConverter):
        """
        Specify a channel for the bot to join
        """
        await self.create_voice_client(channel)

    @commands.command(no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def summon(self, ctx):
        """
        Summons the bot to your voice channel
        """
        channel = ctx.author.voice.channel
        if channel is None:
            await ctx.send('You are not in a voice channel.')

        state = self.get_voice_state(ctx.guild)
        if state.voice is None:
            state.voice = await channel.connect(reconnect=True)
        else:
            await state.voice.move_to(channel)

    @commands.group(invoke_without_command=True)
    async def s(self, ctx, *, name):
        """
        Plays a specific sound clip
        """
        guild = ctx.guild.id
        with SoundDatabase(str(guild) + "/sounds") as db:
            sound = db.find_sound(name)
            self.play_sound(ctx, sound["url"])
            db.used(sound)

    @s.command()
    @commands.has_permissions(create_instant_invite=True)
    async def create(self, ctx, name, *, url):
        """
        Creates a sound clip for the server
        """
        guild = ctx.guild.id
        with SoundDatabase(str(guild) + "/sounds") as db:
            sound = {
                "name": name,
                "url": str(url),
                "creator": ctx.author.display_name,
                "times_used": 0
            }
            db.create_sound(sound)
            msg = f"`?s {name}` has been created by {sound['creator']}"
            await ctx.message.delete()
            await ctx.send(msg)

    @s.command()
    @commands.has_permissions(ban_members=True)
    async def delete(self, ctx, *, name):
        """
        Delete a specific sound clip
        """
        guild = ctx.guild.id
        with SoundDatabase(str(guild) + "/sounds") as db:
            db.delete_sound(name)
            msg = f"`?s {name}` has been removed"
            await ctx.send(msg)

    @s.command(name="all")
    async def _all(self, ctx):
        """
        List all server tags
        """
        guild = ctx.guild.id
        with SoundDatabase(str(guild) + "/sounds") as db:
            sounds = db.get_all_sounds()
            sounds = sorted([sound["name"] for sound in sounds])

            p = Pages(ctx, entries=sounds, per_page=20)
            await ctx.send("**All Server Sound Commands**")
            await p.paginate()

    @s.command()
    async def top(self, ctx):
        """
        List top most played sounds
        """
        guild = ctx.guild.id
        with SoundDatabase(str(guild) + "/sounds") as db:
            sounds = db.get_all_sounds()
            sounds = sorted(sounds, key=itemgetter("times_used"), reverse=True)
            p = Pages(ctx, per_page=20,
                      entries=[f"{sound['name']}\t-\t**{sound['times_used']}**"
                               for sound in sounds])

            await ctx.send("**Top Played Sounds**")
            await p.paginate()


def setup(bot):
    bot.add_cog(Sounds(bot))
