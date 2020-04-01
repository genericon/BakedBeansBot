import discord
from discord.ext import commands


async def is_guild_admin(ctx):
    try:
        return ctx.author.guild_permissions.administrator
    except:
        return False


async def is_test_guild(ctx):
    try:
        return ctx.guild.id == 416940353564704768
    except:
        return False


class BakaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.check(is_guild_admin)
    @commands.check(is_test_guild)
    async def backup_nicks(self, ctx):
        params = []
        for member in ctx.guild.members:
            params.append((member.id, ctx.guild.id, member.nick))

        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                await conn.executemany('''
                    INSERT INTO baka_nicks
                    (user_id, server_id, nick)
                    VALUES ($1, $2, $3)
                ''', params)

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.check(is_guild_admin)
    @commands.check(is_test_guild)
    async def restore_nicks(self, ctx):
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                params = await conn.fetch('''
                    SELECT
                    user_id, nick
                    FROM baka_nicks
                    WHERE server_id = $1
                ''', ctx.guild.id)

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

        for member_info in params:
            member = ctx.guild.get_member(member_info['user_id'])
            member.edit(nick=member_info['nick'])


    @commands.command(hidden=True)
    @commands.guild_only()
    @commands.check(is_guild_admin)
    @commands.check(is_test_guild)
    async def baka(self, ctx):
        for member in ctx.guild.members:
            member.edit(nick='Baka')


def setup(bot):
    bot.add_cog(BakaCog(bot))
