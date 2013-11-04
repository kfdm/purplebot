import logging

__purple__ = __name__

logger = logging.getLogger(__name__)

def auth(bot):
	authserv = bot.settings.get('GamesurgePlugin::authserv')
	authstr = bot.settings.get('GamesurgePlugin::authstring')
	if authserv != None and authstr != None:
		bot.irc_privmsg(authserv,authstr)
		bot.timedelay(10,modes,[bot])
		bot.timedelay(10,join,[bot])
	else:
		logger.debug('Error authing')
auth.event = 'connect'

def join(bot):	
	channels = bot.settings.get('GamesurgePlugin::channels',[])
	for channel in channels:
		bot.irc_join(channel)

def modes(bot):
	modes = bot.settings.get('GamesurgePlugin::authmode')
	if modes != None:
		bot.irc_mode(bot._nick,modes)
	else:
		logger.debug('Error setting modes')
