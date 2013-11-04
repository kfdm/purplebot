try:
    import unittest2 as unittest
except ImportError:
    import unittest

from purplebot.test import testbot
from purplebot.util import parse_hostmask


class TestHostname(unittest.TestCase):
    def setUp(self):
        self.bot = testbot()

    def test_invalid_hostname(self):
        with self.assertRaises(IndexError):
            parse_hostmask('foo')

    def test_hostname(self):
        nick, mask = parse_hostmask(':KFDM!~paul@purple')
        self.assertEqual(nick, 'KFDM')
        self.assertEqual(mask, '~paul@purple')
