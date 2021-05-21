import glob
import os
import random

from discord.ext import commands


class QuizCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.active = {}
        self.count = {}
        self.q_data = []
        self.a_data = []

    @commands.command()
    async def quiz(self, ctx):

        # 送信者がぼっとなら終了
        if ctx.author.bot:
            return

        guild = ctx.guild
        self.active.setdefault(guild, False)

        # 問題出題中なら終了，そうでなければ出題中に変更
        if self.active[guild]:
            await ctx.send("すでに問題を出題中です")
            return
        else:
            self.active[guild] = True
        self.q_data = []
        self.a_data = []

        # ファイルを確認し，存在しない場合は終了
        filepath = os.path.join(self.bot.path, "quiz", "*.txt")
        files = glob.glob(filepath)
        c = 0
        for filepath in files:
            # ファイルからデータ取得
            with open(filepath, encoding="utf_8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == "\n":
                        continue
                    if c % 2 == 0:
                        self.q_data.append(line)
                    else:
                        self.a_data.append(line)
                    c = c+1

        # ランダムに問題を選択
        r = random.randrange(c/2)
        question, answer = self.q_data[r], self.a_data[r].split(" ")

        # 表示
        await ctx.send("[問題] " + question)
        self.count.setdefault(guild, 0)

        # 解答チェック関数
        def check(m):
            if m.author.bot:
                return False
            if m.channel == ctx.channel:
                return m.content in answer
            else:
                return False

        try:
            message = await self.bot.wait_for("message", timeout=30, check=check)
            await ctx.send(message.author.mention + " 正解です！")
            self.count[guild] = self.count[guild] + 1

            # 問題出題中をFalseに
            self.active[guild] = False
        except:
            await ctx.send("正解は " + answer[0] + " でした")
            await ctx.send(str(self.count[guild]) + " 問連続正解でした")
            self.count[guild] = 0

            # 問題出題中をFalseに
            self.active[guild] = False
            return

        await self.quiz(ctx)


def setup(bot):
    bot.add_cog(QuizCog(bot))
