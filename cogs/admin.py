from discord.ext import commands

import asyncio


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.dm_only()
    async def delete_dm(self, ctx, msgs: commands.Greedy[discord.Message]):
        """
        Delete DM's from Bot
        """
        await asyncio.gather(
            *(msg.delete() for msg in filter(lambda m: m.channel is ctx.channel, msgs))
        )


def setup(bot):
    bot.add_cog(AdminCog(bot))
