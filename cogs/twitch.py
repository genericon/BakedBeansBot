import discord
from discord.ext import tasks, commands

import asyncio
import pydle


class TwitchBot(pydle.Client):
    def __init__(self):
        super().__init__(
            nickname=os.getenv('TWITCH_BOT_NICK')
        )
        self.twitch_chan = os.getenv('TWITCH_BOT_CHAN')

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
        # await self.join(f'#{self.twitch_chan}')

    async def capreq(self, message):
        await self.rawmsg('CAP REQ', message)

    async def host(self, chan):
        # await self.rawmsg('HOSTTARGET', f'#{self.twitch_chan}', f':{chan}')
        await self.message(f'#{self.twitch_chan}', f'.host {chan}')

    async def unhost(self):
        # await self.rawmsg('HOSTTARGET', f'#{self.twitch_chan}', ':-')
        await self.message(f'#{self.twitch_chan}', '.unhost')


class TwitchCog(commands.Bot):
    def __init__(self, bot):
        self.bot = bot
        self.twitch = TwitchBot()
        self.lock = asyncio.Lock()
        asyncio.create_task(self.twitch.connect())

    @classmethod
    async def is_rsfa_admin(cls, ctx):
        try:
            guild = ctx.bot.get_guild(ctx.bot.config['server'])
            member = guild.get_member(ctx.author.id)
            return member.guild_permissions.administrator
        except:
            return False

    @commands.command(hidden=True)
    @commands.check(self.is_rsfa_admin)
    async def host(self, ctx, chan: str):
        self.twitch.host(chan)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @commands.command(hidden=True)
    @commands.check(self.is_rsfa_admin)
    async def unhost(self, ctx):
        self.twitch.unhost(chan)
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


    @tasks.loop(minutes=15.0)
    async def host_update(self):
        # self.twitch.host(channel)
        # self.twitch.unhost()
        pass


def setup(bot):
    bot.add_cog(TwitchCog(bot))
