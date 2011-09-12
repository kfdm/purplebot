import logging
logger = logging.getLogger(__name__)

import os

try:
	import json
except ImportError:
	import simplejson as json

#from purplebot.bot import BotError

restricted = ['Core::Admins','Core::Blocks','Core::Owner']

class Settings(object):
	def __init__(self):
		self.__settings = {}
		self.file = os.path.abspath('settings.json')
	
	def get(self,key,default=None,required=False):
		setting = self.__settings.get(key,default)
		if required and setting is None:
			raise BotError('Missing required setting '+key)
		return setting
	def set(self,key,value):
		if key in restricted:
			return
		self.__settings[key] = value
	def append(self,key,value):
		if value in self.__settings[key]:
			return
		self.__settings[key].append(value)
	def remove(self,key,value):
		if value in self.__settings[key]:
			self.__settings[key].remove(value)
			self.save()
	
	def save(self):
		try:
			output = open(self.file,'wb')
			output.write(json.dumps(self.__settings, sort_keys=True, indent=4))
			output.close()
			logger.debug('Settings saved')
		except:
			logger.exception('Error writting settings!')
	def load(self):
		try:
			input = open(self.file,'rb')
			self.__settings = json.loads(input.read())
			input.close()
			logger.debug('Settings loaded')
		except:
			logger.exception('Error loading settings')
	