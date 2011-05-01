import string
import time
import ircsocket
import signal
import logging

class irc(object):
	def __init__ (self,debug=1,log=True):
		self.buffer = ''
		
		self.running		= True
		self.connected		= False
		self._exit 			= False
		self._debugvar 		= debug
		self._logvar 		= log
		self.__logger		= logging.getLogger('irc')
		self._channels 		= []
		self._readbuffer	= ""
		self._last_msg		= time.time()
		
		self._events_privmsg	= []
		self._events_notice		= []
		self._events_join		= []
		self._events_part		= []
		self._events_mode		= []
		self._events_connect	= []
		self._events_timer		= []
		self._events_nick		= []
		
		self._events_timer.append( self.__irc_timeout )
		
		signal.signal(signal.SIGINT, self._sig_term)
		signal.signal(signal.SIGTERM,self._sig_term)
	
	def _sig_term(self,signum,sigframe):
		self.__logger.info('Bot recieved signal %s'%signum)
		self.__logger.info('Exiting')
		self.running = False
		if self._socket: self._socket.close()
		
	def run(self,host,port,nick,ident,realname):
		self._host = host
		self._port = port
		self._nick = nick
		self._ident = ident
		self._realname = realname
		
		if(self._logvar):
			self._logger = open('%s.log'%(nick),'a')
		
		self._socket = ircsocket.ircsocket()
		self._socket.connect(host,port)
		self.irc_nick(self._nick)
		self.irc_user(self._ident, self._host, self._realname)
		while self.running:
			tmp = self._socket.read()
			if tmp:
				self.parse_line(tmp)
		self._socket.close()
	
	def log(self,msg):
		raise Exception('test')
	def debug(self,msg):
		raise Exception('test')
	
	###########################################################################
	# Parsing Functions
	###########################################################################
	def parse_line(self,line):
		message=string.rstrip(line).split(' ',4)
		try:
			if(message[1]=="PRIVMSG"):
				self.__logger.debug('>> %s'%line)
				self.__event_privmsg(message)
			elif(message[1]=="NOTICE"):
				self.__logger.debug('>> %s'%line)
				self.__event_notice(message)
			elif(message[1]=="JOIN"):
				self.__logger.debug('>> %s'%line)
				self.__event_join(message)
			elif(message[1]=="PART"):
				self.__logger.debug('>> %s'%line)
				self.__event_part(message)
			elif(message[1]=="PONG"):
				self.__logger.debug(message)
				self.irc_ping(message[2])
			elif(message[1]=="MODE"):
				self.__logger.debug('>> %s'%line)
				self.__event_mode(message)
			elif(message[1]=="NICK"):
				self.__logger.debug('>> %s'%line)
				self.__event_nick(message)
			else:
				if(message[0]=="PING"):
					self.__logger.debug('>> %s'%line)
					self.irc_pong(message[1])
					if not self.connected:
						self.connected = True
						for event in self._events_connect:
							self.__logger.debug('Connect Event:'+event.__name__)
							event(self)
				elif(message[0]=="ERROR"):
					self.__logger.debug('>> %s'%line)
					message = ' '.join(message)
					self.__logger.error("---Error--- "+message)
					self._socket.close()
					self.running = False
				else:
					self.__logger.debug('>> %s'%line)
					message = ' '.join(message)
					self.__logger.error("--Unknown message-- "+message)
		except Exception,e:
			self.__logger.warning('Error parsing line: %s'%line)
			if self._debugvar >= 2:
				self.running = False
				raise
			
	###########################################################################
	# Event Functions
	###########################################################################
	def __event_privmsg(self,line):
		for event in self._events_privmsg:
			event(self,line)
	def __event_notice(self,line):
		for event in self._events_notice:
			event(self,line)
	def __event_join(self,line):
		for event in self._events_join:
			event(self,line)
	def __event_part(self,line):
		for event in self._events_part:
			event(self,line)
	def __event_mode(self,line):
		for event in self._events_mode:
			event(self,line)
	def __event_nick(self,line):
		for event in self._events_nick:
			event(self,line)
	def __event_timer(self,time):
		self.__logger.info('Timer %s'%time)
		for event in self._events_timer:
			event(self,time)
			
	def __irc_timeout(self,bot,time):
		if time - self._last_msg > self.__TIMEOUT:
			self.disconnect('Irc timed out')
	
	###########################################################################
	# IRC Functions
	###########################################################################
	def irc_raw(self,message):
		#self.send(message)
		self._socket.write(message.encode('utf-8'))
		self.__logger.debug(('<< %s'%message.encode('utf-8')).strip())
	def irc_nick(self,nick):
		self.irc_raw("NICK %s\r\n" % nick)
	def irc_part(self,channel):
		self.irc_raw("PART :%s\r\n" % channel)
	def irc_notice(self,dest,message):
		self.irc_raw("NOTICE %s :%s\r\n" % (dest, message))
	def irc_user(self,ident,host,realname):
		self.irc_raw("USER %s %s bla :%s\r\n" % (ident,host,realname))
	def irc_pong(self,response):
		self.irc_raw("PONG %s\r\n" % response)
	def irc_privmsg(self,dest,msg):
		self.irc_raw("PRIVMSG %s :%s\r\n" % (dest, msg))
	def irc_quit(self,quit=""):
		self.irc_raw("QUIT %s\r\n" % quit)
	def irc_ping(self,test):
		self.irc_raw("PING %s\r\n" % test)
	def irc_join(self,channel):
		self.irc_raw("JOIN %s\r\n" % channel)
	def irc_mode(self,target,modes):
		self.irc_raw('MODE %s %s\r\n'%(target,modes))
	def irc_ctcp_reply(self,dest,msg):
		self.irc_notice(dest, '\x01%s\x01'%msg)
	def irc_ctcp_send(self,dest,msg):
		self.irc_privmsg(dest, '\x01%s\x01'%msg)