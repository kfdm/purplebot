import asyncio
import json
import logging
import os
from pathlib import Path

from discord import Client, Intents, Message

from purplebot.dispatch import dispatch

logging.basicConfig(level=logging.INFO)

try:
    import sentry_sdk

    assert os.environ["SENTRY_DSN"]
except (ImportError, AssertionError, KeyError):
    pass
else:
    sentry_sdk.init(os.environ["SENTRY_DSN"])


SETTINGS_PATH = Path.home() / ".config" / "purplebot" / "settings.json"


logger = logging.getLogger(__name__)

intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)


@client.event
async def on_ready():
    logger.info("Logged in as %s %s", client.user.name, client.user.id)


@dispatch.register("^!test")
async def test(client, command, message):
    counter = 0
    tmp = await client.send_message(message.channel, "Calculating messages...")
    async for log in client.logs_from(message.channel, limit=100):
        if log.author == message.author:
            counter += 1

    await client.edit_message(tmp, "You have {} messages.".format(counter))


@dispatch.register("^!sleep")
async def sleep(client, command, message):
    await asyncio.sleep(5)
    await client.send_message(message.channel, "Done sleeping")


@client.event
async def on_message(message: Message):
    await dispatch.handle(client, message)


def main():
    import purplebot.plugins.gameday  # NOQA
    import purplebot.plugins.quotes  # NOQA

    with SETTINGS_PATH.open() as fp:
        settings = json.load(fp)
    client.settings = settings
    client.run(settings["discord"])
