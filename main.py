import asyncio
import json
import logging
import os

from bakedbeans import BakedBeansBot


def config_load():
    conf = {}
    with open('config.json', 'r', encoding='utf-8') as doc:
        conf.update(json.load(doc))
    with open('config_secret.json', 'r', encoding='utf-8') as doc:
        conf.update(json.load(doc))
    return conf


async def run():
    bot = BakedBeansBot(config=config_load())
    try:
        token = os.getenv('DISCORD_BOT_TOKEN')
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.set_debug(False)
    loop.run_until_complete(run())
