import unittest
from purplebot.settings.jsonsettings import Settings
from purplebot.errors import BotError


class TestSettings(unittest.TestCase):
	"""Test the settings within the framework of the bot"""
	def setUp(self):
		self.settings = Settings()

	def test_set_function(self):
		key = 'Testing'
		val = 'test value'
		self.settings.set(key, val)
		assert val == self.settings.get(key)

	def test_missing(self):
		key = 'Missing value'
		assert None == self.settings.get(key)

	def test_saving(self):
		assert self.settings.save() == True

	def test_loading(self):
		assert self.settings.load() == True

	def test_getitem(self):
		key = 'Testing'
		self.settings.set('Testing', 'foo')
		assert 'foo' == self.settings.get(key)

	def test_setitem(self):
		key = 'setitem'
		val = 'some value'
		self.settings[key] = val
		assert self.settings[key] == val

	def test_required(self):
		key = 'requiredvalue'
		with self.assertRaises(BotError):
			self.settings.required(key)
