__purple__ = __name__

def voice(bot,line):
	nick,host = bot.parse_hostmask(line[0])
	voicelist = bot.setting_get('VoicePlugin::list',[])
	for voice in voicelist:
		if host == voice:
			bot.irc_mode('#japanese','+v %s'%nick)
voice.event = 'join'

def addvoice(bot,hostmask,line):
	voicelist = bot.setting_get('VoicePlugin::list',[])
	if not line[4] in voicelist:
		voicelist.append(line[4])
		bot.setting_set('VoicePlugin::list',voicelist)
addvoice.command = '$addvoice'
addvoice.example = '$addvoice <nick>'
addvoice.admin = True

def delvoice(bot,hostmask,line):
	voicelist = bot.setting_get('VoicePlugin::list',[])
	if line[4] in voicelist:
		voicelist.remove(line[4])
		bot.setting_set('VoicePlugin::list',voicelist)
delvoice.command = '$delvoice'
delvoice.example = '$delvoice <nick>'
delvoice.admin = True