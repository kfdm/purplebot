__purple__ = __name__

import requests
import random

from purplebot.decorators import threaded, ratelimit

@threaded
@ratelimit('QuotePlugin::ratelimit', 60)
def get_quote(bot, hostmask, line):
    dest = line[2] if line[2][0:1] == '#' else hostmask['nick']

    if len(line) == 5:
        response = requests.get('http://localhost:8000/quotes/', params={
            'search': line[4]
        })
        quote = random.choice(response.json())
    else:
        response = requests.get('http://localhost:8000/quotes/random/')
        quote = response.json()

    try:
        bot.irc_privmsg(dest, '{created} {body}'.format(**quote))
    except KeyError:
        bot.irc_privmsg(dest, 'Error reading quote')
get_quote.command = '.quote'
get_quote.example = '.quote [#]'
