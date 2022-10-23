import os, asyncio
from discord import Embed, Intents, File
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, BadArgument, MissingRequiredArgument
from discord.errors import HTTPException, Forbidden
from datetime import datetime
from ..db import db
from glob import glob
import tzlocal

PREFIX = "!"
OWNER_IDS = [612072933770264584]
COGS = [path.split("\\")[-1][:-3] for path in glob("./library/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog is ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])

class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))

        db.autosave(self.scheduler)
        super().__init__(command_prefix=PREFIX, owner_ids=OWNER_IDS, intents=Intents.all())

    async def load_extentions(self):
        for cog in COGS:
            await self.load_extension(f"library.cogs.{cog}")
            print(f" {cog} cog loaded")

        print("setup complete")

    async def run(self, version):
        self.VERSION = version

        print("running setup...")
        await self.load_extentions()

        with open("./library/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        await super().start(self.TOKEN, reconnect=True)

    async def rules_reminder(self):
        await self.stdout.send("Remember to follow the rules!")

    async def on_connect(self):
        print("bot connected")

    async def on_disconnect(self):
        print("bot disconnected")
    
    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong")
        
        await self.stdout.send("An error occured")
        
        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass
        elif isinstance(exc, CommandNotFound):
            await ctx.send("Wrong command")

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more arguments are missing!")

        elif hasattr(exc,"original"):
            if isinstance(exc.original, HTTPException):
                await ctx.send("Unable to send message.")
            
            elif isinstance(exc.original, Forbidden):
                await ctx.send("I do not have permissions to do that.")

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(1031241326479552593)
            self.stdout = self.get_channel(1031486798574129202)
            self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            self.scheduler.start()

            #channel = self.get_channel(1031486798574129202)

            # embed = Embed(title="Now online", description="Bot is online", colour=0xFF0000, timestamp=datetime.now())
            # fields = [("Name", "Value", True),
            #           ("Another field", "This field is next to another one", True),
            #           ("A non-inline field", "This field will appear on it's ows row", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            # embed.set_author(name="dudek0807", icon_url=self.guild.icon)
            # embed.set_footer(text="This is a footer")
            # embed.set_thumbnail(url="https://i.pinimg.com/736x/96/14/41/961441ac981ada78f04b0ec5e1503e21.jpg")
            # #embed.set_image(url=self.guild.icon)
            # await channel.send(embed=embed)

            # await channel.send(file=File("./data/images/test.jpg"))

            while not self.cogs_ready.all_ready():
                await asyncio.sleep(0.5)

            await self.stdout.send("Now online!")
            self.ready = True
            print("bot ready")
        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

bot = Bot()