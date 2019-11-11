from discord import Colour
from discord.ext import commands

import functools
import operator


class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    async def change_color(self, ctx, color=None):
        """
        Change Role Color for Users
        """

        server = self.bot.get_guild(self.bot.config['server'])
        user = server.get_member(ctx.message.author.id)
        highest_role = user.roles[-1]

        if highest_role.id in self.bot.config['group_roles'].values():
            await ctx.send(f'Cannot change color for Group "{highest_role.name}"!')
        else:
            if color:
                colour = Colour(int(color, 16))
            else:
                colour = Colour.default()

            await highest_role.edit(colour=colour)
            await ctx.send(f'Updated color for "{highest_role.name}"!')

    @commands.command()
    async def appoint(self, ctx, role_str: str, target_user: int):
        """Appoint User to a Role"""
        server = self.bot.get_guild(self.bot.config['server'])
        user = server.get_member(ctx.message.author.id)
        appoint_roles = self.bot.config['appoint_roles']

        new_role = next(filter(lambda r: r.name == role_str, server.roles), None)
        if new_role is None:
            await ctx.send(f'Invalid Role "{role_str}"!')
            return

        target_member = server.get_member(target_user)
        if target_member is None:
            await ctx.send(f'Can\'t find user with id "{target_user}"!')
            return

        is_admin = any(map(lambda r: r.permissions.administrator, user.roles))

        if not is_admin:
            appointable_roles = map(lambda r: appoint_roles.get(r.name, []), user.roles)
            appointable_roles = functools.reduce(operator.iconcat, appointable_roles, [])

            if not any(map(lambda r: r.id == new_role.id, appointable_roles)):
                await ctx.send(f'You are not authorized to appoint role "{new_role}"!')
                return

        await target_member.add_roles(new_role)

        await ctx.send("Success")


def setup(bot):
    bot.add_cog(RolesCog(bot))
