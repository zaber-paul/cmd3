from __future__ import print_function
from builtins import object
from cmd3.shell import command


# noinspection PyUnusedLocal
class bar(object):

    def activate_bar(self):
        print("... activate bar")

    def info_bar(self):
        print("information for the class bar")

    @command
    def do_bar(self, arg, arguments):
        """Usage:
                bar -f FILE
                bar FILE
                bar list

        This command does some useful things.

        Arguments:
              FILE   a file name

        Options:
              -f      specify the file

        """
        print(arguments)
