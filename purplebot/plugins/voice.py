__purple__ = __name__

from purplebot.util import parse_hostmask
from purplebot.decorators import require_admin

def voice(bot,line):
	nick,host = parse_hostmask(line[0])
	voicelist = bot.settings.get('VoicePlugin::list',[])
	for voice in voicelist:
		if host == voice:
			bot.irc_mode('#japanese','+v %s'%nick)
voice.event = 'join'

@require_admin
def addvoice(bot,hostmask,line):
	voicelist = bot.settings.get('VoicePlugin::list',[])
	if not line[4] in voicelist:
		voicelist.append(line[4])
		bot.settings.set('VoicePlugin::list',voicelist)
addvoice.command = '$addvoice'
addvoice.example = '$addvoice <nick>'

@require_admin
def delvoice(bot,hostmask,line):
	voicelist = bot.settings.get('VoicePlugin::list',[])
	if line[4] in voicelist:
		voicelist.remove(line[4])
		bot.settings.set('VoicePlugin::list',voicelist)
delvoice.command = '$delvoice'
delvoice.example = '$delvoice <nick>'
