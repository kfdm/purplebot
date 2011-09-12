#!/usr/bin/env python
from distutils.core import setup
from tasks.clean import CleanCommand
from tasks.test import TestCommand

setup(
	name = 'PurpleBot',
	description = 'Mostly simple irc bot',
	cmdclass = { 'test': TestCommand, 'clean': CleanCommand }
)
