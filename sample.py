from purplebot.bot import bot

HOST="Krypt.CA.US.GameSurge.net"
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
sample.setting_set('Setting::key','Setting Value')

#Have functions fire after a certain delay
def join(bot,channels):
	for channel in channels:
		bot.irc_join(channel)
sample.timedelay(10,join,[sample,CHANNELS])

#Run the bot
sample.run(HOST, PORT, NICK, IDENT, REALNAME)
