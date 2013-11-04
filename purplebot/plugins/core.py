__purple__ = __name__

from purplebot.decorators import require_admin, require_owner

@require_owner
def command_enable(bot,hostmask,line):
	if line[4] in ['$enable','$disable']: return
	bot.command_enable(line[4])
command_enable.command = '$enable'

@require_owner
def command_disable(bot,hostmask,line):
	if line[4] in ['$enable','$disable']: return
	bot.command_disable(line[4])
command_disable.command = '$disable'

@require_admin
def kill(bot,hostmask,line):
	nick,host = hostmask['nick'],hostmask['host']
	bot.irc_notice(nick, 'Bot is shutting down')
	bot.irc_quit()
	bot.kill()
kill.command = '$kill'

def help(bot,hostmask,line):
	nick,host = hostmask['nick'],hostmask['host']
	if len(line)==4: line.append('')
	bot.irc_notice(nick,bot.command_help(line[4]))
help.command = '.help'
help.example = '.help <commandname>'

@require_admin
def loadplugin(bot,hostmask,line):
	for p in line[4].split(','):
		bot.plugin_register(p)
loadplugin.command = '$loadplugin'

@require_admin
def unloadplugin(bot,hostmask,line):
	for p in line[4].split(','):
		if p == 'core': continue
		bot.plugin_unregister(p)
unloadplugin.command = '$unloadplugin'

@require_admin
def reloadplugin(bot,hostmask,line):
	unloadplugin(bot, hostmask, line)
	loadplugin(bot, hostmask, line)
reloadplugin.command = '$reloadplugin'

@require_admin
def listplugins(bot,hostmask,line):
	nick,host = hostmask['nick'],hostmask['host']
	bot.irc_notice(nick,bot.plugin_list().__str__())
listplugins.command = '$plugins'

@require_owner
def get_setting(bot,hostmask,line):
	value = bot.settings.get(line[4])
	bot.irc_notice(hostmask['nick'],'[%s] - [%s]'%(line[4],value))
get_setting.command = '$get'

@require_owner
def set_setting(bot,hostmask,line):
	setting = line[4].split(' ',1)
	try: setting[1] = int(setting[1])
	except: pass
	bot.settings.set(setting[0],setting[1])
	bot.irc_notice(hostmask['nick'],'Set [%s] to [%s]'%(setting[0],setting[1]))
set_setting.command = '$set'
