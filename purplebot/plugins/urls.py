__purple__ = __name__

import logging
import re

import bs4
import requests
from purplebot.decorators import threaded

logger = logging.getLogger(__name__)


# From https://gist.github.com/uogbuji/705383
GRUBER_URLINTEXT_PAT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
WHITESPACE = re.compile('\s+')


@threaded
def check_urls(bot, line):
    for match in GRUBER_URLINTEXT_PAT.finditer(line._text):
        url = match.group()
        session = requests.Session()
        logger.debug('Found URL: %s', url)
        head = session.head(url)

        if 'text/html' not in head.headers.get('content-type'):
            logger.debug('URL is not html')
            continue

        result = session.get(url)
        if '<title>' not in result.text:
            logger.debug('Unable to find title')
            continue

        soup = bs4.BeautifulSoup(result.text, "lxml")
        bot.irc_privmsg(line.dest, 'LC: ' + WHITESPACE.sub(' ', soup.title.string))

check_urls.event = 'privmsg'
