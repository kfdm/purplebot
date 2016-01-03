import logging
import threading
import time

from purplebot.errors import CommandError
from purplebot.util import parse_hostmask

__all__ = ['threaded', 'ratelimit', 'require_admin', 'require_owner']

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

	# Copy of threading.Thread.run so that we can log exceptions
	class Thread(threading.Thread):
		def run(self):
			try:
				if self._target:
					self._target(*self._args, **self._kwargs)
			except:
				logger.exception(
					'Uncaught Exception %s.%s',
					func.__module__,
					func.__name__
				)
			finally:
				del self._target, self._args, self._kwargs

	def wrapped(*args, **kwargs):
		logger.debug('Running in a thread: %s.%s', func.__module__, func.__name__)
		Thread(target=func, args=args, kwargs=kwargs).start()
	wrapped.__name__ = func.__name__
	wrapped.__module__ = func.__module__
	wrapped.__doc__ = func.__doc__
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


def require_admin(func):
	def wrapped(bot, hostmask, line, *args, **kwargs):
		if hostmask['host'] == bot.settings.get('Core::Owner', None):
			return func(bot, hostmask, line, *args, **kwargs)
		if hostmask['host'] in bot.settings.get('Core::Admins', []):
			return func(bot, hostmask, line, *args, **kwargs)
		raise CommandError('Command requires Admin')
	wrapped.__name__ = func.__name__
	wrapped.__module__ = func.__module__
	return wrapped


def require_owner(func):
	def wrapped(bot, hostmask, line, *args, **kwargs):
		if hostmask['host'] == bot.settings.get('Core::Owner', None):
			return func(bot, hostmask, line, *args, **kwargs)
		raise CommandError('Command requires Owner')
	wrapped.__name__ = func.__name__
	wrapped.__module__ = func.__module__
	return wrapped


def ignore_self(func):
	def wrapped(self, bot, line):
		nick, host = parse_hostmask(line[0])
		if(nick == bot._nick):
			logger.debug('Ignoring self')
			return  # Bot doesn't need to parse it's own messages
		return func(self, bot, line)
	wrapped.__name__ = func.__name__
	wrapped.__module__ = func.__module__
	wrapped.__doc__ == func.__doc__
	return wrapped
