.. See http://packages.python.org/an_example_pypi_project/sphinx.html#full-code-example
Writing Plugins
===============

A lot of the bot functionality is added through writing additional plugins.
From the main botj

.. automethod:: purplebot.bot.bot.plugin_register
.. automethod:: purplebot.bot.bot.plugin_unregister
.. automethod:: purplebot.bot.bot.plugin_list

Example Command
---------------
::

	# Command plugins will all have this signature where
	# bot is a pointer to the running bot instance
	# hostmask - is a hash of the user invoking the command
	# line - is the PRIVMSG line from IRC
	def nick(bot,hostmask,line):
		"""Allow an admin to change the bot's nick at runtime"""
		# Public bot functions can easily be called from these functions
		bot.irc_nick(line[4])
	# Extra function properties are added to control how the plugins function
	
	# The .command property provides the search string for the bot
	# bot to run the command
	nick.command = '$nick'
	
	# The .example property is used with the .help command to show 
	# the usage of the command
	nick.example = '$nick <Nick>'
	
	# The .admin property is used to restrict commands to users that
	# have been registered as an admin
	nick.admin	= True
	
	# The .owner property is used to restrict commands to the single bot
	# owner.
	nick.owner	= True

.. note:: In the future the help command may come from the first line of the
	function's doc string

.. note:: In the future the .admin and .owner properties will be changed to use
	some sort of user level

Example Event
-------------
::

	# Events will have parameters for the bot and the irc line
	def voice(bot,line):
		"""Auto voice users when they join"""
		nick,host = bot.parse_hostmask(line[0])
		voicelist = bot.setting_get('VoicePlugin::list',[])
		for voice in voicelist:
			if host == voice:
				bot.irc_mode('#channel','+v %s'%nick)
	# The event property sets which event queue the function should be
	# Placed on
	voice.event = 'join'
