import requests

__purple__ = __name__


def healthcheck(bot, line):
    response = requests.get(bot.settings.get('HealthCheck::url'))
    response.raise_for_status()
healthcheck.event = 'ping'
