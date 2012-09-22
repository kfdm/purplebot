__purple__ = __name__


def nick(bot, hostmask, line):
	bot.irc_nick(line[4])
nick.command = '$nick'
nick.example = '$nick <Nick>'
nick.admin = True


def part(bot, hostmask, line):
	bot.irc_part(line[4])
part.command = '$part'
part.example = '$part <channel>'
part.admin = True


def join(bot, hostmask, line):
	bot.irc_join(line[4])
join.command = '$join'
join.example = '$join <example>'
join.admin = True


def addadmin(bot, hostmask, line):
	bot.admin_add(line[4])
addadmin.command = '$addadmin'
addadmin.admin = True


def deladmin(bot, hostmask, line):
	bot.admin_remove(line[4])
deladmin.command = '$deladmin'
deladmin.admin = True


def addblock(bot, hostmask, line):
	bot.block.add(line[4])
addblock.command = '$addblock'
addblock.admin = True


def delblock(bot, hostmask, line):
	bot.block.remove(line[4])
delblock.command = '$delblock'
delblock.admin = True
