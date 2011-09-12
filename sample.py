#!/usr/bin/env python
import os
import logging
from purplebot.bot import bot

# Logging
_format_file = '%(asctime)s %(levelname)-8s %(name)-12s %(message)s'
_format_console = '%(levelname)-8s %(name)-12s: %(message)s'
logging.basicConfig(level=logging.DEBUG,
	format=_format_file,
	datefmt='%m-%d %H:%M',
	filename='bot.log',
	filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(_format_console)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Raw IRC Log
irc = logging.FileHandler('irc.log')
irc.setLevel(logging.NOTSET)
irc.setFormatter( logging.Formatter('%(message)s') )
logging.getLogger('irc.in').addHandler(irc)
logging.getLogger('irc.out').addHandler(irc)

HOST="irc.gamesurge.net"
PORT=6667
NICK="PurpleBot"
IDENT="PurpleBot"
REALNAME="PurpleBot"
QUITMSG = "Sayonara"

CHANNELS=["#bottesting"]

#Setup the bot with debugging
sample = bot(2)

#Load plugins
sample.plugin_register('admin')
sample.plugin_register('voice')

#Add command aliases
sample.alias_add('$ignore','$addblock')

#Settings
sample.settings.set('Setting::key','Setting Value')

#Have functions fire after a certain delay
def join(bot,channels):
	for channel in channels:
		bot.irc_join(channel)
sample.timedelay(10,join,[sample,CHANNELS])

#Run the bot
sample.run(HOST, PORT, NICK, IDENT, REALNAME)
