import discord
from discord import Colour
from discord.ext import commands


class RoleManagement(commands.Cog):
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
    async def appoint(self, ctx):
        '''Appoint User to Role (WIP)'''
        server = self.bot.get_guild(self.bot.config['server'])
        print([(i.name, i.id) for i in server.roles])
        await ctx.send("WIP Command!")


def setup(bot):
    bot.add_cog(RoleManagement(bot))
