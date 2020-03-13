import asyncio
import discord
from discord.ext import commands


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    async def dm_del(self, ctx, msgs: commands.Greedy[discord.Message]):
        """
        Delete DM's from this Bot
        """
        await asyncio.wait(
            list(map(
                lambda msg: msg.delete(),
                filter(lambda m: m.channel is ctx.channel, msgs)
            ))
        )


def setup(bot):
    bot.add_cog(AdminCog(bot))
