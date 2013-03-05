import threading
import logging
import time

__all__ = ['threaded', 'ratelimit']

logger = logging.getLogger(__name__)

_timer = {}
_ratelimit = threading.Lock()

DEFAULT_TIMEOUT = 30


def ratelimit_expired(key, duration=None):
	'''Check to see if the rate limit has expired'''
	if(duration is None):
		duration = DEFAULT_TIMEOUT

	now = int(time.time())
	then = _timer.get(key)

	# If there is no timer set yet, then we set a timer and treat and assume
	# it has not hit the rate limit
	if then is None:
		_timer[key] = now
		return True
	# If the difference between now and then is less than our timeout then
	# we have not hit the rate limit
	elif (now - then) > duration:
		_timer[key] = now
		return True
	# Otherwise, let the calling function know how long is left
	else:
		return duration - (now - then)


def threaded(func):
	'''Run a bot sub command in a thread'''
	def wrapped(*args, **kwargs):
		logger.debug('Running in a thread: %s.%s', func.__module__, func.__name__)
		threading.Thread(target=func, args=args, kwargs=kwargs).start()
	wrapped.__name__ = func.__name__
	wrapped.__module__ = func.__module__
	return wrapped


def _time_to_words(value):
	if value >= 60:
		return '%d minutes' % (value / 60)
	return '%d seconds' % value


def ratelimit(key, value, alert=True):
	'''Enforce a rate limit for bot commands

	:params string key: Rate limit key to check against
	:params int value: Rate limit timeout
	:params boolean alert: Send a NOTICE to users who have hit the rate limit
	'''
	def wrap(func):
		def wrapped(bot, hostmask, line, *args, **kwargs):
			key = func.__module__ + '.' + func.__name__
			timeout = bot.settings.get(key, value)

			logger.debug('Checking rate limit: %s', key)

			expired = ratelimit_expired(key, timeout)
			if expired is True:
				return func(bot, hostmask, line, *args, **kwargs)
			elif hostmask is not None and alert is True:
				bot.irc_notice(hostmask['nick'], 'Please wait %s before using that command again' % _time_to_words(expired))

		wrapped.__name__ = func.__name__
		wrapped.__module__ = func.__module__
		return wrapped
	return wrap
