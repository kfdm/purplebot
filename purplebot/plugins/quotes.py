__purple__ = __name__

import requests
import random

from purplebot import USER_AGENT
from purplebot.decorators import threaded, ratelimit

URL_SUBMIT = 'http://localhost:8000/quotes/'
URL_RANDOM = 'http://localhost:8000/quotes/random/'


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
            quote = random.choice(response.json().get('results'))
        except IndexError:
            bot.irc_notice(hostmask['nick'], 'No quote found for %s' % line[4])
            return
    else:
        response = requests.get(
            bot.settings.get('QuotePlugin::random', URL_RANDOM),
            headers={'user-agent': USER_AGENT}
        )
        quote = response.json()

    try:
        bot.irc_privmsg(dest, '{created} {body}'.format(**quote))
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
