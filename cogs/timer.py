import asyncio

from discord.ext import commands


class TimerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def timer(self, ctx, seconds: float, name: str=""):
        if ctx.author.bot:
            return
        
        name = ' [' + name + '] ' if name != "" else " "

        if seconds <= 0:
            await ctx.send(ctx.author.mention + name + "タイマーをセットできません")
            return
        await ctx.send(ctx.author.mention + name + str(seconds) + "秒のタイマーをセットしました")
        await asyncio.sleep(seconds)
        await ctx.send(ctx.author.mention + name + str(seconds) + "秒経ちましたよ～")

    @commands.command(name="蒙古タンメン")
    async def moukotanmen(self, ctx):
        if ctx.author.bot:
            return
        await ctx.send(ctx.author.mention + " かしこまりました！ 蒙古タンメンですね")
        await asyncio.sleep(300)
        await ctx.send(ctx.author.mention + " 蒙古タンメンができたよ～")

    @commands.command(name="カップヌードル")
    async def cupnoodle(self, ctx):
        if ctx.author.bot:
            return
        await ctx.send(ctx.author.mention + " かしこまりました！ カップヌードルですね")
        await asyncio.sleep(180)
        await ctx.send(ctx.author.mention + " カップヌードルができたよ～")

    @commands.command(name="ペヤング")
    async def peyangu(self, ctx):
        if ctx.author.bot:
            return
        await ctx.send(ctx.author.mention + " かしこまりました！ ペヤングですね")
        await asyncio.sleep(180)
        await ctx.send(ctx.author.mention + " ペヤングができたよ～")

    @commands.command(name="赤いきつね")
    async def peyangu(self, ctx):
        if ctx.author.bot:
            return
        await ctx.send(ctx.author.mention + " かしこまりました！ 赤いきつねですね")
        await asyncio.sleep(300)
        await ctx.send(ctx.author.mention + " 赤いきつねができたよ～")

    @commands.command(name="緑のたぬき")
    async def peyangu(self, ctx):
        if ctx.author.bot:
            return
        await ctx.send(ctx.author.mention + " かしこまりました！ 緑のたぬきですね")
        await asyncio.sleep(180)
        await ctx.send(ctx.author.mention + " 緑のたぬきができたよ～")


def setup(bot):
    bot.add_cog(TimerCog(bot))