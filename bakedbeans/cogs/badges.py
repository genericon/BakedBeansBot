import discord
from discord.ext import commands

import logging
import typing


class BadgeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(hidden=True, pass_context=True)
    async def badges(self, ctx):
        """
        Manage Badges
        """
        if ctx.invoked_subcommand is None:
            # await ctx.send('Invalid badge command passed...')
            await self.badges_view(ctx, None)


    @badges.command(name='view')
    async def badges_view(self, ctx, user: typing.Optional[discord.User]):
        """
        View All User Badges
        """
        if user is None:
            user = ctx.message.author

        embed = discord.Embed(
            title='Badges',
            description=user.name,
            colour=discord.Colour.blue()
        )

        logging.info(f'Getting badge data for "{user.id}"')

        results = []
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                results = await conn.fetch('''
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

        for rec in results:
            embed = embed.add_field(
                name=rec['badge_name'],
                value=rec['badge_count'],
                inline=False
            )

        await ctx.send(embed=embed)

    @badges.command(name='pull')
    @commands.has_guild_permissions(administrator=True)
    async def badge_pull(self, ctx, user: typing.Optional[discord.User]):
        """
        Pull Badge Data from DB and assign appropiate roles
        """
        if user is None:
            user = ctx.message.author

        logging.info(f'Getting badge data for "{user.id}"')

        badges = []
        async with self.bot.db.acquire() as conn:
            badges = await conn.fetch('''
                SELECT
                badges.role_id as role_id,
                FROM badges
                INNER JOIN badge ON
                badges.badge_id = badge.id
                WHERE
                badge.server_id = $1 AND
                badges.uid = $2
            ''', ctx.guild.id, user.id)

        roles = []
        for badge in badges:
            roles.append(ctx.guild.get_role(badge['role_id']))

        user.add_roles(*roles)

    @badges.command(name='create')
    @commands.has_guild_permissions(administrator=True)
    async def badge_create(self, ctx, badge: typing.Union[discord.Role, str]):
        """
        Create New Badge
        """
        role_id = None
        name = ''

        if isinstance(badge, discord.Role):
            role_id = role.id
            name = role.name
        elif isinstance(badge, str):
            name = badge

        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute('''
                    INSERT INTO badge
                    (server_id, role_id, name)
                    VALUES ($1, $2)
                ''', ctx.guild.id, role_id, name)

        logging.info(f'Create badge "{name}"')

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @badges.command(name='push')
    @commands.has_guild_permissions(administrator=True)
    async def badge_push(self, ctx):
        """
        Push Badge Data to DB
        """
        server = ctx.guild

        async with self.bot.db.acquire() as conn:
            badges = []
            async with conn.transaction():
                badge_list = await conn.fetch('''
                    SELECT id, role_id, name
                    FROM badge
                    WHERE server_id = $1 AND
                    role_id IS NOT NULL
                ''', server.id)

                for badge in badge_list:
                    role = server.get_role(badge['role_id'])
                    if badge['name'] != role.name:
                        await conn.execute('''
                            UPDATE badge
                            SET name = $2
                            WHERE id = $1
                        ''', badge['id'], role.name)
                    for member in role.members:
                        badges.append((member.id, badge['id'],))

            async with conn.transaction():
                await conn.executemany('''
                    INSERT INTO badges
                    (uid, badge_id)
                    VALUES ($1, $2)
                    ON CONFLICT
                    DO NOTHING
                ''', badges)

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        # await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

    @badges.command(name='diff')
    @commands.has_guild_permissions(administrator=True)
    async def badge_diff(self, ctx):
        # TODO: Validate Data and make sure there's no badge data mismatch
        server = ctx.guild

        async with self.bot.db.acquire() as conn:
            badges = []
            async with conn.transaction():
                badge_list = await conn.fetch('''
                    SELECT id, role_id, name
                    FROM badge
                    WHERE server_id = $1 AND
                    role_id IS NOT NULL
                ''', server.id)

                for badge in badge_list:
                    role = server.get_role(badge['role_id'])
                    if badge['name'] != role.name:
                        ctx.send(f'{badge['id']} "{badge['name']}" "{role.name}"')

                    users = await conn.fetch('''
                        SELECT uid
                        FROM badges
                        WHERE badge_id = $1
                    ''', badge['id'])

                    s1 = set()
                    for user in users:
                        s1.add(user['uid'])

                    s2 = set()
                    for member in role.members:
                        s2.set(member.id)

                    s1_2 = s1 - s2
                    s2_1 = s2 - s1

                    for u in s1_2:
                        ctx.send(f'{badge['id']} (S1 - S2): {u}')
                    for u in s2_1:
                        ctx.send(f'{badge['id']} (S2 - S1): {u}')


    """
    @badges.command(name='add_user')
    async def events_add_user(self, ctx, user: typing.Optional[discord.User], service: str):
        if user is None:
            user = ctx.message.author

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

    @badges.command(name='rm_user')
    async def events_rm_user(self, ctx, user: typing.Optional[discord.User], service: str):
        if user is None:
            user = ctx.message.author

        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute('''
                    INSERT INTO event
                    (uid, service, username)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (uid, service)
                    DO UPDATE
                    SET username = EXCLUDED.username
                ''', user.id, service, username)

        logging.info(f'Set Service "{service}" to username "{username}" for "{user.id}"')

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
    """

    """
    @commands.dm_only()
    @badges.command(name='import_server')
    async def events_import_server(self, ctx, server_id: int):
        # Import all server roles into the db
        # Filter through them manually later
        server = self.bot.get_guild(server_id)

        if server is not None:
            async with self.bot.db.acquire() as conn:
                for role in server.roles:
                    async with conn.transaction():
                        await conn.execute('''
                            INSERT INTO events
                            (role_id, name, server_id)
                            VALUES ($1, $2, $3)
                            ON CONFLICT
                            DO NOTHING
                        ''', role.id, role.name, role.guild.id)

                    event_id = await conn.fetchval('''
                        SELECT id
                        FROM events
                        WHERE role_id = $1
                    ''', role.id)

                    async with conn.transaction():
                        for member in role.members:
                            await conn.execute('''
                                INSERT INTO events_data
                                (uid, event_id)
                                VALUES ($1, $2)
                                ON CONFLICT
                                DO NOTHING
                            ''', member.id, event_id)
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        else:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
    """


def setup(bot):
    bot.add_cog(BadgeCog(bot))
