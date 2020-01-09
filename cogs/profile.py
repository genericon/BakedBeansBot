import discord
from discord.ext import commands
from discord.utils import escape_markdown

from urllib.parse import quote as url_quote

import logging


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.services = ['MyAnimeList', 'AniList', 'VNDB']

    @commands.command()
    async def profile(self, ctx, user: typing.Optional[discord.User]):
        if user is None:
            user = ctx.message.author

        embed = discord.Embed(
            title='Profile',
            description=author.name,
            colour=Colour.blue()
        )

        results = []
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                results = await conn.fetch('''
                    SELECT service, username
                    FROM profile_data
                    WHERE uid = $i
                    ORDER BY service DESC
                ''', user.id)

        for rec in results:
            if rec['service'] is 'MyAnimeList':
                link = f"https://myanimelist.net/profile/{url_quote(rec['username'])}"
            elif rec['service'] is 'AniList':
                text = f"https://anilist.co/user/{url_quote(rec['username'])}/"
            elif rec['service'] is 'VNDB':
                text = f"https://vndb.org/{url_quote(rec['username'])}"

            value = f"[{escape_markdown(rec['username'])}]({link})"

            embed = embed.add_field(
                name=rec.service,
                value=value,
                inline=True
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def setProfileEntry(self, ctx, user: typing.Optional[discord.User], service: str, username: str):
        if user is None:
            user = ctx.message.author

        if service not in self.services:
            return

        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute('''
                    INSERT INTO profile_data
                    (uid, service, username)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (uid, service)
                    DO UPDATE
                    SET username = $3
                ''', user.id, service, username)

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


    @commands.command()
    async def delProfileEntry(self, ctx, user: typing.Optional[discord.User], service: str):
        if user is None:
            user = ctx.message.author

        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute('''
                    DELETE FROM profile_data
                    WHERE uid = $1 AND service = $2
                ''', user.id, service)

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


    """
    @commands.command()
    async def profileDataMigration(self, ctx):
        # Loop through every message in #mal-anilist-vndb-etc-share
        # for initial data migration
        # This is going to be 'fun'
        return
    """

def setup(bot):
    bot.add_cog(ProfileCog(bot))