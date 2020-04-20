import discord
from discord import Colour
from discord.ext import commands

import asyncio
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
        self.e_lock = asyncio.Lock()
        self.e_stage = ElectionStage.NONE
        self.e_pos = None
        self.e_nom = set()
        self.e_votes = dict()


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

        # if role.id not in ctx.bot.config['officer_roles'].values():
        #     await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        #     return

        # if role.guild.id != ctx.guild.id:
        #     await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

        async with self.e_lock:
            if self.e_stage != ElectionStage.NONE:
                # An election is currently going on
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

            else:
                self.e_stage = ElectionStage.NOMINATION
                self.e_pos = role
                self.e_nom.clear()
                self.e_votes.clear()

                await ctx.send(f'Election started for "{role.name}". Ready for nominations.')


    @election.command(pass_context=True)
    async def nominate(self, ctx, member: discord.Member):
        """
        Nominate a member for current election
        """

        async with self.e_lock:
            if self.e_stage != ElectionStage.NOMINATION:
                # The nomination stage is over
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

            else:
                self.e_nom.add(member.id)
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
            async with self.e_lock:
                self.e_stage = stage_enum


    @election.command(pass_context=True)
    async def review(self, ctx):
        """
        Review Results (supposed to be for admin officers)
        """

        embed = None

        async with self.e_lock:
            if self.e_stage != ElectionStage.REVIEW:
                # The review stage is over
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

            else:
                # TODO: Fill embed with content
                embed = discord.Embed(
                    title='Election Review:',
                    description=f'Results for "{self.e_pos.name}"',
                    colour=Colour.blue()
                )

        if embed is not None:
            await ctx.send(embed=embed)

    @election.command(pass_context=True)
    async def elect(self, ctx, member: discord.Member):
        """
        Set the election stage
        """

        async with self.e_lock:
            if self.e_stage != ElectionStage.REVIEW:
                # The nomination stage is over
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

            else:
                self.e_stage = ElectionStage.NONE
                # winner = member.id
                # TODO: Announce Winner

    @election.command(pass_context=True)
    async def vote(self, ctx):
        """
        Request Vote DM
        """

        async with self.e_lock:
            if self.e_stage != ElectionStage.VOTING:
                # The voting stage is over
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

            else:
                self.bot.dispatch('vote_request', ctx.message)

    @commands.Cog.listener()
    async def on_vote_request(self, message):
        # ctx = await self.bot.get_context(message)

        if message.author.dm_channel is None:
            message.author.create_dm()

        channel = message.author.dm_channel

        # TODO: Send DM Embed with Voting Options
        # dm_message = await channel.send()

        # TODO: Add reactions corresponding to options

        def vote_check(reaction, user):
            if reaction.message != dm_message:
                return False
            # TODO: Check if valid reaction for options
            return True

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=vote_check)
            async with self.e_lock:
                if self.e_stage == ElectionStage.VOTING:
                    await channel.send('\N{THUMBS UP SIGN}')
                    # TODO: Add vote to dict
                else:
                    await channel.send('Voting is Over')
        except asyncio.TimeoutError:
            await channel.send('Vote Request Expired')
        finally:
            await dm_message.delete()


def setup(bot):
    bot.add_cog(ElectionCog(bot))
