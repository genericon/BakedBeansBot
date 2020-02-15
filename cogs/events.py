import discord
from discord.ext import commands

import logging
import typing


class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def events(self, ctx, user: typing.Optional[discord.User]):
        if user is None:
            user = ctx.message.author

        embed = discord.Embed(
            title='Events',
            description=user.name,
            colour=discord.Colour.blue()
        )

        logging.info(f'Getting event data for "{user.id}"')

        results = []
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                results = await conn.fetch('''
                    SELECT
                    events.name as event_name,
                    events.id as event_id
                    FROM event_data
                    INNER JOIN events
                    ON event_data.event_id = events.id
                    WHERE event_data.server_id = $1 AND event_data.uid = $2
                    ORDER BY event_name DESC
                ''', ctx.guild.id, user.id)

        for rec in results:
            name = rec['event_name']

            embed = embed.add_field(
                name=service,
                value=value,
                inline=True
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def event_create(self, ctx, event: str):
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                await conn.execute('''
                    INSERT INTO events
                    (server_id, name)
                    VALUES ($1, $2)
                ''', ctx.guild.id, event)

        logging.info(f'Create event "{event}"')

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    """
    @commands.command()
    async def event_add_user(self, ctx, user: typing.Optional[discord.User], service: str):
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

    @commands.command()
    async def event_remove_user(self, ctx, user: typing.Optional[discord.User], service: str):
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

    @commands.command()
    @commands.dm_only()
    async def events_import_server(self, ctx):
        # Import all roles in Weeb Poly Server into the db
        # Filter through them manually later
        server = self.bot.get_guild(635261572247322639)
        if server is not None:
            async with self.bot.db.acquire() as conn:
                for role in server.roles:
                    async with conn.transaction():
                        await conn.execute('''
                            INSERT INTO events
                            (role_id, server_id)
                            VALUES ($1, $2)
                        ''', role.id, server.id)

                    event_id = await connection.fetchval('''
                        SELECT id
                        FROM event
                        WHERE role_id = $1
                    ''', role.id)

                    async with conn.transaction():
                        for member in role.members:
                            await conn.execute('''
                                INSERT INTO event_data
                                (uid, event_id)
                                VALUES ($1, $2)
                            ''', member.id, event_id)
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        else:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')        


def setup(bot):
    bot.add_cog(EventsCog(bot))
