import datetime
import logging
import random

import arrow
import vobject
from purplebot import session
from purplebot.dispatch import dispatch

LOGGER = logging.getLogger(__name__)


_RECENT_QUOTES = []


MESSAGE = """
{summary} > {diff}
UTC: {utc}
Japan: {jst}
Eastern: {est}
Central: {cst}
"""


@dispatch.register("^.gamenight")
async def gamenight(client, match, message):
    today = datetime.datetime.now(datetime.timezone.utc)
    nextevent = None

    response = session.get(client.settings["gameday"])
    calendar = vobject.readOne(response.text)
    for event in calendar.components():
        # Ignore older events
        try:
            if event.dtstart.value < today:
                continue
        except TypeError:
            # Lazy way to filter out all day events
            continue

        # If the current event is older than our next event, skip
        if nextevent and event.dtstart.value > nextevent.dtstart.value:
            continue
        nextevent = event

    if nextevent:
        remaining = nextevent.dtstart.value - today
        utc_dt = arrow.get(nextevent.dtstart.value)

        await client.send_message(
            message.channel,
            MESSAGE.format(
                summary=nextevent.summary.value,
                diff=remaining,
                utc=utc_dt,
                cst=utc_dt.to("America/Chicago"),
                jst=utc_dt.to("Asia/Tokyo"),
                est=utc_dt.to("America/New_York"),
            ),
        )
