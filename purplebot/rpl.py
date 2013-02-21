import cmd
import logging
from purplebot.test import testbot


class RPL(cmd.Cmd):
    def do_init(self, *args):
        self.bot = testbot()
        self.bot.connect('localhost', 6667, 'testbot', 'testbot', 'testbot')

    def do_exit(self, line):
        exit(0)

    def default(self, line):
        self.bot._parse_line(line)


def main():
    logging.basicConfig(level=logging.DEBUG)
    cli = RPL()
    cli.do_init()
    cli.cmdloop()

if __name__ == '__main__':
    main()
