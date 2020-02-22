from discord.ext import commands


class MentionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.id in message.raw_mentions:
            self.bot.dispatch('mention', message)


def setup(bot):
    bot.add_cog(MentionCog(bot))
