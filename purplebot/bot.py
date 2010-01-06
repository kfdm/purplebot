from irc import irc
import sys
import string
import pickle
import re
import types
import simplejson
import time
import imp
import threading

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
			self.bot.irc_notice(self.nick,'CommandError: %s'%e)
			raise
		except PluginError,e:
			self.bot.irc_notice(self.nick,'PluginError: %s'%e)
			raise
		except Exception, e:
			self.bot.irc_notice(self.nick,'Unknown Exception')
			raise

class bot(irc):
	def __init__ (self,debug=0):
		irc.__init__(self, debug)
		self.__plugins = {}
		self.__settings = {}
		self.__commands = {}
		self.__blocks = []
		self.__timer = {}
		
		#Register command handler on privmsg event queue
		self._events_privmsg.append( self.__parse_commands )
		
		#Register some internal commands
		self.plugin_register('core')
		
		self.settings_load()

		if not self.__settings.__contains__('Core::Admins'):
			self.__settings['Core::Admins'] = []
		if not self.__settings.__contains__('Core::Blocks'):
			self.__settings['Core::Blocks'] = []
		self.block_rebuild()
	
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
					print 'Alias command',line[3],'=>',cmd.alias
					if not cmd.alias in self.__commands.keys():
						raise CommandError('Invalid Alias')
					cmd = self.__commands[cmd.alias]
					
				if hasattr(cmd,'disabled') and cmd.disabled == True:
					self.debug( cmd.command + ' has been disabled')
					return
				if hasattr(cmd,'owner'):
					if host != self.__settings.get('Core::Owner',None):
						raise CommandError('Command requires Owner')
				if hasattr(cmd,'admin'):
					if not self.admin_check({'nick':nick,'host':host}):
						raise CommandError('Command requires Admin')
				if hasattr(cmd, 'thread') and cmd.thread == True:
					self.debug('Running '+cmd.__name__+' in a thread')
					BotThread(self,nick,target=cmd, args=(self,{'nick':nick,'host':host},line)).start()
				else:
					cmd(self,{'nick':nick,'host':host},line)
		except CommandError,e:
			self.irc_notice(nick,e.__str__())
		except Exception,e:
			self.debug('Error processing commands\n%s\n%s'%(line,e))
			self.irc_notice(nick,'There was an error processing that command')
			if self._debugvar >= 2: raise	
	def parse_hostmask(self,hostmask):
		tmp = hostmask.lstrip(':').split('!')
		self.debug("--hostmask--("+hostmask+")("+tmp[0]+")("+tmp[1]+")")
		return tmp[0],tmp[1]
	
	def block_add(self,str):
		if str in self.__settings['Core::Blocks']:
			return
		self.__settings['Core::Blocks'].append(str)
		self.block_rebuild()
		self.settings_save()
	def block_remove(self,str):
		if str in self.__settings['Core::Blocks']:
			self.__settings['Core::Blocks'].remove(str)
			self.block_rebuild()
			self.settings_save()
	def block_check(self,str):
		for block in self.__blocks:
			#self.debug('Checking: %s'%block)
			if block.search(str):
				#self.debug('Blocking: %s'%block)
				return True
		return False
	def block_rebuild(self):
		self.__blocks = []
		for block in self.__settings['Core::Blocks']:
			self.debug('Compiling %s'%block)
			block = block.replace('*','.*')
			self.__blocks.append( re.compile(block) )
	
	def admin_add(self,str):
		if str in self.__settings['Core::Admins']:
			return
		self.__settings['Core::Admins'].append(str)
		self.settings_save()
	def admin_remove(self,str):
		if str in self.__settings['Core::Admins']:
			self.__settings['Core::Admins'].remove(str)
			self.settings_save()
	def admin_check(self,hostmask):
		nick,host = hostmask['nick'],hostmask['host']
		if host == self.__settings.get('Core::Owner',None):
			return True
		if host in self.__settings['Core::Admins']:
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
		if module in self.__plugins.keys():
			return True
		try:
			file	= module.replace('.','/')
			module	= module.replace('.','_')
			print file,module
			mod = imp.load_source(module,'plugins/%s.py' % file)
		except Exception,e:
			self.debug( 'Error loading plugin %s\n%s' % (module,e) )
			if self._debugvar >= 2: raise
			return False
		else:
			self.__plugins[module] = mod
			for name,obj in vars(mod).iteritems():
				if name == 'load':
					self.debug('Running %s plugin load event'%module)
					obj(self)
				if hasattr(obj,'command'):
					self.debug('Loading command: '+obj.command)
					self.__commands[obj.command] = obj
				if hasattr(obj,'event'):
					self.debug('Loading %s event: %s'%(obj.event,name))
					if(obj.event=='privmsg'):
						self._events_privmsg.append(obj)
					elif(obj.event=='notice'):
						self._events_notice.append(obj)
					elif(obj.event=='join'):
						self._events_join.append(obj)
					elif(obj.event=='connect'):
						self._events_connect.append(obj)
					elif(obj.event=='nick'):
						self._events_nick.append(obj)
		
	def plugin_unregister(self,module):
		module	= module.replace('.','_')
		if not module in self.__plugins.keys():
			return False
		try:
			mod = self.__plugins[module]
		except Exception,e:
			self.debug( 'Error unloading plugin %s\n%s' % (module,e) )
			if self._debugvar >= 2: raise
			return False
		else:
			for name,obj in vars(mod).iteritems():
				if name == 'unload':
					self.debug('Running %s plugin unload event'%module)
					obj(self)
				if hasattr(obj,'command'):
					self.debug('Unloading command: '+obj.command)
					self.__commands.pop(obj.command)
				if hasattr(obj,'event'):
					self.debug('Unloading %s event: %s'%(obj.event,name))
					if(obj.event=='privmsg'):
						self._events_privmsg.remove(obj)
					elif(obj.event=='notice'):
						self._events_notice.remove(obj)
					elif(obj.event=='join'):
						self._events_join.remove(obj)
					#elif(obj.event=='connect'):
					#	self._events_connect.remove(obj)
			self.__plugins.pop(module)
	
	def setting_get(self,key,default=None,required=False):
		if key in ['Core::Admins','Core::Blocks','Core::Owner']: return
		setting = self.__settings.get(key,default)
		if required and setting is None:
			raise BotError('Missing required setting '+key)
		return setting
	def setting_set(self,key,value):
		if key in ['Core::Admins','Core::Blocks','Core::Owner']: return
		self.__settings[key] = value
	def settings_save(self):
		try:
			output = open('settings.js','wb')
			output.write(simplejson.dumps(self.__settings, sort_keys=True, indent=4))
			output.close()
		except:
			sys.stderr.write('Error writting settings!\n')
			if self._debugvar >= 2: raise
	def settings_load(self):
		try:
			input = open('settings.js','rb')
			self.__settings = simplejson.loads(input.read())
			input.close()
		except:
			sys.stderr.write('Error loading settings!\n')
			if self._debugvar >= 2: raise
	
	def __cmd_version(self,bot,hostmask,line):
		bot.irc_ctcp_reply(line, '1.1')
	
	def kill(self):
		for p in self.__plugins.keys():
			self.plugin_unregister(p)
		self._events_privmsg.remove(self.__parse_commands)
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
		return self.__plugins.keys()
	
	def command_enable(self,cmd):
		if cmd in self.__commands.keys():
			self.debug('Enable command' + cmd)
			cmd = self.__commands[cmd]
			cmd.disabled = False
	
	def command_disable(self,cmd):
		if cmd in self.__commands.keys():
			self.debug('Disable command' + cmd)
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
		return '%s'%(self.__settings)
