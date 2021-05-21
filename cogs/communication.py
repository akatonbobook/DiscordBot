import json
import os
import random
import re

from discord.ext import commands


class CommunicationCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.file_path = os.path.join(self.bot.path, "communication.json")
        self.dictionary = {}
        self.load_json()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not str(message.author.id) in self.dictionary.keys():
            return
        user_dictionary = self.dictionary[str(message.author.id)]

        if not message.content in user_dictionary.keys():
            return
        rep = user_dictionary[message.content]
        n = len(rep)
        r = random.randrange(n)
        await message.channel.send(user_dictionary[message.content][r])

    @commands.command()
    async def list(self, ctx):
        if ctx.author.bot:
            return
        if not str(ctx.author.id) in self.dictionary.keys():
            await ctx.send("登録しているkeyはありません")
            return
        if len(self.dictionary[str(ctx.author.id)].keys()) == 0:
            await ctx.send("登録しているkeyはありません")
            return
        msg = ctx.author.mention + " 登録しているkeyは\n"
        for key in self.dictionary[str(ctx.author.id)].keys():
            msg += key + ", "
        msg = msg[:-2] + "\nです"
        await ctx.send(msg)

    @commands.command()
    async def remove(self, ctx, key):
        if ctx.author.bot:
            return
        if not str(ctx.author.id) in self.dictionary.keys():
            await ctx.send("keyが見つかりませんでした")
            return
        if not key in self.dictionary[str(ctx.author.id)].keys():
            await ctx.send("keyが見つかりませんでした")
            return
        self.dictionary[str(ctx.author.id)].pop(key)
        self.save_json()
        await ctx.send("keyを削除しました")

    @commands.command()
    async def add(self, ctx, key, *values):
        if ctx.author.bot:
            return
        p = re.compile("[0-9]+")
        if p.match(key[0]):
            await ctx.send("数字から始まるkeyは登録できません")
            return
        if key[0] == self.bot.command_prefix:
            await ctx.send(self.bot.command_prefix + " から始まるkeyは登録できません")
            return
        self.dictionary.setdefault(str(ctx.author.id), {})
        self.dictionary[str(ctx.author.id)][key] = values
        self.save_json()
        await ctx.send("登録しました")

    def load_json(self):
        self.dictionary = {}
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding="utf8") as f:
                json.dump({}, f, indent=2, ensure_ascii=False)
        with open(self.file_path, encoding="utf8") as f:
            j_extensions = json.load(f)
            for id in j_extensions.keys():
                self.dictionary[id] = j_extensions[id]

    def save_json(self):
        with open(self.file_path, 'w', encoding="utf8") as f:
            json.dump(self.dictionary, f, indent=2, ensure_ascii=False)


def setup(bot):
    bot.add_cog(CommunicationCog(bot))