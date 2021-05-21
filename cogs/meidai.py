import discord
from discord.ext import commands


class PropCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def p(self, ctx, txt :str):
        pm = PropManager(src=txt)
        table = PropManager.test_all(pm, trg="p")
        await ctx.send("命題論理式：" + str(pm.prop))
        await self.show_table(ctx, table)
        
    @commands.command()
    async def nff(self, ctx, txt :str):
        pm = PropManager(src=txt)
        table = PropManager.test_all(pm, trg="nff")
        await ctx.send(txt + " の否定標準形：" + str(pm.nff))
        await self.show_table(ctx, table)

    @commands.command()
    async def cnf(self, ctx, txt :str):
        pm = PropManager(src=txt)
        table = PropManager.test_all(pm, trg="cnf")
        await ctx.send(txt + " の連言標準形：" + str(pm.cnf))
        await self.show_table(ctx, table)
        
    async def show_table(self, ctx, table):
        s = "```\n真理値表\n"
        b = True
        for idx, row in enumerate(table):
            if idx == 0:
                length = [0] * len(row)
            for idx, cell in enumerate(row):
                length[idx] = length[idx] if len(cell) < length[idx] else len(cell)
        for row in table:
            for idx, cell in enumerate(row):
                padding = " " * (length[idx] - len(cell) + 1)
                s += " " + cell + padding + "|"
            else:
                s = s[:-1]
                s += "\n"
            if b:
                s += "-" * sum(length) + "-" * 3 * len(row)
                s = s[:-1] + "\n"
                b = False
        else:
            s += "```"
        await ctx.send(s)


def setup(bot):
    bot.add_cog(PropCog(bot))


class PropFormula:
    pass


class Vari(PropFormula):

    pri = 4

    def __init__(self, name :str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name
    
    def test(self, init :dict):
        return init[self.name]


class Static(PropFormula):

    pri = 4

    def __init__(self, b :bool) -> None:
        self.b = b
    
    def __str__(self) -> str:
        return 'T' if self.b else 'F'

    @classmethod
    def top(cls) -> PropFormula:
        return Static(True)
    
    @classmethod
    def btm(cls) -> PropFormula:
        return Static(True)
    
    def test(self, init :dict):
        return self.b


class Not(PropFormula):

    pri = 3

    def __init__(self, inner :PropFormula) -> None:
        self.inner = inner
    
    def __str__(self) -> str:
        if self.inner.pri < self.pri:
            inner = "(" + str(self.inner) + ")"
        else:
            inner = str(self.inner)
        return "-" + inner

    def test(self, init :dict):
        init.setdefault(str(self), not self.inner.test(init))
        return init[str(self)]


class And(PropFormula):

    pri = 2

    def __init__(self, left :PropFormula, right :PropFormula) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        if self.left.pri <= self.pri:
            left = "(" + str(self.left) + ")"
        else:
            left = str(self.left)
        if self.right.pri < self.pri:
            right = "(" + str(self.right) + ")"
        else:
            right = str(self.right)
        return left + "&" + right
    
    def test(self, init :dict):
        init.setdefault(str(self),self.left.test(init) & self.right.test(init))
        return init[str(self)]


class Or(PropFormula):

    pri = 1

    def __init__(self, left :PropFormula, right :PropFormula) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        if self.left.pri <= self.pri:
            left = "(" + str(self.left) + ")"
        else:
            left = str(self.left)
        if self.right.pri < self.pri:
            right = "(" + str(self.right) + ")"
        else:
            right = str(self.right)
        return left + "|" + right

    def test(self, init :dict):
        init.setdefault(str(self), self.left.test(init) | self.right.test(init))
        return init[str(self)]


class Imp(PropFormula):

    pri = 0

    def __init__(self, left :PropFormula, right :PropFormula) -> None:
        self.left = left
        self.right = right

    def __str__(self) -> str:
        if self.left.pri <= self.pri:
            left = "(" + str(self.left) + ")"
        else:
            left = str(self.left)
        return left + "=>" + str(self.right)

    def test(self, init :dict):
        init.setdefault(str(self), (not self.left.test(init)) | self.right.test(init))
        return init[str(self)]

class PropManager:
    import regex
    f = regex.compile(r'(-)|(=>)|(&)|(\|)|(?<rec>\((?:[^\(\)]+|(?&rec))*\))')
    g = regex.compile(r'\(.*\)')
    h = regex.compile(r'(&)|(\|)|(=>)|(-)')

    def __init__(self, *, vari=dict(), prop=None, src=None) -> None:
        self.vari = vari
        self.prop = prop
        if type(src) == str:
            self.str_to_PF(src)
            self.convert_to_NFF()
            self.convert_to_CNF()

    @classmethod
    def test(cls, init :dict, trg):
        trg.test(init)
    
    @classmethod
    def test_all(cls, pm, trg="p"):
        if trg == "p":
            target = pm.prop
        elif trg == "nff":
            target = pm.nff
        elif trg == "cnf":
            target = pm.cnf
        else:
            raise Exception()

        n = len(pm.vari)
        x = 0
        while (1<<n) > x:
            init = dict()
            for idx, key in enumerate(pm.vari.keys()):
                if x>>(n-idx-1) & 0b1 == 1:
                    init[key] = False
                else:
                    init[key] = True
            target.test(init)

            if x == 0:
                results = [[""]*len(init)]
                for idx, key in enumerate(init.keys()):
                    results[0][idx] = key
            l = list()
            print(init)
            for key in results[0]:
                l.append(str(init[key]))
            results.append(l)
            x += 1
        return results

    def str_to_PF(self, txt):
        l1 = list(filter(lambda s: s != None and s != "", PropManager.f.split(txt)))

        def convert(t):
            if PropManager.g.match(t):  #   括弧
                return self.str_to_PF(t[1:-1])
            elif t == 'T':              #   Top
                return Static.top()
            elif t == 'F':              #   Bottom
                return Static.btm()
            elif PropManager.h.match(t):#   operator
                return t
            else:                       #   variable
                self.vari.setdefault(t, Vari(t))
                return self.vari[t]
        l2 = list(map(convert, l1))

        while len(l2) > 1:
            for i in range(len(l2)):
                if l2[-i-1] == "-":
                    l2[-i-1] = Not(l2[-i])
                    del l2[-i]
                    break
            else:
                break

        while len(l2) > 1:
            for i in range(len(l2)):
                if l2[-i-1] == "&":
                    l2[-i-2] = And(l2[-i-2], l2[-i])
                    del l2[-i-1]
                    del l2[-i]
                    break
            else:
                break
        
        while len(l2) > 1:
            for i in range(len(l2)):
                if l2[-i-1] == "|":
                    l2[-i-2] = Or(l2[-i-2], l2[-i])
                    del l2[-i-1]
                    del l2[-i]
                    break
            else:
                break
        
        while len(l2) > 1:
            for i in range(len(l2)):
                if l2[-i-1] == "=>":
                    l2[-i-2] = Imp(l2[-i-2], l2[-i])
                    del l2[-i-1]
                    del l2[-i]
                    break
            else:
                break
        
        self.prop = l2[0]
        return self.prop

    def convert_to_NFF(self):
        def _pos(A):
            if type(A) == Vari:
                return A
            elif type(A) == Static:
                return A
            elif type(A) == Not:
                return _neg(A.inner)
            elif type(A) == And:
                return And(_pos(A.left), _pos(A.right))
            elif type(A) == Or:
                return Or(_pos(A.left), _pos(A.right))
            elif type(A) == Imp:
                return Or(_neg(A.left), _pos(A.right))

        def _neg(A):
            if type(A) == Vari:
                return Not(A)
            elif type(A) == Static:
                return Static(not A.b)
            elif type(A) == Not:
                return _pos(A.inner)
            elif type(A) == And:
                return Or(_neg(A.left), _neg(A.right))
            elif type(A) == Or:
                return And(_neg(A.left), _neg(A.right))
            elif type(A) == Imp:
                return And(_pos(A.left), _neg(A.right))

        self.nff = _pos(self.prop)
        return self.nff

    @classmethod
    def _and_all(cls, elements) -> PropFormula:
        if len(elements) > 1:
            return And(elements[0], PropManager._and_all(elements[1:]))
        elif len(elements) == 1:
            return elements[0]
        else:
            raise Exception("and_all")

    def convert_to_CNF(self):

        def _develop(left, right):
            l_list = list()
            r_list = list()
            l = left
            r = right
            while True:
                if type(l) == Vari:
                    l_list.append(l)
                    break
                elif type(l) == Static:
                    l_list.append(l)
                    break
                elif type(l) == Not:
                    l_list.append(l)
                    break
                elif type(l) == Or:
                    l_list.append(l)
                    break
                elif type(l) == And:
                    l_list.append(l.left)
                    l = l.right
                    continue
                else:
                    raise Exception()
            while True:
                if type(r) == Vari:
                    r_list.append(r)
                    break
                elif type(r) == Static:
                    r_list.append(r)
                    break
                elif type(r) == Not:
                    r_list.append(r)
                    break
                elif type(r) == Or:
                    r_list.append(r)
                    break
                elif type(r) == And:
                    r_list.append(r.left)
                    r = r.right
                    continue
                else:
                    raise Exception()
            
            li = list()
            
            for i in l_list:
                for j in r_list:
                    li.append(Or(i, j))
            return PropManager._and_all(li)


        def _c(A):
            if type(A) == Vari:
                return A
            elif type(A) == Static:
                return A
            elif type(A) == Not:
                return A
            elif type(A) == And:
                return And(_c(A.left), _c(A.right))
            elif type(A) == Or:
                return _develop(_c(A.left), _c(A.right))

        if not self.nff:
            self.convert_to_NFF()
        self.cnf = _c(self.nff)

    def __str__(self):
        return str(self.prop)