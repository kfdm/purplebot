from optparse import OptionParser
from purplebot.bot import bot

def join(bot,channels):
	for channel in channels:
		bot.irc_join(channel)

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option("--debug", dest="debug", help="Debug", default=0,type="int")
	parser.add_option("--host", dest="host", help="IRC Server", default="irc.gamesurge.net")
	parser.add_option("--port", dest="port", help="IRC Port", default=6667,type="int")
	parser.add_option("--nick", dest="nick", help="Nickname", default="PurpleBot")
	parser.add_option("--ident", dest="ident", help="Ident", default="PurpleBot")
	parser.add_option("--realname", dest="realname", help="Realname", default="PurpleBot")
	parser.add_option("--quit", dest="quit", help="Quit Message", default="Sayonara")
	parser.add_option("--channel", dest="channels", help="Channels to join", default=[],action="append")
	parser.add_option("--plugin", dest="plugins", help="Plugins", default=[],action="append")
	(opts,args) = parser.parse_args()
	newbot = bot(opts.debug)
	for plugin in opts.plugins:
		newbot.plugin_register(plugin)
	newbot.timedelay(10,join,[newbot,opts.channels]) #Delayed join
	newbot.run(opts.host, opts.port, opts.nick, opts.ident, opts.realname)