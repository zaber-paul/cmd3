from __future__ import print_function
from builtins import object
from cmd3.shell import command


# noinspection PyUnusedLocal
class opt_example(object):
    """opt_example class"""

    def activate_opt_example(self):
        pass

    @command
    def do_opt_example(self, args, arguments):
        """
        Usage:
               opt_example [-vr] [FILE] ...

        Process FILE and optionally apply some options

        Arguments:
          FILE        optional input file

        Options:
          -v       verbose mode
          -r       make report

        """
        print(arguments)

    @command
    def do_neu(self, args, arguments):
        """
        Usage:
               opt_example [-vr] [FILE] ...

        Process FILE and optionally apply some options

        Arguments:
          FILE        optional input file

        Options:
          -v       verbose mode
          -r       make report

        """
        # arguments = _get_doc_args(self.do_neu,args)

        print(arguments)
        return ""

    @command
    def do_old(self, args, arguments):
        """
        Usage:
               old [-ab] [FILE] ...

        Process FILE and optionally apply some options

        Arguments:
          FILE        optional input file

        Options:
          -a       verbose mode
          -b       make report

        """
        # arguments = _get_doc_args(self.do_neu,args)

        print(arguments)
        return ""
