import logging
import optparse
import os

from purplebot.bot import bot


class PurpleParser(optparse.OptionParser):
	def __init__(self):
		def store_path(option, opt, value, parser):
			setattr(parser.values, option.dest, os.path.realpath(value))
		optparse.OptionParser.__init__(self, usage="%prog [options] (start|stop|restart)")
		self.add_option('--settings', help='Settings File',
			dest='settings', default=os.path.expanduser('~/.purplebot/settings.json'))
		self.add_option('--host', help='IRC Server',
			dest='host', default='irc.gamesurge.net')
		self.add_option('--port', help='IRC Port',
			dest='port', type='int', default=6667)
		self.add_option('--nick', help='Nickname',
			dest='nick', default='PurpleBot')
		self.add_option('--ident', help='Ident',
			dest='ident', default='PurpleBot')
		self.add_option('--realname', help='Realname',
			dest='realname', default='PurpleBot')
		self.add_option('--quit', help='Quit Message',
			dest='quit', default='Sayonara')
		self.add_option('--channel', help='Channels to join',
			dest='channels', action='append', default=[])
		self.add_option('--plugins', help='Plugins to load',
			dest='plugins', action='append', default=[])
		self.add_option('-v', '--verbose', dest='verbose', default=logging.INFO,
			action='store_const', const=logging.DEBUG)


def main():
	(options, args) = PurpleParser().parse_args()
	logging.root.setLevel(options.verbose)

	pb = bot(1, options.settings)

	for plugin in pb.settings.get('Plugins', []):
		pb.plugin_register(plugin)

	pb.run(
		options.host,
		options.port,
		options.nick,
		options.ident,
		options.realname
	)

if __name__ == '__main__':
	main()
