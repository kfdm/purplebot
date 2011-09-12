#!/usr/bin/env python
import unittest
from purplebot.test import testbot

class TestSettings(unittest.TestCase):
	"""Test the settings within the framework of the bot"""
	def setUp(self):
		self.bot = testbot()
	def test_set_function(self):
		key = 'Testing'
		val = 'test value'
		self.bot.settings.set(key,val)
		assert val == self.bot.settings.get(key)
	def test_missing(self):
		key = 'Missing value'
		assert None == self.bot.settings.get(key)
	def test_saving(self):
		assert self.bot.settings.save() == True
	def test_loading(self):
		assert self.bot.settings.load() == True
	
	def test_getitem(self):
		key = 'Testing'
		assert self.bot.settings[key] == self.bot.settings.get(key)
	def test_setitem(self):
		key = 'setitem'
		val = 'some value'
		self.bot.settings[key] = val
		assert self.bot.settings[key] == val
	
	def test_required(self):
		key = 'requiredvalue'
		assert self.bot.settings.required(key)