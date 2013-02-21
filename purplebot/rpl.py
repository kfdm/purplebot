import cmd
import logging
import code
from purplebot.test import testbot


class RPL(cmd.Cmd):
    prompt = 'bot> '

    def do_spawn(self, *args):
        """Spawn new bot"""
        self.bot = testbot()
        self.bot.connect('localhost', 6667, 'testbot', 'testbot', 'testbot')

    def do_exit(self, line):
        """Exit RPL"""
        return True

    def do_shell(self, line):
        """Jump into a Python Shell"""
        code.interact(local={'bot': self.bot})

    def emptyline(self):
        pass

    def default(self, line):
        if line == 'EOF':
            return True
        self.bot._parse_line(line)


def main():
    logging.basicConfig(level=logging.DEBUG)
    cli = RPL()
    cli.do_spawn()
    cli.cmdloop()

if __name__ == '__main__':
    main()
