import re
import logging

logger = logging.getLogger(__name__)


class BlockList(object):
    def __init__(self, settings):
        self.settings = settings
        self.rebuild()

    def add(self, str):
        """Add name to the blocklist"""
        if str in self.settings['Core::Blocks']:
            return
        self.settings['Core::Blocks'].append(str)
        self.rebuild()
        self.settings.save()

    def remove(self, str):
        """Remove name from the block list"""
        if str in self.settings['Core::Blocks']:
            self.settings['Core::Blocks'].remove(str)
            self.rebuild()
            self.settings.save()

    def check(self, str):
        for block in self.__blocks:
            #logger.debug('Checking: %s'%block)
            if block.search(str):
                #logger.debug('Blocking: %s'%block)
                return True
        return False

    def rebuild(self):
        self.__blocks = []
        for block in self.settings.get('Core::Blocks', []):
            logger.debug('Compiling %s' % block)
            block = block.replace('*', '.*')
            self.__blocks.append(re.compile(block))
