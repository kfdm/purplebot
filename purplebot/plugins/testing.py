__purple__ = __name__

from purplebot.decorators import require_owner

@require_owner
def raw(bot,hostmask,line):
	bot.irc_raw(line[4]+'\r\n')
raw.command = '$raw'

@require_owner
def say(bot,hostmask,line):
	dest,msg = __dest_msg(hostmask, line)
	bot.irc_privmsg(dest,msg)
say.command = '$say'

@require_owner
def me(bot,hostmask,line):
	dest,msg = __dest_msg(hostmask, line)
	bot.irc_ctcp_send(dest,'ACTION '+msg)
me.command = '$me'

def __dest_msg(hostmask,line):
	if line[4][0:1] == '#':
		tmp = line[4].split(' ',1)
		return tmp[0],tmp[1]
	else:
		if line[2][0:1] == '#': dest = line[2]
		else: dest = hostmask['nick']
		return dest,line[4]
