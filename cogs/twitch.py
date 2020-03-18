import discord
from discord.ext import tasks, commands

import asyncio
import pydle
import typing


class TwitchBot(pydle.Client):
    def __init__(self):
        super().__init__(
            nickname=os.getenv('TWITCH_BOT_NICK')
        )

    async def connect(self):
        await super().connect(
            hostname='irc.chat.twitch.tv',
            port=6697,
            password=os.getenv('TWITCH_BOT_PASSWORD'),
            tls=True,
            tls_verify=False
        )

    async def on_connect(self):
        await super().on_connect()
        # await self.capreq(':twitch.tv/membership')
        # await self.capreq(':twitch.tv/tags')
        await self.capreq(':twitch.tv/commands')
        # await self.join(f'#{self.twitch_chan}')

    async def capreq(self, message):
        await self.rawmsg('CAP REQ', message)

    async def host_target(self, host_chan: str, chan: typing.Optional[str] = None, num_viewers: typing.Optional[int] = None):
        # Based on https://dev.twitch.tv/docs/irc/commands#hosttarget-twitch-commands

        if chan is None:
            chan = '-'

        if num_viewers is None:
            msg = chan
        else:
            msg = f'{chan} {num_viewers}'

        await self.rawmsg('HOSTTARGET', f'#{self.host_chan}', msg)

class TwitchCog(commands.Bot):
    def __init__(self, bot):
        self.bot = bot
        self.twitch = TwitchBot()
        self.lock = asyncio.Lock()
        self.host_chan = os.getenv('TWITCH_BOT_CHAN')
        asyncio.create_task(self.twitch.connect())

    def cog_unload(self):
        asyncio.create_task(self.twitch.disconnect())

    @classmethod
    async def is_rsfa_admin(cls, ctx):
        try:
            guild = ctx.bot.get_guild(ctx.bot.config['server'])
            member = guild.get_member(ctx.author.id)
            return member.guild_permissions.administrator
        except:
            return False

    @commands.command(hidden=True)
    @commands.check(is_rsfa_admin)
    async def host(self, ctx, chan: str):
        self.twitch.host(chan)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(hidden=True)
    @commands.check(is_rsfa_admin)
    async def unhost(self, ctx):
        self.twitch.unhost(chan)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @tasks.loop(minutes=15.0)
    async def host_update(self):
        # self.twitch.host_target(self.host_chan, channel)
        # self.twitch.host_target(self.host_chan)
        pass


def setup(bot):
    bot.add_cog(TwitchCog(bot))
