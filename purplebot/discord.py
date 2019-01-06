import json
import logging
from pathlib import Path

import asyncio
import discord
from purplebot.dispatch import dispatch


logging.basicConfig(level=logging.INFO)

SETTINGS_PATH = Path.home() / ".config" / "purplebot" / "settings.json"

client = discord.Client()
logger = logging.getLogger(__name__)


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")


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
async def on_message(message):
    await dispatch.handle(client, message.content, message)


def main():
    import purplebot.plugins.quotes
    import purplebot.plugins.gameday
    with SETTINGS_PATH.open() as fp:
        settings = json.load(fp)
    client.settings = settings
    client.run(settings["discord"])
