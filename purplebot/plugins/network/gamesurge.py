import logging

__purple__ = __name__

logger = logging.getLogger(__name__)

def auth(bot):
	authserv = bot.settings.get('GamesurgePlugin::authserv')
	authstr = bot.settings.get('GamesurgePlugin::authstring')
	if authserv != None and authstr != None:
		bot.irc_privmsg(authserv,authstr)
		bot.timedelay(10,modes,[bot])
	else:
		logger.debug('Error authing')
auth.event = 'connect'


def invite(self, bot, line):
	channels = bot.settings.get('GamesurgePlugin::whitelist',[])
	if line[4] in channels:
		bot.irc_join(line[4])
	else:
		logger.warning('Channel [%s] is not white listeded', line[4])
invite.event = 'invite'


def modes(bot):
	modes = bot.settings.get('GamesurgePlugin::authmode')
	if modes != None:
		bot.irc_mode(bot._nick,modes)
	else:
		logger.debug('Error setting modes')
