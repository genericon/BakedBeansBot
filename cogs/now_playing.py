import discord
from discord.ext import commands

from random import choice

import logging

class NowPlaying(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx):
        """
        Play a Random Game
        """

        games = list(filter(lambda x: x['type'] == 0, self.bot.config['activity']))
        game = choice(games)
        game_name = game['name']
        await self.bot.change_presence(activity=discord.Game(name=game_name))
        logging.info(f'Set Presense to: {game_name}')
        await ctx.send(f'Now Playing: "{game_name}"!')

    @commands.command()
    async def status(self, ctx):
        """
        Set a Random Status
        """

        status_list = list(filter(lambda x: x['type'] == 4, self.bot.config['activity']))
        status = choice(status_list)
        status_text = status['name']
        # Waiting on Custom Status support for discord.py
        #logging.info(f'Set Status to: {status_text}')
        await ctx.send(f'Status: "{status_text}"!')


def setup(bot):
    bot.add_cog(NowPlaying(bot))
