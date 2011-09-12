"""Basic IRC Bot"""
import os
import string
import re
import time
import imp
import threading
import signal
import logging

from purplebot.irc import irc
from purplebot.settings.jsonsettings import Settings

class BotError(Exception):
	def __init__(self,message):
		self.message = message
	def __str__(self):
		return self.message
class PluginError(BotError):
	pass
class CommandError(BotError):
	pass
class CommandDisabledError(BotError):
	pass

class BotThread(threading.Thread):
	def __init__(self, bot, nick, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
		threading.Thread.__init__(self,group,target,name,args,kwargs,verbose)
		self.bot = bot
		self.nick = nick
	def run(self):
		try:
			if self._Thread__target:
				self._Thread__target(*self._Thread__args, **self._Thread__kwargs)
		except CommandError,e:
			logging.getLogger(__name__).exception('Command Error')
			self.bot.irc_notice(self.nick,'CommandError: %s'%e)
			raise
		except PluginError,e:
			logging.getLogger(__name__).exception('Plugin Error')
			self.bot.irc_notice(self.nick,'PluginError: %s'%e)
			raise
		except Exception, e:
			logging.getLogger(__name__).exception('Unknown Exception')
			self.bot.irc_notice(self.nick,'Unknown Exception')
			raise

class bot(irc):
	settings = Settings()
	
	"""Mostly simple IRC Bot framework"""
	def __init__ (self,debug=0):
		irc.__init__(self, debug)
		self.__logger = logging.getLogger(__name__)
		
		self.__plugins = {}
		self.__commands = {}
		self.__blocks = []
		self.__timer = {}
		
		#Register command handler on privmsg event queue
		self.event_register('PRIVMSG',self.__parse_commands)
		
		self.plugindir = os.path.realpath(os.path.join(os.path.dirname(__file__),'../plugins'))
		
		#Register some internal commands
		self.plugin_register('core')
		
		self.settings.load()
		
		self.block_rebuild()
		
		signal.signal(signal.SIGUSR1,self.__reload_plugins)
		
	def __reload_plugins(self,signum,sigframe):
		self.__logger.info('Bot recieved signal %s',signum)
		self.__logger.info('Reloading Plugins')
		for plugin in self.__plugins:
			plugin = plugin.replace('_','.')
			self.__logger.info('Reloading %s',plugin)
			self.plugin_unregister(plugin)
			self.plugin_register(plugin)
	
	def __parse_commands(self,bot,line):
		'[":hostname(sender)","PRIVMSG","reciever(#channel or nick)",":*",*]'
		try:
			nick, host = self.parse_hostmask(line[0])
			if(nick == self._nick):
				return # Bot doesn't need to parse it's own messages
			if self.block_check(line[0]):
				return # Ignore messages from blocked users
			line[3] = string.lstrip(line[3],':')
			
			if line[3] in self.__commands.keys():
				cmd = self.__commands[line[3]]
				if hasattr(cmd,'alias'):
					self.__logger.info('Alias command %s => %s',line[3],cmd.alias)
					if not cmd.alias in self.__commands.keys():
						raise CommandError('Invalid Alias')
					cmd = self.__commands[cmd.alias]
					
				if hasattr(cmd,'disabled') and cmd.disabled == True:
					self.__logger.debug('%s has been disabled',cmd.command)
					return
				if hasattr(cmd,'owner'):
					if host != self.settings.get('Core::Owner',None):
						raise CommandError('Command requires Owner')
				if hasattr(cmd,'admin'):
					if not self.admin_check({'nick':nick,'host':host}):
						raise CommandError('Command requires Admin')
				if hasattr(cmd, 'thread') and cmd.thread == True:
					self.__logger.debug('Running %s in a thread',cmd.__name__)
					BotThread(self,nick,target=cmd, args=(self,{'nick':nick,'host':host},line)).start()
				else:
					cmd(self,{'nick':nick,'host':host},line)
		except CommandError,e:
			self.__logger.exception('CommandError')
			self.irc_notice(nick,e.__str__())
		except Exception,e:
			self.__logger.exception('Error processing commands\n%s',line)
			self.irc_notice(nick,'There was an error processing that command')
			if self._debugvar >= 2: raise
	def parse_hostmask(self,hostmask):
		"""Parse a hostmask into the nick and hostmask parts
		
		@param hostmask:
		"""
		tmp = hostmask.lstrip(':').split('!')
		self.__logger.debug("--hostmask--(%s)(%s)(%s)",hostmask,tmp[0],tmp[1])
		return tmp[0],tmp[1]
	
	def block_add(self,str):
		"""Add name to the blocklist"""
		if str in self.__settings['Core::Blocks']:
			return
		self.__settings['Core::Blocks'].append(str)
		self.block_rebuild()
		self.settings.save()
	def block_remove(self,str):
		"""Remove name from the block list"""
		if str in self.__settings['Core::Blocks']:
			self.__settings['Core::Blocks'].remove(str)
			self.block_rebuild()
			self.settings.save()
	def block_check(self,str):
		for block in self.__blocks:
			#self.__logger.debug('Checking: %s'%block)
			if block.search(str):
				#self.__logger.debug('Blocking: %s'%block)
				return True
		return False
	def block_rebuild(self):
		self.__blocks = []
		for block in self.settings.get('Core::Blocks',[]):
			self.__logger.debug('Compiling %s'%block)
			block = block.replace('*','.*')
			self.__blocks.append( re.compile(block) )
	
	def admin_add(self,str):
		self.settings.append('Core::Admins',str)
		self.settings.save()
	def admin_remove(self,str):
		self.settings.remove('Core::Admins',str)
	def admin_check(self,hostmask):
		nick,host = hostmask['nick'],hostmask['host']
		if host == self.settings.get('Core::Owner',None):
			return True
		if host in self.settings.get('Core::Admins',[]):
			return True
		return False
	def alias_add(self,alias,command):
		if alias in self.__commands.keys():
			raise BotError('Alias cannot overwrite existing object')
		def alias_func(): pass
		alias_func.alias = command
		self.__commands[alias] = alias_func
	def alias_remove(self,alias):
		if not alias in self.__commands.keys():
			raise BotError('Invalid alias name')
		cmd = self.__commands[alias]
		if not hasattr(cmd,'alias'):
			raise BotError('Invalid alias')
		self.__commands.pop(alias)
		
	def plugin_register(self,module):
		"""Register a new plugin
		
		:param module: Module name in dot format. Ex my.plugin
		:type module: str
		"""
		if module in self.__plugins.keys():
			return True
		
		path	= module.replace('.','/')+'.py'
		module	= module.replace('.','_')
		path = os.path.join(self.plugindir,path)
		try:
			mod = imp.load_source(module,path)
		except Exception,e:
			self.__logger.exception( 'Error loading plugin %s',path)
			if self._debugvar >= 2: raise
			return False
		else:
			self.__plugins[module] = mod
			for name,obj in vars(mod).iteritems():
				if name == 'load':
					self.__logger.info('Running %s plugin load event',module)
					obj(self)
				if hasattr(obj,'command'):
					self.__logger.info('Loading command: %s',obj.command)
					self.__commands[obj.command] = obj
				if hasattr(obj,'event'):
					self.__logger.info('Loading %s event: %s',obj.event,name)
					self.event_register(obj.event,obj)
		
	def plugin_unregister(self,module):
		"""Unregister a plugin
		
		:param module: Module name in dot format. Ex my.plugin
		:type module: str
		"""
		module	= module.replace('.','_')
		if not module in self.__plugins.keys():
			return False
		try:
			mod = self.__plugins[module]
		except Exception,e:
			self.__logger.debug( 'Error unloading plugin %s',module)
			if self._debugvar >= 2: raise
			return False
		else:
			for name,obj in vars(mod).iteritems():
				if name == 'unload':
					self.__logger.debug('Running %s plugin unload event',module)
					obj(self)
				if hasattr(obj,'command'):
					self.__logger.debug('Unloading command: %s',obj.command)
					self.__commands.pop(obj.command)
				if hasattr(obj,'event'):
					self.__logger.debug('Unloading %s event: %s',obj.event,name)
					self.event_unregister(obj.event,obj)
			self.__plugins.pop(module)
	def __cmd_version(self,bot,hostmask,line):
		bot.irc_ctcp_reply(line, '1.1')
	
	def kill(self):
		for p in self.__plugins.keys():
			self.plugin_unregister(p)
		self.event_unregister('PRIVMSG',self.__parse_commands)
		self.running = False
	
	def command_help(self,cmd):
		if cmd in self.__commands.keys():
			if hasattr(self.__commands[cmd], 'example'):
				return self.__commands[cmd].example
			else:
				return 'No help for that command'
		else:
			return 'Invalid Command'
	
	def plugin_list(self):
		"""Return a list of currently loaded plugins"""
		return self.__plugins.keys()
	
	def command_enable(self,cmd):
		if cmd in self.__commands.keys():
			self.__logger.info('Enable command %s',cmd)
			cmd = self.__commands[cmd]
			cmd.disabled = False
	
	def command_disable(self,cmd):
		if cmd in self.__commands.keys():
			self.__logger.info('Disable command %s',cmd)
			cmd = self.__commands[cmd]
			cmd.disabled = True
	
	def timer(self,name,value=None):
		if(value==None):
			value = 30
		tmp = self.__timer.get(name,False)
		if tmp != False:
			now = int(time.time())
			if (now - tmp) > value:
				self.__timer[name] = now
				return True
			else:
				return value - (now - tmp)
		self.__timer[name] = int(time.time())
		return True
	
	__ratelimit = threading.Lock()
	def ratelimit(self,key,timeout,nick=None):
		self.__ratelimit.acquire()
		timeout = self.timer(key,timeout)
		self.__ratelimit.release()
		
		if timeout == True: return False
		if nick != None:
			if timeout > 60:
				self.irc_notice(nick, 'Please wait %d minutes before using that command again'%(timeout/60))
			else:
				self.irc_notice(nick, 'Please wait %d seconds before using that command again'%timeout)
		return True
	
	def timedelay(self,time,func,args):
		threading.Timer(time,func,args).start()
	
	def __str__(self):
		return '%s'%(self.settings)
