import logging
import re

from discord import Message

from purplebot.exceptions import CommandError

logger = logging.getLogger(__name__)


class Dispatch:
    def __init__(self):
        self.mapping = []

    def register(self, key, help=""):
        def wrapping(func):
            logger.info("Registering [%s] %s", key, func)
            self.mapping.append(
                {"key": key, "re": re.compile(key), "func": func, "help": help}
            )

        return wrapping

    async def handle(self, client, message: Message):
        logger.info("parsing command from: %s", message)
        for cmd in self.mapping:
            match = cmd["re"].match(message.content)
            if match:
                logger.info("Found match %s", match)
                try:
                    return await cmd["func"](client, match, message)
                except CommandError as e:
                    pass


dispatch = Dispatch()
