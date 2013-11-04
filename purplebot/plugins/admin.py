__purple__ = __name__

from purplebot.decorators import require_admin

@require_admin
def nick(bot, hostmask, line):
	bot.irc_nick(line[4])
nick.command = '$nick'
nick.example = '$nick <Nick>'


@require_admin
def part(bot, hostmask, line):
	bot.irc_part(line[4])
part.command = '$part'
part.example = '$part <channel>'


@require_admin
def join(bot, hostmask, line):
	bot.irc_join(line[4])
join.command = '$join'
join.example = '$join <example>'


@require_admin
def addadmin(bot, hostmask, line):
	bot.settings.append('Core::Admins', line[4])
	bot.settings.save()
addadmin.command = '$addadmin'


@require_admin
def deladmin(bot, hostmask, line):
	bot.settings.remove('Core::Admins', line[4])
deladmin.command = '$deladmin'


@require_admin
def addblock(bot, hostmask, line):
	bot.block.add(line[4])
addblock.command = '$addblock'


@require_admin
def delblock(bot, hostmask, line):
	bot.block.remove(line[4])
delblock.command = '$delblock'

