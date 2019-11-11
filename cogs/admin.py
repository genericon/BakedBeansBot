import discord
from discord.ext import commands


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    async def delete_dm(self, ctx, msg_id: int):
        """
        Delete DM's from Bot
        """

        msg = await ctx.message.channel.fetch_message(msg_id)
        await msg.delete()


def setup(bot):
    bot.add_cog(AdminCog(bot))
