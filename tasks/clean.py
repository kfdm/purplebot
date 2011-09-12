from distutils.core import setup,Command
from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join as pjoin, walk
import os

class CleanCommand(Command):
	user_options = [ ]

	def initialize_options(self):
		self._clean_me = [ ]
		for root, dirs, files in os.walk('.'):
			for f in files:
				if f.endswith('.pyc'):
					self._clean_me.append(pjoin(root, f))

	def finalize_options(self):
		pass

	def run(self):
		for clean_me in self._clean_me:
			try:
				print 'Removing:',clean_me
				os.unlink(clean_me)
			except:
				pass
