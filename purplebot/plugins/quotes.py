__purple__ = __name__

import datetime
import logging
import random

import requests

from purplebot import USER_AGENT
from purplebot.decorators import ratelimit, threaded

URL_SUBMIT = 'http://localhost:8000/quotes/'
URL_RANDOM = 'http://localhost:8000/quotes/random/'

LAST_MESSAGE = datetime.datetime.utcnow()
LOGGER = logging.getLogger(__name__)
# Wait 3 hours between pings
WAIT_TIME = 3 * 60 * 60

_RECENT_QUOTES = []


def reset_timer(self, line):
    '''Reset the timer for the bot'''
    LAST_MESSAGE = datetime.datetime.utcnow()
    LOGGER.debug('Resetting timer %s', LAST_MESSAGE)
reset_timer.event = 'privmsg'

def check_ping(self, message):
    now = datetime.datetime.utcnow()
    if (now - LAST_MESSAGE).total_seconds() < WAIT_TIME:
        return
check_ping.event = 'ping'


@threaded
@ratelimit('QuotePlugin::ratelimit', 60)
def get_quote(bot, hostmask, line):
    dest = line[2] if line[2][0:1] == '#' else hostmask['nick']

    if len(line) == 5:
        response = requests.get(
            bot.settings.get('QuotePlugin::submit', URL_SUBMIT),
            params={'search': line[4]},
            headers={'user-agent': USER_AGENT}
        )
        try:
            quotes = response.json().get('results')
            while quotes:
                quote = random.choice(quotes)
                if quote['id'] in _RECENT_QUOTES:
                    quotes.remove(quote)
                    LOGGER.debug('Seen %s recently', quote['id'])
                    continue
                break
            quote['extra'] = '(Found %s) ' % response.json().get('count')
        except IndexError:
            bot.irc_notice(hostmask['nick'], 'No quote found for %s' % line[4])
            return
    else:
        response = requests.get(
            bot.settings.get('QuotePlugin::random', URL_RANDOM),
            headers={'user-agent': USER_AGENT}
        )
        quote = response.json()
        quote['extra'] = ''

    LOGGER.debug('Appending quote %s to recently seen', quote['id'])
    _RECENT_QUOTES.append(quote['id'])
    if len(_RECENT_QUOTES) > 10:
        _RECENT_QUOTES.pop(0)

    try:
        quote['created'] = quote['created'].split('T')[0]
        bot.irc_privmsg(dest, '{extra}{created} {body}'.format(**quote))
    except KeyError:
        bot.irc_notice(hostmask['nick'], 'Error reading quote')
get_quote.command = '.quote'
get_quote.example = '.quote [#]'


@threaded
def add_quote(bot, hostmask, line):
    try:
        response = requests.post(
            bot.settings.get('QuotePlugin::submit', URL_SUBMIT),
            data={'body': line[4]},
            auth=(bot.settings.get('Misc::rpcuser'), bot.settings.get('Misc::rpcpass')),
            headers={'user-agent': USER_AGENT}
        )
        response.raise_for_status()
    except:
        bot.irc_notice(hostmask['nick'], 'Error adding quote')
    else:
        bot.irc_notice(hostmask['nick'], 'Quote Added')
add_quote.command = '.addquote'
