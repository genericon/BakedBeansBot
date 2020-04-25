import discord
from discord import Colour
from discord.ext import commands

import asyncio
import typing

from enum import Enum
from enum import unique as enum_unique


@enum_unique
class ElectionStage(Enum):
    NONE = 'none'
    NOMINATION = 'nomination'
    PRESENTATION = 'presentation'
    VOTING = 'voting'
    REVIEW = 'review'


class ElectionStageConverter(commands.Converter):
    async def convert(self, ctx, argument: str):
        stage = None

        argument = argument.lower()

        try:
            stage = ElectionStage(argument)
        except ValueError:
            pass

        return stage


async def is_rsfa(ctx):
    try:
        return ctx.guild.id == ctx.bot.config['server']
    except:
        return False

async def is_rsfa_admin(ctx):
    try:
        guild = ctx.bot.get_guild(ctx.bot.config['server'])
        member = guild.get_member(ctx.author.id)
        return member.guild_permissions.administrator
    except:
        return False


class ElectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.e_lock = asyncio.Lock()
        self.e_stage = ElectionStage.NONE
        self.e_pos = ''
        self.e_nom = set()
        self.e_votes = dict()


    def _generate_emojis(self, options: int) -> List[str]:
        _emojis = []

        if options > 10:
            for i in range(options):  # generates unicode emojis [A,B,C,…]
                hex_str = hex(224 + (6 + i))[2:]
                emoji = b'\\U0001f1a'.replace(b'a', bytes(hex_str, "utf-8"))
                emoji = emoji.decode("unicode-escape")
                _emojis.append(emoji)

        else:
            for i in range(options):  # generates unicode emojis [1,2,3,…]
                if i < 9:
                    emoji = 'x\u20e3'.replace('x', str(i + 1))
                else:
                    emoji = '\U0001f51f'

                _emojis.append(emoji)

        return _emojis

    def _get_rsfa_member(self, uid: int):
        guild = self.bot.get_guild(self.bot.config['server'])
        return guild.get_member(uid)

    @commands.group(pass_context=True)
    @commands.guild_only()
    @commands.check(is_rsfa)
    @commands.max_concurrency(1, commands.BucketType.guild, True)
    async def election(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid election command passed')


    @election.command(pass_context=True)
    async def start(self, ctx, role: typing.Union[discord.Role, str]):
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

                if isinstance(self.e_pos, str):
                    pos_name = self.e_pos
                else:
                    pos_name = self.e_pos.name

                await ctx.send(f'Election started for "{pos_name}". Ready for nominations.')


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
    async def stage(self, ctx, stage: ElectionStageConverter):
        """
        Set the election stage
        """

        if stage_enum is not None:
            async with self.e_lock:
                self.e_stage = stage_enum


    @election.command(pass_context=True)
    @commands.check(is_rsfa_admin)
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
                if isinstance(self.e_pos, str):
                    pos_name = self.e_pos
                else:
                    pos_name = self.e_pos.name

                vote_tally = {}

                for choice in self.e_nom:
                    vote_calc[choice] = []

                for voter, choice in self.e_votes.items():
                    vote_calc[choice].append(voter)

                embed = discord.Embed(
                    title='Election Review',
                    description=f'Results for "{pos_name}"',
                    colour=Colour.blue()
                )

                for choice, votes in self.vote_tally.items():
                    embed = embed.add_field(
                        name=str(choice),
                        value=len(votes),
                        inline=False
                    )


        if embed is not None:
            await ctx.send(embed=embed)

'''
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
'''

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

        choices = {}

        async with self.e_lock:
            if isinstance(self.e_pos, str):
                pos_name = self.e_pos
            else:
                pos_name = self.e_pos.name

            embed = discord.Embed(
                title='Vote',
                description=f'Ballot for "{pos_name}"',
                colour=Colour.blue()
            )

            emojis = _generate_emojis(len(self.e_nom))
            choices = dict(zip(emoji, self.e_nom))

            for emoji, nom in choices.items():
                choice_name = self._get_rsfa_member(nom).display_name
                embed = embed.add_field(
                    name=emoji,
                    value=choice_name,
                    inline=False
                )

        dm_message = await channel.send(embed=embed)

        def vote_check(reaction):
            if reaction.message != dm_message:
                return False
            return reaction.emoji in choices.keys()

        try:
            reaction = await client.wait_for('reaction_add', timeout=60.0, check=vote_check)
            async with self.e_lock:
                if self.e_stage == ElectionStage.VOTING:
                    await channel.send('\N{THUMBS UP SIGN}')
                    self.e_votes[message.author.id] = choices[reaction.emoji]
                else:
                    await channel.send('Voting is Over')
        except asyncio.TimeoutError:
            await channel.send('Vote Request Expired')
        finally:
            await dm_message.delete()


def setup(bot):
    bot.add_cog(ElectionCog(bot))
