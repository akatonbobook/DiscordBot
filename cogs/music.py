import glob
import json
import os

import discord
from discord.ext import commands

from audio import virtualaudio
from cogs import voice


class PlayMusic(voice.VoiceCore):

    def __init__(self, bot):
        super().__init__(bot)

    async def playmusic(self, s, voice_channel, text_channel, volume=0.5):
        """
            入室と音源の再生

            ボイスチャンネルが無効ならメッセージを表示して終了
        """
        if voice_channel == None:
            if not text_channel == None:
                await text_channel.send("ボイスチャンネルから呼んでね")
            return
        audiosource = discord.FFmpegPCMAudio(source=s)
        await self.play_source(voice_channel, audiosource, enter=True, volume=volume)

    async def play_virtual(self, voice_channel, text_channel, volume=0.5):
        if voice_channel == None:
            if not text_channel == None:
                await text_channel.send("ボイスチャンネルから呼んでね")
            return
        audiosource = virtualaudio.VirtualSource()
        await self.play_source(voice_channel, audiosource, enter=True, volume=volume)


def load_json(file_path, make=True):

    if not os.path.exists(file_path):
        save_json(file_path, {})
    j = {}
    with open(file_path, encoding="utf8") as f:
        j = json.load(f)
    return j


def save_json(file_path, dictionary):

    with open(file_path, 'w', encoding="utf8") as f:
        json.dump(dictionary, f, indent=2, ensure_ascii=False)


class MusicCog(PlayMusic):

    def __init__(self, bot):
        super().__init__(bot)
        self.thememusic = {}
        self.musics = {}
        self.musicfiles = []

    @commands.command()
    async def virtualaudio(self, ctx):
        if ctx.author.id != 490866292585136128:
            await ctx.send("このコマンドを実行する権限がありません")
            return
        
        if ctx.author.voice == None:
            return

        voice_channel = ctx.author.voice.channel
        await self.play_virtual(voice_channel, None, volume=0.5)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return
        if after.channel == None:
            if len(before.channel.members) == 1 and before.channel.members[0].bot:
                await self.leave_voice_channel(before.channel)
            return
        if before.channel == after.channel:
            return
        if before.channel != None:
            if before.channel.guild == after.channel.guild:
                return
        self.thememusic = load_json(os.path.join(self.bot.path, "theme.json"))
        self.thememusic.setdefault(str(after.channel.guild.id), False)
        save_json(os.path.join(self.bot.path, "theme.json"), self.thememusic)
        if not self.thememusic[str(after.channel.guild.id)]:
            return
        self.musics = load_json(os.path.join(self.bot.path, "musics.json"))
        self.musics.setdefault(str(member.id), "bittersweetsamba.mp3")
        save_json(os.path.join(self.bot.path, "musics.json"), self.musics)
        await self.playmusic("music\\"+self.musics[str(member.id)], after.channel, None, volume=0.6)

    @commands.group()
    async def theme(self, ctx):
        if ctx.author.bot:
            return
        if ctx.invoked_subcommand != None:
            return
        
        user_voice = ctx.author.voice
        self.musicfiles = glob.glob(os.path.join(self.bot.path, "music", "*.mp3"))

        voice_channel = None
        if user_voice != None:
            voice_channel = user_voice.channel

        self.musics = load_json(os.path.join(self.bot.path, "musics.json"))
        self.musics.setdefault(str(ctx.author.id), "bittersweetsamba.mp3")
        save_json(os.path.join(self.bot.path, "musics.json"), self.musics)

        await self.playmusic("music\\"+self.musics[str(ctx.author.id)], voice_channel, ctx.channel, volume=0.6)

    @theme.command()
    async def list(self, ctx):
        if ctx.author.bot:
            return
        self.musicfiles = glob.glob(os.path.join(self.bot.path, "music", "*.mp3"))
        message = ""
        for idx, music in enumerate(self.musicfiles):
            message += str(idx) + " : " + music.split("\\")[-1][:-4] + "\n"
        await ctx.send(message)

    @theme.command()
    async def set(self, ctx, filenum):
        if ctx.author.bot:
            return
        if not filenum.isdecimal():
            await ctx.send("引数には数字を指定してね")
            return
        else:
            num = int(filenum)
            self.musicfiles = glob.glob(os.path.join(self.bot.path, "music", "*.mp3"))
            if num >= len(self.musicfiles):
                await ctx.send("引数が大きすぎです")
                return
        self.musics = load_json(os.path.join(self.bot.path, "musics.json"))
        self.musics[str(ctx.author.id)] = self.musicfiles[num].split("\\")[-1]
        save_json(os.path.join(self.bot.path, "musics.json"), self.musics)
        await ctx.send("テーマ曲を "+self.musics[str(ctx.author.id)]+" に変更しました")
    
    @theme.command()
    async def now(self, ctx):
        if ctx.author.bot:
            return
        self.musics = load_json(os.path.join(self.bot.path, "musics.json"))
        self.musics.setdefault(str(ctx.author.id), "bittersweetsamba.mp3")
        save_json(os.path.join(self.bot.path, "musics.json"), self.musics)
        await ctx.send("現在の "+ ctx.author.name +" のテーマ曲は "+self.musics[str(ctx.author.id)]+" です")

    @theme.command()
    async def true(self, ctx):
        if ctx.author.bot:
            return
        self.bittersweetsamba = load_json(os.path.join(self.bot.path, "theme.json"))
        self.bittersweetsamba[str(ctx.channel.guild.id)] = True
        save_json(os.path.join(self.bot.path, "theme.json"), self.bittersweetsamba)
        await ctx.send("thememusic: true")

    @theme.command()
    async def false(self, ctx):
        if ctx.author.bot:
            return
        self.bittersweetsamba = load_json(os.path.join(self.bot.path, "theme.json"))
        self.bittersweetsamba[str(ctx.channel.guild.id)] = False
        save_json(os.path.join(self.bot.path, "theme.json"), self.bittersweetsamba)
        await ctx.send("thememusic: false")


def setup(bot):
    bot.add_cog(MusicCog(bot))
