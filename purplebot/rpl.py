import cmd
import logging
import code
import sys

from pprint import pprint
from purplebot.test import testbot
from purplebot.cli.console import LOG_FORMAT


class RPL(cmd.Cmd):
    prompt = 'bot> '

    def do_spawn(self, *args):
        """Spawn new bot"""
        self.bot = testbot()
        self.bot.connect('localhost', 6667, 'testbot', 'testbot', 'testbot')

    def do_exit(self, line):
        """Exit RPL"""
        return True

    def do_load(self, plugin):
        self.bot.plugin_register(plugin)

    def do_unload(self, plugin):
        self.bot.plugin_unregister(plugin)

    def do_list(self, *args):
        print self.bot.plugin_list()

    def do_shell(self, line):
        """Jump into a Python Shell"""
        env = {'bot': self.bot, 'pprint': pprint}
        try:
            import readline
        except ImportError:
            pass
        else:
            import rlcompleter
            readline.set_completer(rlcompleter.Completer(env).complete)
            if(sys.platform == 'darwin'):
                readline.parse_and_bind("bind ^I rl_complete")
            else:
                readline.parse_and_bind("tab:complete")

        code.interact(local=env)

    def emptyline(self):
        pass

    def default(self, line):
        if line == 'EOF':
            return True
        self.bot._parse_line(line)


def main():
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    cli = RPL()
    cli.do_spawn()
    cli.cmdloop()

if __name__ == '__main__':
    main()
