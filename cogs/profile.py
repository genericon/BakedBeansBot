import discord
from discord.ext import commands

import logging


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def profile(self, ctx):
        author = ctx.message.author

        embed = discord.Embed(
            title='Profile',
            description=author.name,
            colour=Colour.blue()
        )

        """
        results = await self.bot.redis.hmget(f'discord:{author.id:#016x}', 'mal', 'anilist', 'vndb')

        if results[0] is not None:
            embed = embed.add_field(
                name='MAL',
                value=results[0],
                inline=True
            )

        if results[1] is not None:
            embed = embed.add_field(
                name='Anilist',
                value=results[0],
                inline=True
            )

        if results[2] is not None:
            embed = embed.add_field(
                name='VNDB',
                value=results[2],
                inline=True
            )        

        """

        await ctx.send(embed=embed)

    @commands.command()
    async def setMal(self, ctx):
        author = ctx.message.author.id
        # await self.bot.redis.hset(f'discord:{author:#016x}', 'mal', username)
        return

    @commands.command()
    async def setAnilist(self, ctx):
        author = ctx.message.author.id
        # await self.bot.redis.hset(f'discord:{author:#016x}', 'anilist', username)
        return

    @commands.command()
    async def setVndb(self, ctx):
        author = ctx.message.author.id
        # self.bot.redis.hset(f'discord:{author:#016x}', 'vndb', username)
        return

    @commands.command()
    async def profileDataMigration(self, ctx):
        # Loop through every message in #mal-anilist-vndb-etc-share
        # for initial data migration
        # This is going to be 'fun'
        return

def setup(bot):
    bot.add_cog(ProfileCog(bot))
