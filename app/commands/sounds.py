import random
import asyncio
import discord
import pymongo
import youtube_dl
import settings
from config import logger
from discord.ext import commands

OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll',
             'libopus.so.0', 'libopus.0.dylib', 'opus']

for opus_lib in OPUS_LIBS:
    try:
        discord.opus.load_opus(opus_lib)
    except OSError:
        pass

logger.info(f"Opus Library Loaded: {discord.opus.is_loaded()}")


class VoiceConnection:
    def __init__(self, bot):
        self.bot = bot
        self.voice = None
        self.current = None
        self.play_next_sound = asyncio.Event()
        self.sounds = asyncio.Queue()
        self.player = self.bot.loop.create_task(self.play_sound())
    
    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_sound.set)

    async def play_sound(self):
        while True:
            self.play_next_sound.clear()
            self.current = await self.sounds.get()
            self.current.start()
            await self.play_next_sound.wait()


class Sounds:
    """ Sound related commands for Evil Rick """
    rate = 1
    per = 6.0

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}
        self.is_playing = False
        self.greetings = ['https://www.youtube.com/watch?v=evtmNulZAj0',
                          'https://www.youtube.com/watch?v=9SL35HaJ2Ys',
                          'https://www.youtube.com/watch?v=XuI5sV_-kx0',
                          'https://youtu.be/B7lgrFKI_L8']

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceConnection(self.bot)
            self.voice_states[server.id] = state
        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    async def on_voice_state_update(self, before, after):
        """ Greets a user who joins the voice channel"""
        user_joined_bots_channel = False
        tim = '142914172089401344'
        members_before = before.voice_channel.voice_members
        members_after = after.voice_channel.voice_members

        users_before = [member.name for member in members_before]
        users_after = [member.name for member in members_after]

        for voice in self.bot.voice_clients:
            if after.voice_channel == voice.channel:
                user_joined_bots_channel = True

        if len(users_before) < len(users_after) and user_joined_bots_channel:
            state = self.get_voice_state(after.server)
            try:
                if after.id == tim:
                    player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=EDrMco4g8ng',
                                                                  use_avconv=True)
                else:
                    player = await state.voice.create_ytdl_player(random.choice(self.greetings),
                                                                  use_avconv=True)
                player.start()
            except discord.ClientException:
                logger.error("On_Voice_State Greeting Failed")

    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def join(self, ctx, *, channel : discord.Channel):
        """Specify a channel for the bot to join """
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            await self.bot.say('Already in a voice channel...')
        except discord.InvalidArgument:
            await self.bot.say('This is not a voice channel...')

    @commands.command(pass_context=True, no_pm=True)
    @commands.has_permissions(ban_members=True)
    async def summon(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('You are not in a voice channel.')

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def stfu(self, ctx):
        """SHUT THE FUCK UP!"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=wQYob6dpTTk', 
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def pump(self, ctx):
        """I'm here to pump you up"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://youtu.be/BgWd1dcODHU?t=10',
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def listen(self, ctx):
        """Listen here you beautiful bitch...."""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=Jsi5VTzJpPw', 
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def plums(self, ctx):
        """...a nice bluish hue"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=7cIAcXpUuS0',
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')
        
    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def hadtosay(self, ctx):
        """Shiiiiit, Negro! That's all you had to say"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=hRb7-3kebUQ',
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def omg(self, ctx):
        """Oh my god, who the hell cares?"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=RFZrzg62Zj0',
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def damn(self, ctx):
        """DAAAAAMMMMMMMMMNNNNN!"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=w1EHH0_CqqU',
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def dominate(self, ctx):
        """Dominating"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=tq65HEqNq-8',
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def wub(self, ctx):
        """Wubba Lubba Dub Dub"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=PAhoNoQ91_c',
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def pickle(self, ctx):
        """I'm Pickle Rick!"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=Ij7ayjBaNhc',
                                                          after=toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def gold(self, ctx):
        """I Love Gold"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=DOFAnpb8I3E',
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def bitch(self, ctx):
        """Like A Bitch"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player('https://www.youtube.com/watch?v=koCAtBJA5XU',
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def leeroy(self, ctx):
        """....jenkins!"""
        state = self.get_voice_state(ctx.mesage.server)
        try:
            player = await state.voice.create_ytdl_player("https://www.youtube.com/watch?v=yOMj7WttkOA",
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def ree(self, ctx):
        """REEEEEEEEE!"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player("https://www.youtube.com/watch?v=cLBq9vrWGuE",
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def horny(self, ctx):
        """DO I MAKE YOU RANDY!?!"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player("https://www.youtube.com/watch?v=gXlIymq7ofE",
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

    @commands.command(pass_context=True)
    @commands.has_permissions(create_instant_invite=True)
    @commands.cooldown(rate, per, type=commands.BucketType.server)
    async def triple(self, ctx):
        """Oh baby a triple, oh yeah!"""
        state = self.get_voice_state(ctx.message.server)
        try:
            player = await state.voice.create_ytdl_player("https://www.youtube.com/watch?v=13VFfsJTLdc",
                                                          after=state.toggle_next, use_avconv=True)
            await state.sounds.put(player)
        except discord.ClientException:
            self.bot.say('An error occured while streaming audio...')

def setup(bot):
    bot.add_cog(Sounds(bot))
