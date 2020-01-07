from discord.ext import commands

import functools
import operator
import typings


class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def is_rsfa(ctx):
        return ctx.guild and ctx.guild.id == ctx.bot.config['server']

    @commands.command()
    @commands.dm_only()
    async def change_color(self, ctx, colour: typing.Optional[discord.Colour]):
        """
        Change Role Color for Users
        """

        server = self.bot.get_guild(self.bot.config['server'])
        user = server.get_member(ctx.message.author.id)
        highest_role = user.roles[-1]
        if colour is None:
            colour = Colour.default()

        if highest_role.id in self.bot.config['group_roles'].values():
            await ctx.send(f'Cannot change color for Group "{highest_role.name}"!')
        else:
            await highest_role.edit(colour=colour)
            await ctx.send(f'Updated color for "{highest_role.name}"!')


    @commands.command()
    @commands.check(is_rsfa)
    async def appoint(self, ctx, new_role: discord.Role, target_member: discord.Member):
        """Appoint User to a Role"""
        server = self.bot.get_guild(self.bot.config['server'])
        user = server.get_member(ctx.message.author.id)
        appoint_roles = self.bot.config['appoint_roles']

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
