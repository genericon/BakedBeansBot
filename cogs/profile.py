import discord
from discord.ext import commands
from discord.utils import escape_markdown

from urllib.parse import quote as url_quote

import logging
import typing

# import tempfile


class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.services = ['MyAnimeList', 'AniList', 'VNDB', 'MyFigureCollection']

    @commands.command()
    async def profile(self, ctx, user: typing.Optional[discord.User]):
        if user is None:
            user = ctx.message.author

        embed = discord.Embed(
            title='Profile',
            description=user.name,
            colour=discord.Colour.blue()
        )

        logging.info(f'Getting profile data for "{user.id}"')

        results = []
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                results = await conn.fetch('''
                    SELECT service, username
                    FROM profile_data
                    WHERE uid = $1
                    ORDER BY service DESC
                ''', user.id)

        for rec in results:
            service, username = rec['service'], rec['username']
            logging.debug(f'"{user.id}" "{service}" "{username}"')

            if service == 'MyAnimeList':
                link = f"https://myanimelist.net/profile/{url_quote(username)}"
            elif service == 'AniList':
                link = f"https://anilist.co/user/{url_quote(username)}/"
            elif service == 'VNDB':
                link = f"https://vndb.org/{url_quote(username)}"
            elif service == 'MyFigureCollection':
                link = f"https://myfigurecollection.net/profile/{url_quote(username)}"

            value = f"[{escape_markdown(username)}]({link})"

            embed = embed.add_field(
                name=service,
                value=value,
                inline=True
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def profile_set(self, ctx, user: typing.Optional[discord.User], service: str, username: str):
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
                    SET username = EXCLUDED.username
                ''', user.id, service, username)

        logging.info(f'Set Service "{service}" to username "{username}" for "{user.id}"')

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


    @commands.command()
    async def profile_del(self, ctx, user: typing.Optional[discord.User], service: str):
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
    async def profile_export(self, ctx):
        with tempfile.TemporaryFile() as fp:
            async with self.bot.db.acquire() as conn:
                async with conn.transaction():
                    await conn.copy_from_table('profile_data', output=fp, format='csv')
            fp.seek(0)
            await ctx.send(file=discord.File(fp, 'export.csv'))
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


    @commands.command()
    async def profile_import(self, ctx):
        attached = ctx.message.attachments[0]
        with tempfile.TemporaryFile() as fp:
            await attached.save(fp, seek_begin=True)
            async with self.bot.db.acquire() as conn:
                async with conn.transaction():
                    await conn.copy_to_table('profile_data', source=fp, format='csv')
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
    """

    """
    @commands.command()
    async def profile_import_channel(self, ctx):
        # Loop through every message in #mal-anilist-vndb-etc-share
        # for initial data migration
        # This is going to be 'fun'
        return
    """

def setup(bot):
    bot.add_cog(ProfileCog(bot))
