import logging
import re

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

    async def handle(self, client, command, event):
        logger.info("parsing command: %s %s", command, event)
        for cmd in self.mapping:
            match = cmd["re"].match(command)
            if match:
                try:
                    return await cmd["func"](client, match, event)
                except CommandError as e:
                    pass


dispatch = Dispatch()
