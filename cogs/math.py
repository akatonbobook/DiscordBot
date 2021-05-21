from discord.ext import commands


def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()


def prime_factorize(n):
    a = []
    while n % 2 == 0:
        a.append(2)
        n //= 2
    o = 3
    while o * o <= n:
        if n % o == 0:
            a.append(o)
            n //= o
        else:
            o += 2
    if n != 1:
        a.append(n)
    return a


class MathCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pf(self, ctx, num):
        if ctx.author.bot:
            return
        if not is_integer(num):
            return
        n = int(num)
        if n == 0 or n == 1:
            await ctx.send(num + " = " + num)
            return
        a = prime_factorize(n)
        msg = str(n) + " = "
        for i in a:
            msg += str(i) + " x "
        else:
            msg = msg[:-3]
        await ctx.send(msg)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not is_integer(message.content):
            return
        n = int(message.content)
        ch = message.channel
        msg = ""
        if n == 0 or n == 1:
            await ch.send("その数字，素因数分解すると " + message.content + " だね")
            return
        elif n == 334:
            await ch.send("なんでや阪神関係ないやろ")
            msg += "ちなみに"
        a = prime_factorize(n)
        msg += "その数字，素因数分解すると "
        for i in a:
            msg += str(i) + " x "
        else:
            msg = msg[:-3]
            msg += " だね"
        await ch.send(msg)


def setup(bot):
    bot.add_cog(MathCog(bot))