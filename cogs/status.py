import discord
from discord.ext import commands

import random
import logging


class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def game_presence(self, ctx):
        """
        Play a Random Game
        """

        #games = list(filter(lambda x: x['type'] == 0, self.bot.config['activity']))
        #game_name = random.choice(games)['name']
        #game = discord.Game(name=game_name)

        game = None
        async with self.bot.db.acquire() as conn:
            game_name = ''
            async with conn.transaction():
                game_name = await conn.fetchval('''
                    SELECT name
                    FROM activities
                    WHERE type = 0
                    ORDER BY RANDOM()
                    LIMIT 1
                ''')
            game = discord.Game(name=game_name)


        await self.bot.change_presence(activity=game)
        logging.info(f'Set Presense to: {game_name}')
        await ctx.send(f'Now Playing: "{game_name}"!')

    @commands.command()
    async def activity_presence(self, ctx):
        """
        Set a Random Status
        """

        #statuses = list(filter(lambda x: x['type'] == 4, self.bot.config['activity']))
        #status_text = random.choice(statuses)['name']
        #status = discord.CustomActivity(name=status_text)

        status = None
        async with self.bot.db.acquire() as conn:
            r = None
            async with conn.transaction():
                r = await conn.fetchrow('''
                    SELECT name,
                    other->'emoji' as emoji
                    FROM activities
                    WHERE type = 4
                    ORDER BY RANDOM()
                    LIMIT 1
                ''')

            emoji = r['emoji']

            if emoji is not None:
                emoji = self.bot.get_emoji(emoji)

            status = discord.CustomActivity(name=r['name'], emoji=emoji)

        await self.bot.change_presence(activity=status)
        logging.info(f'Set Status to: "{name}" "{status_text}"!')
        await ctx.send(f'Status: "{name}" "{status_text}"!')

    @commands.command()
    async def clear_presence(self, ctx):
        """
        Clear Presence
        """

        await self.bot.change_presence(activity=None)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


def setup(bot):
    bot.add_cog(StatusCog(bot))
