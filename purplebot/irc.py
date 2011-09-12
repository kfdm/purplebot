import string
import time
import ircsocket
import signal
import logging

class irc(object):
	"""Core IRC methods"""
	def __init__ (self,debug=1):
		"""Initialize the bot
		:param debug: debug level
		"""
		self.buffer = ''
		
		self.running		= True
		self.connected		= False
		self._exit 			= False
		self._debugvar 		= debug
		self.__logger		= logging.getLogger(__name__)
		self.__log_in		= logging.getLogger('irc.in')
		self.__log_out		= logging.getLogger('irc.out')
		self._channels 		= []
		self._readbuffer	= ""
		self._last_msg		= time.time()
		
		self.__events		= {}
		self.event_register('timer',self.__irc_timeout)
		
		signal.signal(signal.SIGINT, self.__sig_term)
		signal.signal(signal.SIGTERM,self.__sig_term)
	
	def __sig_term(self,signum,sigframe):
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
		
		self._socket = ircsocket.ircsocket()
		self._socket.connect(host,port)
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
	_parse_events = [
		'PRIVMSG',
		'NOTICE',
		'JOIN',
		'PART',
		'PONG',
		'MODE',
		'NICK',
	]
	def _parse_line(self,line):
		"""Parse an incoming message from the irc server"""
		self.__log_in.debug(line)
		message=string.rstrip(line).split(' ',4)
		try:
			if message[1] in self._parse_events:
				self.event(message[1],message)
			elif(message[1]=="PONG"):
				self.irc_ping(message[2])
			else:
				if(message[0]=="PING"):
					self.irc_pong(message[1])
					if not self.connected:
						self.connected = True
						self.event('CONNECT')
				elif(message[0]=="ERROR"):
					message = ' '.join(message)
					self.__logger.error("---Error--- "+message)
					self._socket.close()
					self.running = False
				else:
					message = ' '.join(message)
					self.__logger.warning("--Unknown message-- "+message)
		except Exception,e:
			self.__logger.warning('Error parsing line: %s'%line)
			if self._debugvar >= 2:
				self.running = False
				raise
	
	###########################################################################
	# Event Functions
	###########################################################################
	def event(self,event_name,*args):
		'''Run events on named queue
		:param event_name: Examples PRIVMSG, CONNECT, JOIN
		:type event_name: str
		:param param: Parameters to send to the registered functions. Varies from
		event to event
		'''
		if event_name in self.__events:
			for event in self.__events[event_name]:
				logging.getLogger('events').info('%s|%s',event_name,*args)
				event(self,*args)
	def event_register(self,event_name,function):
		"""Register a new event
		:param event_name: Examples PRIVMSG, CONNECT, JOIN
		:type event_name: str
		:param function: function to be called. Order is not guarenteed
		:type function: func
		"""
		event_name = event_name.upper()
		if not event_name in self.__events:
			self.__events[event_name] = []
		self.__events[event_name].append(function)
	def event_unregister(self,event_name,function):
		"""Unregister an event
		
		:param event_name: Examples PRIVMSG, CONNECT, JOIN
		:type event_name: str
		:param function: function to be unregistered
		:type function: func
		"""
		event_name = event_name.upper()
		if event_name in self.__events:
			self.__events[event_name].remove(function)
			if len(self.__events[event_name]) == 0:
				self.__events.pop(event_name)
			
	def __irc_timeout(self,bot,time):
		if time - self._last_msg > self.__TIMEOUT:
			self.disconnect('Irc timed out')
	
	###########################################################################
	# IRC Functions
	###########################################################################
	def irc_raw(self,message):
		"""Send a raw IRC message as is"""
		self._socket.write(message.encode('utf-8'))
		self.__log_out.debug(message.encode('utf-8').strip())
	def irc_nick(self,nick):
		"""Change nick"""
		self.irc_raw("NICK %s\r\n" % nick)
	def irc_part(self,channel):
		"""Part channel"""
		self.irc_raw("PART :%s\r\n" % channel)
	def irc_notice(self,dest,message):
		"""Send a notice to a user or channel"""
		self.irc_raw("NOTICE %s :%s\r\n" % (dest, message))
	def irc_user(self,ident,host,realname):
		self.irc_raw("USER %s %s bla :%s\r\n" % (ident,host,realname))
	def irc_pong(self,response):
		"""Send a response pong"""
		self.irc_raw("PONG %s\r\n" % response)
	def irc_privmsg(self,dest,msg):
		"""Send a PRIVMSG to a user or channel"""
		self.irc_raw("PRIVMSG %s :%s\r\n" % (dest, msg))
	def irc_quit(self,quit=""):
		"""Quit IRC"""
		self.irc_raw("QUIT %s\r\n" % quit)
	def irc_ping(self,test):
		"""Send a ping message to the server"""
		self.irc_raw("PING %s\r\n" % test)
	def irc_join(self,channel):
		"""Join an IRC channel"""
		self.irc_raw("JOIN %s\r\n" % channel)
	def irc_mode(self,target,modes):
		"""Set modes on a target user or channel"""
		self.irc_raw('MODE %s %s\r\n'%(target,modes))
	def irc_ctcp_reply(self,dest,msg):
		"""Send a ctcp reply message"""
		self.irc_notice(dest, '\x01%s\x01'%msg)
	def irc_ctcp_send(self,dest,msg):
		"""Send a ctcp message"""
		self.irc_privmsg(dest, '\x01%s\x01'%msg)
