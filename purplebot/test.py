import logging
from purplebot.bot import bot

logging.basicConfig(level=logging.ERROR)

class testbot(bot):
	"""Simple offline bot testing framework"""
	def connect(self,host,port,nick,ident,realname):
		self._host = host
		self._port = port
		self._nick = nick
		self._ident = ident
		self._realname = realname
		
		self.event('CONNECT')
	def disconnect(self,quit=''):
		self._exit = True
		self.irc_quit(quit)
		if(self._logvar):
			self._logger.close()
	def irc_raw(self,message):
		print message.strip()
	def run(self):
		pass
	def dump_events(self):
		"""Dump the events list to the screen"""
		print self._irc__events
	def parse_file(self,irc_logfile):
		"""Simulate the bot by using a raw irc log"""
		self.connect('localhost',6667,'testbot','testbot','testbot')
		for line in open(irc_logfile):
			self._parse_line(line)
	def __str__(self):
		return self.__settings.__str__()
