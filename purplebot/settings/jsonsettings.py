import logging
logger = logging.getLogger(__name__)

import os

try:
	import json
except ImportError:
	import simplejson as json

#import purplebot.bot
from purplebot.errors import BotError

restricted = ['Core::Admins', 'Core::Blocks', 'Core::Owner']


class Settings(object):
	def __init__(self):
		self.__settings = {}
		self.file = os.path.abspath('settings.json')

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
		if value in self.__settings[key]:
			return
		self.__settings[key].append(value)

	def remove(self, key, value):
		"""Treat the key as a list and remove the value"""
		if value in self.__settings[key]:
			self.__settings[key].remove(value)
			self.save()

	def save(self):
		try:
			output = open(self.file, 'wb')
			output.write(json.dumps(self.__settings, sort_keys=True, indent=4))
			output.close()
			logger.debug('Settings saved')
			return True
		except:
			logger.exception('Error writting settings!')
			return False

	def load(self):
		try:
			input = open(self.file, 'rb')
			self.__settings = json.loads(input.read())
			input.close()
			logger.debug('Settings loaded')
			return True
		except:
			logger.exception('Error loading settings')
			return False

if __name__ == '__main__':
	print 'testing'
