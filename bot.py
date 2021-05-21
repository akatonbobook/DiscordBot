import json
import os
import traceback
import datetime

import discord
from discord.ext import commands


path = os.path.dirname(__file__)


class DiscordBot(commands.Bot):

    """
    Bot
    """
    def logging(self, *args):
        now = datetime.datetime.now()
        msg = "[" + now.strftime("%Y/%m/%d %H:%M:%S") + "] "
        for ctx in args:
            msg += str(ctx) + " "
        print(msg)

    def __init__(self, command_prefix):
        super().__init__(command_prefix)
        self.path = os.path.dirname(__file__)
        self.start_time = datetime.datetime.now()
        for cog in self.get_extensions():
            try:
                self.load_extension(cog)
                self.logging("load", cog)
            except Exception:
                traceback.print_exc()

    async def on_ready(self):
        self.logging("BOT IS READY")
        await self.change_presence(activity=discord.Game(name="python", type=1))

    async def reload(self):

        """
        extension.jsonのextensionを再読み込みする関数
        :return:
        """

        extensions = dict(self.extensions)
        for cog in extensions:
            self.unload_extension(cog)
        for cog in self.get_extensions():
            try:
                self.load_extension(cog)
                self.logging("reload", cog)
            except Exception:
                traceback.print_exc()

    def get_extensions(self):

        """
        extension.jsonのextensionリストを読み込む関数
        :return: List[str]
        """

        file_path = os.path.join(self.path, "extension.json")
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                d = {"extensions": []}
                json.dump(d, f, indent=2, ensure_ascii=False)

        extensions = []
        with open(file_path) as f:
            j_extensions = json.load(f)
            extensions = j_extensions["extensions"]
        return extensions


if __name__ == "__main__":

    """
        main処理
    """

    
    file = os.path.join(path, "token.txt")
    with open(file) as f:
        token = f.readline()

    bot_client = DiscordBot(command_prefix='$')

    bot_client.remove_command("help")

    @bot_client.command()
    async def log(ctx):
        if ctx.author.bot:
            return
        bot_client.logging("$log")
        date = datetime.datetime.now()
        delta = date - bot_client.start_time
        days, hour = divmod(delta.total_seconds(), 24*60*60)
        hour, minutes = divmod(hour, 60*60)
        minutes, seconds = divmod(minutes, 60)
        msg = "起動してから"
        msg += str(int(days)) + "日" if days > 0 else ""
        msg += str(int(hour)) + "時間" if days > 0 or hour > 0 else ""
        msg += str(int(minutes)) + "分" if days > 0 or hour > 0 or minutes > 0 else ""
        msg += str(int(seconds)) + "秒が経過"
        await ctx.send(msg)

    @bot_client.command()
    async def reload(ctx):
        """extensionを再読み込み
        :param ctx:
        :return:
        """
        if ctx.author.bot:
            return
        await bot_client.reload()
        try:
            await ctx.message.delete()
        except Exception:
            pass

    #   botを起動
    try:
        bot_client.run(token)
    except:
        bot_client.logging("tokenが間違っています")