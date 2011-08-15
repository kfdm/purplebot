
Core Bot Functions
==================

When modifying the base bot or writing plugins, these are the methods you will
typically be interested in

Plugins
-------

Much of the functionality for the bot comes from registering plugins

.. automethod:: purplebot.bot.bot.plugin_register
.. automethod:: purplebot.bot.bot.plugin_unregister
.. automethod:: purplebot.bot.bot.plugin_list

Commands
--------
.. automethod:: purplebot.bot.bot.command_enable
.. automethod:: purplebot.bot.bot.command_disable
.. automethod:: purplebot.bot.bot.command_help

Admin
-----
.. automethod:: purplebot.bot.bot.admin_add
.. automethod:: purplebot.bot.bot.admin_remove
.. automethod:: purplebot.bot.bot.admin_check

Block
-----
.. automethod:: purplebot.bot.bot.block_add
.. automethod:: purplebot.bot.bot.block_remove

Alias
-----
.. automethod:: purplebot.bot.bot.alias_add
.. automethod:: purplebot.bot.bot.alias_remove

Setting
-------
.. automethod:: purplebot.bot.bot.setting_get
.. automethod:: purplebot.bot.bot.setting_set
.. automethod:: purplebot.bot.bot.settings_save
.. automethod:: purplebot.bot.bot.settings_load

Core IRC Functions
=====================================

Bot Events
----------

The event system allows you to watch for an event, and register a function to
be called. Examples of events would be some of the IRC message types such as
PRIVMSG, JOIN, PART, QUIT, etc.

.. automethod:: purplebot.irc.irc.event
.. automethod:: purplebot.irc.irc.event_register
.. automethod:: purplebot.irc.irc.event_unregister

IRC Commands
------------

Basic IRC commands. Use these to send messages to the server.

.. automethod:: purplebot.irc.irc.irc_raw
.. automethod:: purplebot.irc.irc.irc_nick
.. automethod:: purplebot.irc.irc.irc_part
.. automethod:: purplebot.irc.irc.irc_notice
.. automethod:: purplebot.irc.irc.irc_user
.. automethod:: purplebot.irc.irc.irc_pong
.. automethod:: purplebot.irc.irc.irc_privmsg
.. automethod:: purplebot.irc.irc.irc_quit
.. automethod:: purplebot.irc.irc.irc_ping
.. automethod:: purplebot.irc.irc.irc_join
.. automethod:: purplebot.irc.irc.irc_mode
.. automethod:: purplebot.irc.irc.irc_ctcp_reply
.. automethod:: purplebot.irc.irc.irc_ctcp_send


.. toctree::
   :maxdepth: 2

See http://packages.python.org/an_example_pypi_project/sphinx.html#full-code-example