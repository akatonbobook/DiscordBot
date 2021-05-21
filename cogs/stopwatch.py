import datetime

from discord.ext import commands


class StopWatchCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guilds = {}

    @commands.group()
    async def sw(self, ctx):
        pass

    @sw.command()
    async def start(self, ctx):
        if ctx.author.bot:
            return
        startDateTime = datetime.datetime.now()
        if ctx.guild in self.guilds:
            users = self.guilds[ctx.guild]
            self.guilds[ctx.guild][ctx.author] = startDateTime
        else:
            self.guilds[ctx.guild] = {ctx.author: startDateTime}
        
        await ctx.channel.send(ctx.author.mention + " [StopWatch] スタート")
    
    @sw.command()
    async def stop(self, ctx):
        if ctx.author.bot:
            return
        endDateTime = datetime.datetime.now()
        if ctx.guild in self.guilds:
            if ctx.author in self.guilds[ctx.guild]:
                timedelta = endDateTime - self.guilds[ctx.guild][ctx.author]
                await ctx.channel.send(ctx.author.mention + " [StopWatch] 結果 " + str(timedelta)[:10])
                self.guilds[ctx.guild].pop(ctx.author)
                return

        await ctx.channel.send(ctx.author.mention + " [StopWatch] タイマーが動いていません")



def setup(bot):
    bot.add_cog(StopWatchCog(bot))