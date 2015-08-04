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
        head = session.head(url, allow_redirects=True)

        if 'text/html' not in head.headers.get('content-type'):
            logger.debug('URL is not html')
            continue

        # Get the actual page with the now possibly redirected URL
        result = session.get(head.url)
        if '<title>' not in result.text:
            logger.debug('Unable to find title')
            continue

        # If there is no encoding set, then lets force it to decode as utf8
        if result.encoding is None or result.encoding == 'ISO-8859-1':
            result.encoding = 'utf-8'

        soup = bs4.BeautifulSoup(result.text, "lxml")
        bot.irc_privmsg(line.dest, 'LC: ' + WHITESPACE.sub(' ', soup.title.string))

check_urls.event = 'privmsg'
