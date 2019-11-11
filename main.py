import asyncio
from datetime import datetime
import discord
from discord.ext import commands
import json
import logging
import os

INITIAL_EXTENSIONS = [
    'cogs.help',
    'cogs.admin',
    'cogs.general',
    'cogs.status',
    'cogs.roles'
]


def config_load():
    with open('config.json', 'r', encoding='utf-8') as doc:
        # Please make sure encoding is correct, especially after editing the config file
        return json.load(doc)


async def run():
    """
    Where the bot gets started. If you wanted to create an database connection pool or other session for the bot to use,
    it's recommended that you create it here and pass it to the bot as a kwarg.
    """

    config = config_load()
    description = config.pop('description')
    bot = Bot(config=config,
              description=description)
    try:
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))
    except KeyboardInterrupt:
        await bot.logout()


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=self.get_prefix_,
            description=kwargs['description']
        )
        self.start_time = None
        self.app_info = None

        self.config = kwargs['config']

        self.loop.create_task(self.track_start())

        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
                logging.info(f'Loaded {extension}')
            except Exception as e:
                error = f'{extension}\n {type(e).__name__} : {e}'
                logging.warning(f'Failed to load extension {error}')

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time.
        Can be used to work out uptime.
        """
        await self.wait_until_ready()
        self.start_time = datetime.utcnow()

    @staticmethod
    async def get_prefix_(bot, message):
        """
        A coroutine that returns a prefix.

        I have made this a coroutine just to show that it can be done. If you needed async logic in here it can be done.
        A good example of async logic would be retrieving a prefix from a database.
        """
        prefix = ['!', '?']
        return commands.when_mentioned_or(*prefix)(bot, message)

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        self.app_info = await self.application_info()
        logging.info(f'Logged in as: {self.user.name}')
        logging.info(f'Using discord.py version: {discord.__version__}')
        logging.info(f'Owner: {self.app_info.owner}')

    async def on_message(self, message):
        """
        This event triggers on every message received by the bot. Including one's that it sent itself.

        If you wish to have multiple event listeners they can be added in other cogs. All on_message listeners should
        always ignore bots.
        """
        # ignore all bots
        if message.author.bot:
            return
        await self.process_commands(message)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
