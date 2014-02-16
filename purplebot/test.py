import logging
import sys
from purplebot.bot import bot
from purplebot.cli.console import LOG_FORMAT

colors = {
	logging.WARNING: "\033[1;31m%s\033[1;m",
	logging.ERROR: "\033[1;41m%s\033[1;m",
	logging.INFO: "\033[1;32m%s\033[1;m",
	logging.DEBUG: "\033[1;33m%s\033[1;m",
}

for k in colors:
	logging.addLevelName( k, colors[k] % logging.getLevelName(k))


class testbot(bot):
	"""Simple offline bot testing framework"""
	def connect(self, host, port, nick, ident, realname):
		self._host = host
		self._port = port
		self._nick = nick
		self._ident = ident
		self._realname = realname
		self.event('CONNECT')

	def disconnect(self, quit=''):
		self._exit = True
		self.irc_quit(quit)
		if(self._logvar):
			self._logger.close()

	def irc_raw(self, message):
		print message.strip()

	def run(self, host, port, nick, ident, realname):
		pass

	def dump_events(self):
		"""Dump the events list to the screen"""
		print self._irc__events

	def parse_file(self, irc_logfile):
		"""Simulate the bot by using a raw irc log"""
		self.connect('localhost', 6667, 'testbot', 'testbot', 'testbot')
		for line in open(irc_logfile):
			self._parse_line(line)

	def __str__(self):
		return self.__settings.__str__()


def main():
	logging.basicConfig(level=logging.DEBUG,format=LOG_FORMAT)

	test = testbot(debug=1)
	test.connect('localhost', 6667, 'testbot', 'testbot', 'testbot')
	for line in sys.stdin.readlines():
		test._parse_line(line.strip())


if __name__ == '__main__':
	main()
