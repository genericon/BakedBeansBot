import discord
from discord import Colour
from discord.ext import commands

import asyncio
import functools
import operator
import typing

from enum import Enum

class ElectionStage(Enum):
    NONE = 0
    NOMINATION = 1
    PRESENTATION = 2
    VOTING = 3
    REVIEW = 4


async def is_rsfa(ctx):
    try:
        return ctx.guild.id == ctx.bot.config['server']
    except:
        return False


class ElectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.e_state = {
            position: None,
            stage: ElectionStage.NONE,
            nominations: set(),
            votes: set(),
            winner: None
        }


    @commands.group(pass_context=True)
    @commands.guild_only()
    @commands.check(is_rsfa)
    @commands.max_concurrency(1, commands.BucketType.guild, True)
    async def election(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid election command passed')


    @election.command(pass_context=True)
    async def start(self, ctx, role: discord.Role):
        """
        Start Election Nomination Stage
        """

        if role.id not in ctx.bot.config['officer_roles'].values():
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
            return

        if role.guild.id != ctx.guild.id:
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
            return

        if self.e_state.stage != ElectionStage.NONE:
            # An election is currently going on
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
            return

        self.e_state = {
            position: role.id,
            stage: ElectionStage.NOMINATION
            nominations: set(),
            votes: {},
            winner: None
        }

        await ctx.send(f'Election started for "{role.name}". Ready for nominations.')


    @election.command(pass_context=True)
    async def nominate(self, ctx, member: discord.Member):
        """
        Nominate a member for current election
        """

        # if role.id not in ctx.bot.config['officer_roles'].values():
        #     await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

        if self.e_state.stage != ElectionStage.NOMINATION:
            # The nomination stage is over
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

        else:
            self.e_state.nominations.add(member.id)
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


    @election.command(pass_context=True)
    async def stage(self, ctx, stage: str):
        """
        Set the election stage
        """

        stage_enum = None

        if stage == 'nomination':
            stage_enum = ElectionStage.NOMINATION
        elif stage == 'presentation':
            stage_enum = ElectionStage.PRESENTATION
        elif stage == 'voting':
            stage_enum = ElectionStage.VOTING
        elif stage == 'review':
            stage_enum = ElectionStage.REVIEW
        elif stage == 'none':
            stage_enum = ElectionStage.NONE

        if stage_enum is not None:
            self.e_state.stage = stage_enum


    @election.command(pass_context=True)
    async def review(self, ctx):
        """
        Set the election stage
        """

        if self.e_state.stage != ElectionStage.REVIEW:
            # The nomination stage is over
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
            return

        embed = discord.Embed(
            title='Election Review:',
            description=self.bot.description,
            colour=Colour.blue()
        ).add_field(
            name='Contributing',
            value='Check out the source on [GitHub](https://github.com/genericon/BakedBeansBot)',
            inline=False
        ).add_field(
            name='License',
            value='BakedBeansBot is released under the MIT License',
            inline=False
        )

        await ctx.send(embed=embed)

    @election.command(pass_context=True)
    async def elect(self, ctx, member: discord.Member):
        """
        Set the election stage
        """

        if self.e_state.stage != ElectionStage.REVIEW:
            # The nomination stage is over
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
            return

        else:
            self.e_state.stage = ElectionStage.NONE
            self.e_state.winner = member.id
            # TODO: Announce Winner
            # TODO: Announce Winner


    @election.command(pass_context=True)
    async def vote(self, ctx, member: discord.Member):
        """
        Set the election stage
        """

        if self.e_state.stage != ElectionStage.VOTING:
            # The nomination stage is over
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

        else:
            # TODO: Send PM
            # TODO: Dispatch separate command to get around bucket


def setup(bot):
    bot.add_cog(ElectionCog(bot))
