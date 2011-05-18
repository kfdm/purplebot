import logging
from purplebot.bot import bot
from extras.daemon import Daemon

logger = logging.getLogger(__name__)

class PurpleDaemon(Daemon):
	def _join_channels(self,bot,channels):
		for channel in channels:
			bot.irc_join(channel)
	def _load_bot(self):
		for plugin in self.options.plugins:
			self.bot.plugin_register(plugin)
		self.bot.timedelay(10,self._join_channels,[self.bot,self.options.channels]) #Delayed join
	def _run_bot(self):
		self.bot.run(self.options.host, self.options.port, self.options.nick, self.options.ident, self.options.realname)
	def parse_args(self,options,args):
		self.options = options
		if 'start' in args:
			self.start()
		elif 'restart' in args:
			self.restart()
		elif 'stop' in args:
			self.stop()
		else:
			self.run()
	def run(self):
		logger.info('Initializing bot')
		self.bot = bot()
		logger.info('Loading bot')
		self._load_bot()
		logger.info('Running bot')
		self._run_bot()
