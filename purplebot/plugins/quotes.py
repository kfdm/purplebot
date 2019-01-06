from purplebot import session
from purplebot.dispatch import dispatch
import random
import logging


LOGGER = logging.getLogger(__name__)


_RECENT_QUOTES = []


@dispatch.register("^.quote( (?P<search>.*))?")
async def quote(client, match, message):
    args = match.groupdict()
    if "search" in args:
        response = session.get("https://tsundere.co/api/quotes", params=args)
        try:
            quotes = response.json().get("results")
            while quotes:
                quote = random.choice(quotes)
                if quote["id"] in _RECENT_QUOTES:
                    quotes.remove(quote)
                    LOGGER.debug("Seen %s recently", quote["id"])
                    continue
                break
            quote["extra"] = "(Found %s) " % response.json().get("count")
        except IndexError:
            return await client.send_message(
                message.channel, "No quote found for {search}".format(**args)
            )
    else:
        response = session.get("https://tsundere.co/api/quotes/random")
        quote = response.json()
        quote["extra"] = ""

    await client.send_message(message.channel, "{created} {body}".format(**quote))
