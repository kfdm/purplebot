from purplebot import session
from purplebot.dispatch import dispatch
import datetime
import random
import logging
import vobject
from pytz import timezone


LOGGER = logging.getLogger(__name__)


_RECENT_QUOTES = []


MESSAGE = """
Next game day: {summary}
UTC: {utc}
JST: {jst}
EST: {est}
CST: {cst}
"""


@dispatch.register("^.gamenight")
async def gamenight(client, match, message):
    today = datetime.datetime.now(datetime.timezone.utc)
    nextevent = None

    response = session.get(client.settings["gameday"])
    calendar = vobject.readOne(response.text)
    for event in calendar.components():
        # Ignore older events
        if event.dtstart.value < today:
            continue
        print(event)
        # If the current event is older than our next event, skip
        if nextevent and event.dtstart.value > nextevent.dtstart.value:
            continue
        nextevent = event

    if nextevent:
        await client.send_message(
            message.channel,
            MESSAGE.format(
                summary=nextevent.summary.value,
                utc=nextevent.dtstart.value,
                cst=nextevent.dtstart.value.astimezone(timezone("America/Chicago")),
                jst=nextevent.dtstart.value.astimezone(timezone("Asia/Tokyo")),
                est=nextevent.dtstart.value.astimezone(timezone("America/New_York")),
            ),
        )

