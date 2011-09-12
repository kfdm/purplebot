class BotError(Exception):
	def __init__(self,message):
		self.message = message
	def __str__(self):
		return self.message
class PluginError(BotError):
	pass
class CommandError(BotError):
	pass
class CommandDisabledError(BotError):
	pass