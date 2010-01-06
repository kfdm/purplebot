def auth(bot):
	authserv = bot.setting_get('GamesurgePlugin::authserv')
	authstr = bot.setting_get('GamesurgePlugin::authstring')
	if authserv != None and authstr != None:
		bot.irc_privmsg(authserv,authstr)
		bot.timedelay(10,modes,[bot])
		bot.timedelay(10,join,[bot])
	else:
		bot.debug('Error authing')
auth.event = 'connect'

def join(bot):	
	channels = bot.setting_get('GamesurgePlugin::channels',[])
	print channels
	for channel in channels:
		bot.irc_join(channel)

def modes(bot):
	modes = bot.setting_get('GamesurgePlugin::authmode')
	if modes != None:
		bot.irc_mode(bot._nick,modes)
	else:
		bot.debug('Error setting modes')
