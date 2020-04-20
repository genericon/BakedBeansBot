import discord
from discord.ext import tasks, commands

import os
import asyncio
import pydle
import typing

async def is_rsfa_admin(ctx):
    try:
        guild = ctx.bot.get_guild(ctx.bot.config['server'])
        member = guild.get_member(ctx.author.id)
        return member.guild_permissions.administrator
    except:
        return False


class TwitchBot(pydle.featurize(
		pydle.features.RFC1459Support,
		pydle.features.IRCv3Support,
		pydle.features.ircv3.CapabilityNegotiationSupport
		)):
    def __init__(self):
        nickname = os.getenv('TWITCH_BOT_NICK')
        super().__init__(
            nickname=nickname,
            realname='BakedBeansBot'
        )
        self.twitch_chan = f'#{nickname}'

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
        # await self.capreq(':twitch.tv/commands')
        await self.join(self.twitch_chan)

    def on_raw_004(self, msg):
        """
        Twitch IRC does not match what the pydle library expects
        which causes Pydle to raise exceptions.
        Override on_raw_004 and prevent super call

        Copied from:
        https://github.com/LangridgeDaniel/python-twitch-irc/blob/master/python_twitch_irc/irc.py
        """
        logging.debug(f'on_raw_004: {msg}')

    async def capreq(self, message):
        await self.rawmsg('CAP REQ', message)

    async def raid_target(self, host_chan: str, chan: typing.Optional[str] = None):
        if chan is None:
            await self.message(self.twitch_chan, '.unraid')
        else:
            await self.message(self.twitch_chan, f'.raid {chan}')

    '''
    async def host_target(self, host_chan: str, chan: typing.Optional[str] = None, num_viewers: typing.Optional[int] = None):
        # Based on https://dev.twitch.tv/docs/irc/commands#hosttarget-twitch-commands

        if chan is None:
            chan = '-'

        if num_viewers is None:
            msg = chan
        else:
            msg = f'{chan} {num_viewers}'

        await self.rawmsg('HOSTTARGET', f'#{self.host_chan}', msg)
    '''


class TwitchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.twitch = TwitchBot()
        self.lock = asyncio.Lock()
        self.host_chan = os.getenv('TWITCH_BOT_CHAN')
        asyncio.create_task(self.twitch.connect())

    def cog_unload(self):
        asyncio.create_task(self.twitch.disconnect())

    @commands.command(hidden=True)
    @commands.check(is_rsfa_admin)
    async def raid(self, ctx, chan: str):
        self.twitch.raid_target(chan)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(hidden=True)
    @commands.check(is_rsfa_admin)
    async def unraid(self, ctx):
        self.twitch.raid_target(None)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    '''
    @tasks.loop(minutes=15.0)
    async def host_update(self):
        # self.twitch.host_target(self.host_chan, channel)
        # self.twitch.host_target(self.host_chan)
        pass
    '''


def setup(bot):
    bot.add_cog(TwitchCog(bot))
