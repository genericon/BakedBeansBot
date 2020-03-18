import discord
from discord import Colour
from discord.ext import commands

import functools
import operator
import typing

async def is_rsfa(ctx):
    try:
        return ctx.guild.id == ctx.bot.config['server']
    except:
        return False

class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    async def change_color(self, ctx, colour: typing.Optional[discord.Colour]):
        """
        Change Role Color for Users
        """

        guild = self.bot.get_guild(self.bot.config['server'])
        member = guild.get_member(ctx.author.id)
        highest_role = member.roles[-1]
        if colour is None:
            colour = Colour.default()

        if highest_role.id in self.bot.config['group_roles'].values():
            await ctx.send(f'Cannot change color for Group "{highest_role.name}"!')
        else:
            await highest_role.edit(colour=colour)
            await ctx.send(f'Updated color for "{highest_role.name}"!')


    @commands.command()
    @commands.guild_only()
    @commands.check(is_rsfa)
    async def appoint(self, ctx, target_member: discord.Member, new_role: discord.Role):
        """Appoint User to a Role"""
        member = ctx.author

        if not member.guild_permissions.administrator:
            appoint_roles = self.bot.config['appoint_roles']

            appointable_roles = map(lambda r: appoint_roles.get(r.name, []), member.roles)
            appointable_roles = functools.reduce(operator.iconcat, appointable_roles, [])

            if not any(map(lambda r: r.id == new_role.id, appointable_roles)):
                await ctx.send(f'You are not authorized to appoint role "{new_role}"!')
                return

        await target_member.add_roles(new_role)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


def setup(bot):
    bot.add_cog(RolesCog(bot))
