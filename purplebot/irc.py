import logging
import signal
import string
import time

from purplebot.event import EventDelegate
from purplebot.ircsocket import ircsocket
from purplebot.util import parse_hostmask

__all__ = ['irc']

logger = logging.getLogger(__name__)


class irc(object):
	"""Core IRC methods"""
	def __init__(self, debug=1):
		"""Initialize the bot
		:param debug: debug level
		"""
		self.running = True
		self.connected = False
		self._exit = False
		self._debugvar = debug
		self._last_msg = time.time()

		self.event = EventDelegate()
		self.event.register('timer', self.__irc_timeout)
		self.event.register('PING', self.__irc_ping)
		self.event.register('ERROR', self.__irc_error)

		signal.signal(signal.SIGINT, self.__sig_term)
		signal.signal(signal.SIGTERM, self.__sig_term)

	def __sig_term(self, signum, sigframe):
		logger.info('Bot recieved signal %s' % signum)
		logger.info('Exiting')
		self.running = False
		if self._socket:
			self._socket.close()

	def run(self, host, port, nick, ident, realname):
		self._host = host
		self._port = port
		self._nick = nick
		self._ident = ident
		self._realname = realname

		self._socket = ircsocket()
		self._socket.connect(host, port)
		self.irc_nick(self._nick)
		self.irc_user(self._ident, self._host, self._realname)
		while self.running:
			tmp = self._socket.read()
			if tmp:
				self._parse_line(tmp)
		self._socket.close()

	###########################################################################
	# Parsing Functions
	###########################################################################
	_parse_events = (
		'AUTH',
		'JOIN',
		'MODE',
		'NICK',
		'NOTICE',
		'PART',
		'PONG',
		'PRIVMSG',
		'QUIT',
		'TOPIC',
	)

	def _parse_line(self, line):
		class Line(object):
			def __init__(self, line):
				self._raw = line
				self._parts = string.rstrip(line).split(' ', 4)
				if self._parts[1] in ['PRIVMSG', 'NOTICE']:
					_, self._command, self._text = string.rstrip(line).split(':', 2)

			def __getitem__(self, key):
				return self._parts[key]

			def __len__(self):
				# Shim for len(line)
				return len(self._parts)

			@property
			def dest(self):
				if self._parts[2][0:1] == '#':
					return self._parts[2]
				else:
					nick, host = parse_hostmask(self._parts[0])
					return nick

			def hostmask(self):
				# This should only be run for PRIVMSG/NOTICE but for now
				# I'll leave it without extra checks
				return parse_hostmask(self._line[0])

		"""Parse an incoming message from the irc server"""
		parts = Line(line)
		try:
			if parts[1] in self._parse_events:
				self.event(parts[1], self, parts)
			elif parts[0] in ("PING", "ERROR"):
				self.event(parts[0], self, parts)
			elif parts[1].isdigit():
				logger.debug('Server message: %s', line)
			else:
				logger.warning("Unknown message: %s", line)
		except Exception:
			logger.exception('Error parsing line: %s', line)

	def __irc_timeout(self, bot, time):
		if time - self._last_msg > self.__TIMEOUT:
			self.disconnect('Irc timed out')

	def __irc_ping(self, bot, message):
		self.irc_pong(message[1])
		if not self.connected:
			self.connected = True
			self.event('CONNECT', self)

	def __irc_error(self, bot, message):
		message = ' '.join(message)
		logger.error("---Error--- %s", ' '.join(message))
		self._socket.close()
		self.running = False

	###########################################################################
	# IRC Functions
	###########################################################################

	def irc_raw(self, message):
		"""Send a raw IRC message as is"""
		self._socket.write(message.encode('utf-8'))

	def irc_nick(self, nick):
		"""Change nick"""
		self.irc_raw("NICK %s\r\n" % nick)

	def irc_part(self, channel):
		"""Part channel"""
		self.irc_raw("PART :%s\r\n" % channel)

	def irc_notice(self, dest, message):
		"""Send a notice to a user or channel"""
		self.irc_raw("NOTICE %s :%s\r\n" % (dest, message))

	def irc_user(self, ident, host, realname):
		self.irc_raw("USER %s %s bla :%s\r\n" % (ident, host, realname))

	def irc_pong(self, response):
		"""Send a response pong"""
		self.irc_raw("PONG %s\r\n" % response)

	def irc_privmsg(self, dest, msg):
		"""Send a PRIVMSG to a user or channel"""
		self.irc_raw("PRIVMSG %s :%s\r\n" % (dest, msg))

	def irc_quit(self, quit=""):
		"""Quit IRC"""
		self.irc_raw("QUIT %s\r\n" % quit)

	def irc_ping(self, test):
		"""Send a ping message to the server"""
		self.irc_raw("PING %s\r\n" % test)

	def irc_join(self, channel):
		"""Join an IRC channel"""
		self.irc_raw("JOIN %s\r\n" % channel)

	def irc_mode(self, target, modes):
		"""Set modes on a target user or channel"""
		self.irc_raw('MODE %s %s\r\n' % (target, modes))

	def irc_ctcp_reply(self, dest, msg):
		"""Send a ctcp reply message"""
		self.irc_notice(dest, '\x01%s\x01' % msg)

	def irc_ctcp_send(self, dest, msg):
		"""Send a ctcp message"""
		self.irc_privmsg(dest, '\x01%s\x01' % msg)
