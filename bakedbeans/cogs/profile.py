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
    'VNDB': ("https://vndb.org/", (lambda u: f"https://vndb.org/u{url_quote(u)}")),
    'MyFigureCollection': ("https://myfigurecollection.net/", (lambda u: f"https://myfigurecollection.net/profile/{url_quote(u)}")),
    'Kitsu': ("https://kitsu.io/", (lambda u: f"https://kitsu.io/users/{url_quote(u)}"))
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
            embed = embed.add_field(
                name=service,
                value=entry[0]
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
            colour=Colour.blue()
        )

        embed.set_author(
            name=f"{user.name}#{user.discriminator}",
            icon_url=user.avatar_url
        )

        logging.info(f'Getting profile data for "{user.id}"')

        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                results1 = await conn.fetch('''
                    SELECT
                    (each(data)).key as service,
                    (each(data)).value as username
                    FROM profile_data
                    WHERE uid = $1
                    ORDER BY service DESC
                ''', user.id)

                results2 = await conn.fetch('''
                    SELECT
                    badge.name as badge_name,
                    attendance.count as badge_count
                    FROM badges
                    INNER JOIN badge ON
                    badges.badge_id = badge.id
                    INNER JOIN (
                        SELECT badge_id,
                        COUNT(badge_id) as count
                        FROM badges
                        GROUP BY badge_id
                    ) attendance USING (badge_id)
                    WHERE
                    badge.server_id = $1 AND
                    badges.uid = $2
                    ORDER BY badge.id ASC
                ''', ctx.guild.id, user.id)

        accs = []
        for rec in results1:
            service, username = rec['service'], rec['username']
            logging.debug(f'"{user.id}" "{service}" "{username}"')

            formatter = PROFILE_SERVICES.get(service)[1]
            if formatter is not None:
                link = formatter(username)
                value = f"**{service}**: [{escape_markdown(username)}]({link})"
                accs.append(value)

        if accs:
            embed.add_field(
                name="Links",
                value="\n".join(accs)
            )

        badges = []
        for rec in results2:
            badges.append(f"{rec['badge_name']} *({rec['badge_count']})*")

        if badges:
            embed.add_field(
                name="Badges",
                value="\n".join(badges)
            )

        if not embed.fields:
            embed.add_field(
                name="No Data Available",
                value="*Higurashi Sounds*"
            )

        embed.set_footer(text="Unstable Feature")

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


    @profile.command(name='addlink')
    async def profile_addlink(self, ctx, user: typing.Optional[discord.User], url: str):
        """
        Add a link to your profile (if service is accepted)
        """

        if url.endswith('/'):
            url = url[:-1]

        if url.startswith("https://"):
            url = url[8:]
        elif url.startswith("http://"):
            url = url[7:]

        service = None
        username = None
        if url.startswith("myanimelist.net/profile/"):
            service = 'MyAnimeList'
            username = url[len("myanimelist.net/profile/"):]
        elif url.startswith("anilist.co/user/"):
            service = 'AniList'
            username = url[len("anilist.co/user/"):]
        elif url.startswith("github.com/"):
            service = 'GitHub'
            username = url[len("github.com/"):]
        elif url.startswith("vndb.org/u"):
            service = 'VNDB'
            username = url[len("vndb.org/u"):]
        elif url.startswith("myfigurecollection.net/profile/"):
            service = 'MyFigureCollection'
            username = url[len("myfigurecollection.net/profile/"):]
        elif url.startswith("kitsu.io/users/"):
            service = 'Kitsu'
            username = url[len("kitsu.io/users/"):]

        if service is not None:
            await self.profile_add(ctx, user, service, username)


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
