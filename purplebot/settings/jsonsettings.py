import logging
logger = logging.getLogger(__name__)

import os

try:
	import json
except ImportError:
	import simplejson as json

from purplebot.errors import BotError

restricted = ['Core::Admins', 'Core::Blocks', 'Core::Owner']

DEFAULT_PATH = os.path.join(
	os.path.expanduser('~'), '.config', 'purplebot', 'settings.json')

class Settings(object):
	def __init__(self, path=None):
		self.__settings = {}
		if path:
			self.file = path
		else:
			self.file = DEFAULT_PATH

	def __getitem__(self, key):
		return self.__settings[key]

	def __setitem__(self, key, value):
		self.__settings[key] = value

	def required(self, key):
		"""Require that a queried key is found"""
		if key not in self.__settings:
			raise BotError('Missing required setting ' + key)
		return self.__settings[key]

	def get(self, key, default=None, required=False):
		if required:
			return self.required(key)
		return self.__settings.get(key, default)

	def set(self, key, value):
		self.__settings[key] = value

	def append(self, key, value):
		"""Treat the key as a list and append the value"""
		if key not in self.__settings:
			self.__settings[key] = []
		if value in self.__settings[key]:
			return
		self.__settings[key].append(value)

	def remove(self, key, value):
		"""Treat the key as a list and remove the value"""
		if value in self.__settings[key]:
			self.__settings[key].remove(value)
			self.save()

	def save(self):
		with open(self.file, 'w', encoding='utf8') as fp:
			fp.write(json.dumps(self.__settings, sort_keys=True, indent=4))
			logger.debug('Settings saved')
			return True
		logger.exception('Error writting settings!')
		return False

	def load(self):
		if os.path.exists(self.file) is False:
			logger.debug('No settings file exists')
			return False
		with open(self.file, 'r', encoding='utf8') as fp:
			self.__settings = json.loads(fp.read())
			logger.debug('Settings loaded')
			return True
		logger.exception('Error writing settings')
		return False
