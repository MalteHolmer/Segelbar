import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import random
from comments import comments

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="#")

class Nebelhorn(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.honk_loop_task = None
        self.min_minutes = 5
        self.max_minutes = 25
        self.last_channel = None

    async def honk_at_random_loop(self):
        min_seconds = self.min_minutes*60
        max_seconds = self.max_minutes*60
        while True:
            sleep_time = random.randint(min_seconds, max_seconds)
            await asyncio.sleep(sleep_time)
            await self.play_honk()

    async def play_honk(self):
        await self.honk_comment()
        audio = discord.FFmpegPCMAudio("./Nebelhorn.mp3")
        if bot.voice_clients:
            bot.voice_clients[0].play(audio)

    async def start_honk(self):
        if self.honk_loop_task and not self.honk_loop_task.cancelled():
            self.honk_loop_task.cancel()
        self.honk_loop_task = asyncio.create_task(self.honk_at_random_loop())

    async def stop_honk(self):
        if self.honk_loop_task and not self.honk_loop_task.cancelled():
            self.honk_loop_task.cancel()

    @commands.command(brief="Setzt das Intervall in dem wir wohl trinken müssen.")
    async def set_timer(self, ctx: commands.context.Context, min_minutes, max_minutes):
        try:
            min_minutes = float(min_minutes)
            max_minutes = float(max_minutes)
        except ValueError:
            await ctx.channel.send("Intervall ergibt keinen Sinn, willst du gar nicht trinken?")
            return
        if min_minutes >= max_minutes or min_minutes < 0 or max_minutes < 0:
            await ctx.channel.send("Intervall ergibt keinen Sinn, willst du gar nicht trinken?")
            return
        self.min_minutes = min_minutes
        self.max_minutes = max_minutes
        await ctx.channel.send("Intervall erfolgreich gesetzt, das wird böse!")

        if self.honk_loop_task and not self.honk_loop_task.cancelled():
            await self.start_honk()

    @commands.command(brief="Guck woran du mit der Segelbar heut bist.")
    async def whatsup(self, ctx):
        await ctx.channel.send("Intervall ist momentan: {}-{} Minuten.".format(self.min_minutes, self.max_minutes))
        await ctx.channel.send("Der Honker ist momentan {}."
                               .format("aktiviert" if (self.honk_loop_task and not self.honk_loop_task.cancelled())
                                       else "aus"))

    @commands.command(brief="Lässt den Spaß beginnen ;)")
    async def start_honker(self, ctx: commands.context.Context):
        self.last_channel = ctx.channel
        if not bot.voice_clients:
            await ctx.channel.send("Die Segelbar kann nur honken, wenn sie in einem Voice-Channel ist.")
            return
        await ctx.channel.send("Honk-Timer wurde gestartet. Bald müssen wir trinken ;)")
        await self.start_honk()

    @commands.command(brief="Hält die Segelbar davon ab uns noch mehr trinken zu lassen.")
    async def stop_honker(self, ctx: commands.context.Context):
        await self.stop_honk()
        await ctx.channel.send("Honk-Timer gestoppt, aber wieso?????")

    async def honk_comment(self):
        await self.last_channel.send(random.choice(comments))

    @commands.command(brief="Lässt die Segelbar ihr Nebelhorn spielen.")
    async def honk(self, ctx: commands.context.Context):
        if not bot.voice_clients:
            await ctx.channel.send("Die Segelbar kann nur honken, wenn sie in einem Voice-Channel ist.")
            return

        self.last_channel = ctx.channel
        await self.play_honk()

        #await ctx.channel.send("Honk-Timer wurde zurückgesetzt.")
        if self.honk_loop_task and not self.honk_loop_task.cancelled():
            await self.start_honk(ctx)

    @commands.command(brief="Lässt die Segelbar zu uns kommen :)")
    async def join(self, ctx: commands.context.Context):
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()

    @commands.command(brief="Weg mit dir Segelbar :O")
    async def leave(self, ctx: commands.context.Context):
        await self.stop_honker(ctx)
        if bot.voice_clients:
            await bot.voice_clients[0].disconnect()


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


bot.add_cog(Nebelhorn(bot))
bot.run(TOKEN)