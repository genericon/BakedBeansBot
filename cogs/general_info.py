import discord
from discord import Colour
from discord.ext import commands


class GeneralInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['about'])
    async def info(self, ctx):
        """
        Shows info about the bot
        """

        embed = discord.Embed(
            title='About BakedBeansBot',
            description=self.bot.description,
            colour=Colour.blue()
        ).add_field(
            name='Contributing',
            value='Check out the source on GitHub: https://github.com/genericon/BakedBeansBot',
            inline=False
        ).add_field(
            name='License',
            value='BakedBeansBot is released under the MIT License',
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def ping(self, ctx):
        """
        Check latency
        """

        await ctx.send(f'**Pong!** Current ping is {self.bot.latency*1000:.1f} ms')


def setup(bot):
    bot.add_cog(GeneralInfo(bot))
