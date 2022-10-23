from cmath import isnan
from discord import Member, Embed
from discord.ext.commands import Cog, command
from random import choice, randint
from aiohttp import request

class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="hello", aliases=["hi"], hidden=True)
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(('Hello', 'Hi', 'Sup', 'Hey'))} {ctx.author.mention}!")

    @command(name="slap", aliases=["hit"])
    async def slap_member(self, ctx, member: Member, *, reason="no reason"):
        # embed = Embed(title="Slap!", description="Slapped a member!", colour=0xFF0000)
        # fields = [("Name", "Value", True),
        #           ("Another field", "This field is next to another one", True),
        #           ("A non-inline field", "This field will appear on it's ows row", False)]
        # for name, value, inline in fields:
        #     embed.add_field(name=name, value=value, inline=inline)
        # embed.set_author(name="dudek0807", icon_url=self.bot.guild.icon)
        # embed.set_footer(text="This is a footer")
        await ctx.send(f"{ctx.author.mention} slapped {member.mention} for {reason}!")

    @command(name="animu")
    async def animu(self, ctx, action: str):
        match action:
            case "hug":
                URL = "https://some-random-api.ml/animu/hug"
            case "facepalm":
                URL = "https://some-random-api.ml/animu/face-palm"
            case "pat":
                URL = "https://some-random-api.ml/animu/pat"
            case "wink":
                URL = "https://some-random-api.ml/animu/wink"
            case _:
                URL = "Nothing to see here"
        print(URL)
        if URL.startswith("Nothing"):
            await ctx.send("Nothing to see here")
            return

        async with request("GET", URL, headers={}) as response:
            if response.status == 200:
                data = await response.json()
                await ctx.send(data["link"])
            else:
                await ctx.send(f"API returned a {response.status} status")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")
            await self.bot.stdout.send("Fun cog ready!")
            print("fun cog ready!!!!")


async def setup(bot):
    await bot.add_cog(Fun(bot))