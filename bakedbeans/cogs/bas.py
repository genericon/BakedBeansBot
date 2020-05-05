import discord
from discord import Colour
from discord.ext import commands

BetterAntispam_UID = 501982335076532224
ExplosionImgUrl = "https://media1.tenor.com/images/11bf9c144c0ad3c418721c99a35961ca/tenor.gif"

class BetterAntispamCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.author.id == BetterAntispam_UID and
            "Nuked this channel" in message.content):
            self.bot.dispatch('bas_nuke', message)

    @commands.Cog.listener()
    async def on_bas_nuke(self, message):
        # only allow in RSFA as of now
        if message.guild.id == self.bot.config['server']:
            ctx = await self.bot.get_context(message)
            ctx.command = self.bot.get_command('explosion')
            await self.bot.invoke(ctx)

    @commands.command(hidden=True)
    async def explosion(self, ctx):
        embed = discord.Embed(
            title="Explosion!",
            colour=Colour.blue()
        )

        embed.set_image(url=ExplosionImgUrl)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(BetterAntispamCog(bot))
