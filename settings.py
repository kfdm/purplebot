#!/usr/bin/env python
import os
from purplebot.test import testbot
logfile = os.path.abspath('./irc.log')
bot = testbot()
#bot.parse_file(logfile)

bot.settings.set('Testing','test')
print 'Testing should equal:', bot.settings.get('Testing')
print 'Missing setting:', bot.settings.get('Missing','default missing')
bot.settings.save()
