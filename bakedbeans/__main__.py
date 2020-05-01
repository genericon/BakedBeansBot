import asyncio
import json
import logging
import os

import time
import socket

from .bot import BakedBeansBot


def wait_for_port(port: int, host: str = 'localhost', timeout: float = 15.0) -> None:
    """
    Wait until a port starts accepting TCP connections.
    Based on https://gist.github.com/butla/2d9a4c0f35ea47b7452156c96a4e7b12

    :param port: port number
    :param host: host address on which the port should exist
    :param timeout: how many seconds to wait
    :raises TimeoutError: The port isn't accepting connections (before timeout)
    """

    start_time = time.perf_counter()
    while True:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return
        except OSError as ex:
            time.sleep(0.01)
            end_time = time.perf_counter()
            if end_time - start_time >= timeout:
                raise TimeoutError(
                    f'Waited too long for the port {port} on host {host} to start accepting '
                    'connections.'
                ) from ex


def wait_for_it():
    waitable = os.getenv('WAIT_FOR_IT')
    if waitable is not None:
        host, port = waitable.split(":", 1)
        port = int(port)
        wait_for_port(port, host)


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
    wait_for_it()
    loop = asyncio.get_event_loop()
    loop.set_debug(False)
    loop.run_until_complete(run())
