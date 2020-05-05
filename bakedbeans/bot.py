from datetime import datetime
import discord
from discord.ext import commands
import logging
import traceback

from bakedbeans import db

class BakedBeansBot(commands.Bot):
    def __init__(self, **kwargs) -> None:
        super().__init__(
            command_prefix=self._get_prefix,
        )
        self.start_time = None

        self.config = kwargs.get('config', {})

        self.logger = logging.getLogger(__name__)
        self._extensions = [
            'bakedbeans.cogs.help',
            'bakedbeans.cogs.admin',
            'bakedbeans.cogs.bas',
            'bakedbeans.cogs.general',
            'bakedbeans.cogs.mention',
            'bakedbeans.cogs.poke',
            'bakedbeans.cogs.status',
            'bakedbeans.cogs.roles',
            'bakedbeans.cogs.profile',
            'bakedbeans.cogs.events'
        ]
        self.load_extensions()

        self.loop.create_task(self.track_start())

    async def _get_prefix(self, bot, message):
        return ('bbb.',)

    def load_extensions(self) -> None:
        for extension in self._extensions:
            try:
                self.load_extension(extension)
                self.logger.info(f'Loaded {extension}')
            except Exception as e:
                error = f'{type(e).__name__} : {e}'
                self.logger.warning(f'Failed to load extension {extension}\n {error}')

    async def start(self, *args, **kwargs) -> None:
        self.db = await db.create_pool()
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        await super().close()
        await self.db.close()

    async def track_start(self) -> None:
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out uptime.
        """
        await self.wait_until_ready()
        self.start_time = datetime.utcnow()

    async def on_ready(self) -> None:
        """
        This event is called every time the bot connects or resumes connection.
        """
        app_info = await self.application_info()
        self.logger.info(f'Logged in as: {self.user.name}')
        self.logger.info(f'Using discord.py version: {discord.__version__}')
        self.logger.info(f'Owner: {app_info.owner}')

    async def on_message(self, message) -> None:
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.

        If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
        always ignore bots.
        """
        # ignore all bots
        if message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_error(self, context, exception) -> None:
        tb = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        self.logger.error(f'Ignoring exception in command {context.command}:\n{tb}')
