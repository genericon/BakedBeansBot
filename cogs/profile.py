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
        self.services = {
            'MyAnimeList': (lambda u: f"https://myanimelist.net/profile/{url_quote(u)}"),
            'AniList': (lambda u: f"https://anilist.co/user/{url_quote(u)}/"),
            'GitHub': (lambda u: f"https://github.com/{url_quote(u)}"),
            'VNDB': (lambda u: f"https://vndb.org/{url_quote(u)}"),
            'MyFigureCollection': (lambda u: f"https://myfigurecollection.net/profile/{url_quote(u)}")
        }

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

        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                results = await conn.fetch('''
                    SELECT
                    (each(data)).key as service,
                    (each(data)).value as username
                    FROM profile_data
                    WHERE uid = $1
                    ORDER BY service DESC
                ''', user.id)

        for rec in results:
            service, username = rec['service'], rec['username']
            logging.debug(f'"{user.id}" "{service}" "{username}"')

            func = self.services.get(service)
            if func is not None:
                link = func(username)
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
                    (uid, data)
                    VALUES ($1, hstore($2, $3))
                    ON CONFLICT (uid)
                    DO UPDATE
                    SET data = profile_data.data || EXCLUDED.data
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
                    UPDATE profile_data
                    SET data = delete(data, $2)
                    WHERE uid = $1
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


def setup(bot):
    bot.add_cog(ProfileCog(bot))
