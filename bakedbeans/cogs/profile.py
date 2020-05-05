import discord
from discord import Colour
from discord.ext import commands
from discord.utils import escape_markdown

from urllib.parse import quote as url_quote

import logging
import typing

# import tempfile

PROFILE_SERVICES = {
    'MyAnimeList': ("https://myanimelist.net/", (lambda u: f"https://myanimelist.net/profile/{url_quote(u)}")),
    'AniList': ("https://anilist.co/", (lambda u: f"https://anilist.co/user/{url_quote(u)}/")),
    'GitHub': ("https://github.com/", (lambda u: f"https://github.com/{url_quote(u)}")),
    'VNDB': ("https://vndb.org/", (lambda u: f"https://vndb.org/{url_quote(u)}")),
    'MyFigureCollection': ("https://myfigurecollection.net/", (lambda u: f"https://myfigurecollection.net/profile/{url_quote(u)}"))
}

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def profile(self, ctx):
        """
        Manage Profile
        """
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid profile command passed...')

    @profile.command(name='services')
    async def profile_services(self, ctx):
        """
        View supported services
        """

        embed = discord.Embed(
            title='Services',
            colour=Colour.blue()
        )

        for service, entry in PROFILE_SERVICES.items():
            link = entry[0]
            value = f"[{escape_markdown(service)}]({link})"
            embed = embed.add_field(
                value=value,
                inline=True
            )

        await ctx.send(embed=embed)

    @profile.command(name='view')
    async def profile_view(self, ctx, user: typing.Optional[discord.User]):
        """
        Displays user profile
        """

        if user is None:
            user = ctx.message.author

        embed = discord.Embed(
            title='Profile',
            description=user.name,
            colour=Colour.blue()
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

            formatter = PROFILE_SERVICES.get(service)[1]
            if formatter is not None:
                link = formatter(username)
                value = f"[{escape_markdown(username)}]({link})"
                embed = embed.add_field(
                    name=service,
                    value=value,
                    inline=True
                )

        await ctx.send(embed=embed)

    @profile.command(name='add')
    async def profile_add(self, ctx, user: typing.Optional[discord.User], service: str, username: str):
        """
        Add a service to your profile
        """

        if user is None:
            user = ctx.message.author

        if service not in PROFILE_SERVICES:
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


    @profile.command(name='rm')
    async def profile_rm(self, ctx, user: typing.Optional[discord.User], service: str):
        """
        Remove a service to your profile
        """
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
    @profile.command(name='export')
    async def profile_export(self, ctx):
        with tempfile.TemporaryFile() as fp:
            async with self.bot.db.acquire() as conn:
                async with conn.transaction():
                    await conn.copy_from_table('profile_data', output=fp, format='csv')
            fp.seek(0)
            await ctx.send(file=discord.File(fp, 'export.csv'))
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


    @profile.command(name='import')
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
