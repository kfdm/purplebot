try:
    import unittest2 as unittest
except ImportError:
    import unittest

from purplebot.settings.jsonsettings import Settings
from purplebot.util import BlockList


class TestBlockList(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()
        self.settings['Core::Blocks'] = []
        self.block = BlockList(self.settings)

    def test_add_block(self):
        self.block.add('foo')

    def test_block(self):
        self.block.add('foo')
        self.assertTrue(self.block.check('foobar'))

    def test_remove_block(self):
        self.block.add('foo')
        self.assertTrue(self.block.check('foobar'))
        self.block.remove('foo')
        self.assertFalse(self.block.check('foobar'))
