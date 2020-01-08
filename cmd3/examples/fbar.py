from __future__ import print_function
from cmd3.shell import function_command


def main_func(arguments):
    """
    Usage:
         hallo NAME
    
    Arguments:
         NAME    just an example [default: gregor]
    """
    print(arguments)
    print("Name", arguments["NAME"])


# noinspection PyUnusedLocal
class fbar:

    def activate_fbar(self):
        print("... activate fbar")

    def info_fbar(self):
        print("information for the class bar")

    @function_command(main_func)
    def do_fbar(self, arg, arguments):
        main_func(arguments)
        pass
