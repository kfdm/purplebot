"""Basic IRC Bot"""
import string
import threading
import signal
import logging

from purplebot.irc import irc
from purplebot.settings.jsonsettings import Settings
from purplebot.errors import *
from purplebot.util import BlockList, parse_hostmask

__all__ = ['bot']


class bot(irc):
	settings = Settings()

	"""Mostly simple IRC Bot framework"""
	def __init__(self, debug=0):
		irc.__init__(self, debug)
		self.__logger = logging.getLogger(__name__)

		self.__plugins = {}
		self.__commands = {}
		self.__timer = {}

		#Register command handler on privmsg event queue
		self.event_register('PRIVMSG', self.__parse_commands)

		#Register some internal commands
		self.plugin_register('purplebot.plugins.core')

		self.settings.load()
		self.block = BlockList(self.settings)

		signal.signal(signal.SIGUSR1, self.__reload_plugins)

	def __reload_plugins(self, signum, sigframe):
		self.__logger.info('Bot recieved signal %s', signum)
		self.__logger.info('Reloading Plugins')
		for plugin in self.__plugins:
			plugin = plugin.replace('_', '.')
			self.__logger.info('Reloading %s', plugin)
			self.plugin_unregister(plugin)
			self.plugin_register(plugin)

	def __parse_commands(self, bot, line):
		'[":hostname(sender)","PRIVMSG","reciever(#channel or nick)",":*",*]'
		try:
			nick, host = parse_hostmask(line[0])
			if(nick == self._nick):
				return  # Bot doesn't need to parse it's own messages
			if self.block.check(line[0]):
				return  # Ignore messages from blocked users
			line[3] = string.lstrip(line[3], ':')

			if line[3] in self.__commands.keys():
				cmd = self.__commands[line[3]]
				if hasattr(cmd, 'alias'):
					self.__logger.info('Alias command %s => %s', line[3], cmd.alias)
					if not cmd.alias in self.__commands.keys():
						raise CommandError('Invalid Alias')
					cmd = self.__commands[cmd.alias]

				if hasattr(cmd, 'disabled') and cmd.disabled == True:
					self.__logger.debug('%s has been disabled', cmd.command)
					return
				else:
					cmd(self, {'nick': nick, 'host': host}, line)
		except CommandError, e:
			self.__logger.warning('CommandError')
			self.irc_notice(nick, e.__str__())
		except Exception, e:
			self.__logger.exception('Error processing commands\n%s', line)
			self.irc_notice(nick, 'There was an error processing that command')
			if self._debugvar >= 2:
				raise

	def alias_add(self, alias, command):
		def alias_func():
			pass
		if alias in self.__commands.keys():
			raise BotError('Alias cannot overwrite existing object')
		alias_func.alias = command
		self.__commands[alias] = alias_func

	def alias_remove(self, alias):
		if not alias in self.__commands.keys():
			raise BotError('Invalid alias name')
		cmd = self.__commands[alias]
		if not hasattr(cmd, 'alias'):
			raise BotError('Invalid alias')
		self.__commands.pop(alias)

	def plugin_register(self, module):
		"""Register a new plugin

		:param module: Module name in dot format. Ex my.plugin
		:type module: str
		"""
		if module in self.__plugins.keys():
			self.__logger.warning('Already loaded module %s', module)
			return True

		try:
			# We want to split off the last part of the module name
			# so that we can get just the module we want instead of
			# the entire stack
			name = module.split('.').pop()
			mod = __import__(module, fromlist=[name])
			self.__logger.info('Registering %s', mod.__purple__)
		except ImportError:
			self.__logger.exception('Error importing %s', module)
			return False
		except AttributeError:
			self.__logger.exception('Incomptable module %s', module)
			return False
		except Exception:
			self.__logger.exception('Unknown Error loading plugin %s', module)
			if self._debugvar >= 2:
				raise
			return False
		else:
			self.__plugins[module] = mod
			for name, obj in vars(mod).iteritems():
				if name == 'load':
					self.__logger.info('Running %s plugin load event', module)
					obj(self)
				if hasattr(obj, 'command'):
					self.__logger.info('Loading command: %s', obj.command)
					self.__commands[obj.command] = obj
				if hasattr(obj, 'event'):
					self.__logger.info('Loading %s event: %s', obj.event, name)
					self.event_register(obj.event, obj)

	def plugin_unregister(self, module):
		"""Unregister a plugin

		:param module: Module name in dot format. Ex my.plugin
		:type module: str
		"""
		module = module.replace('.', '_')
		if not module in self.__plugins.keys():
			return False
		try:
			mod = self.__plugins[module]
		except Exception:
			self.__logger.debug('Error unloading plugin %s', module)
			if self._debugvar >= 2:
				raise
			return False
		else:
			for name, obj in vars(mod).iteritems():
				if name == 'unload':
					self.__logger.debug('Running %s plugin unload event', module)
					obj(self)
				if hasattr(obj, 'command'):
					self.__logger.debug('Unloading command: %s', obj.command)
					self.__commands.pop(obj.command)
				if hasattr(obj, 'event'):
					self.__logger.debug('Unloading %s event: %s', obj.event, name)
					self.event_unregister(obj.event, obj)
			self.__plugins.pop(module)

	def __cmd_version(self, bot, hostmask, line):
		bot.irc_ctcp_reply(line, '1.1')

	def kill(self):
		for p in self.__plugins.keys():
			self.plugin_unregister(p)
		self.event_unregister('PRIVMSG', self.__parse_commands)
		self.running = False

	def command_help(self, cmd):
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

	def command_enable(self, cmd):
		if cmd in self.__commands.keys():
			self.__logger.info('Enable command %s', cmd)
			cmd = self.__commands[cmd]
			cmd.disabled = False

	def command_disable(self, cmd):
		if cmd in self.__commands.keys():
			self.__logger.info('Disable command %s', cmd)
			cmd = self.__commands[cmd]
			cmd.disabled = True

	def timedelay(self, time, func, args):
		threading.Timer(time, func, args).start()

	def __str__(self):
		return '%s' % (self.settings)
