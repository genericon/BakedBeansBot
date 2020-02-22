import discord
from discord.ext import commands


class PokeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_mention(self, message):
        if self.bot.user.id is not message.author.id:
            ctx = await self.bot.get_context(message)
            ctx.command = self.bot.get_command('poke')
            await self.bot.invoke(ctx)

    @commands.command()
    async def poke(self, ctx):
        await ctx.send(f'Hai, {self.bot.user.mention} Desu')


def setup(bot):
    bot.add_cog(PokeCog(bot))
