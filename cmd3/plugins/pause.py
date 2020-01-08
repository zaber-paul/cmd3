from builtins import input
from builtins import object
from cmd3.shell import command


# noinspection PyUnusedLocal
class pause(object):

    def activate_pause(self):
        """activates the pause command"""
        pass

    @command
    def do_pause(self, arg, arguments):
        """
        ::

            Usage:
                pause [MESSAGE]

            Displays the specified text then waits for the user to press RETURN.

            Arguments:
               MESSAGE  message to be displayed
        """
        eval(input(arg + '\n'))
