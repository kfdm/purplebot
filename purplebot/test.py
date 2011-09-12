from bot import bot
import sys,string
class testbot(bot):
	def connect(self,host,port,nick,ident,realname):
		self._host = host
		self._port = port
		self._nick = nick
		self._ident = ident
		self._realname = realname
		
		#self.irc_nick(self._nick)
		#self.irc_user(self._ident, self._host, self._realname)
		
		#for event in self._events_connect:
		#	event(self)
	def disconnect(self,quit=''):
		self._exit = True
		self.irc_quit(quit)
		if(self._logvar):
			self._logger.close()
	def irc_raw(self,message):
		print message.strip()
		self.log('<< %s'%message)
	def run(self):
		pass
