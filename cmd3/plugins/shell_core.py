from __future__ import print_function
from builtins import str
from builtins import input
from builtins import object
import os
import sys
from textwrap import dedent

import pkg_resources
from cloudmesh_base.util import get_python
from cloudmesh_base.util import check_python
from cmd3.console import Console
import cloudmesh_base

import cmd3


class shell_core(object):

    def help_help(self):
        """
        Usage:
           help NAME

        Prints out the help message for a given function
        """
        print(dedent(self.help_help.__doc__))

    def info_shell_core(self):
        """prints information about the shell core"""
        Console.ok("{:>20} = {:}".format("VERSION", cmd3.__version__))

    def do_version(self, args):
        """
        Usage:
           version

        Prints out the version number
        """
        Console.ok("cmd3: {:}".format(str(cmd3.__version__)))
        Console.ok("cloudmesh_base: {:}".format(str(cloudmesh_base.__version__)))

        python_version, pip_version = get_python()

        Console.ok("python: {:}".format(str(python_version)))
        Console.ok("pip: {:}".format(str(pip_version)))


        check_python()


    def activate_shell_core(self):
        """activates the shell_core commands"""
        self._hist = []

    def do_EOF(self, args):
        """
        Usage:
            EOF

        Command to the shell to terminate reading a script.
        """
        return True

    def do_quit(self, args):
        """
        Usage:
            quit

        Action to be performed whne quit is typed
        """
        sys.exit()

    do_q = do_quit
        
    def emptyline(self):
        return

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.
        """
        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey + ": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro) + "\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = eval(input(self.prompt))
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    def do_exec(self, filename):
        """
        ::
        
            Usage:
               exec FILENAME

            executes the commands in the file. See also the script command.

            Arguments:
              FILENAME   The name of the file
        """
        if not filename:
            Console.error("the command requires a filename as parameter")
            return

        if os.path.exists(filename):
            with open(filename, "r") as f:
                for line in f:
                    Console.ok("> {:}".format(str(line)))
                    self.onecmd(line)
        else:
            Console.error('file "{:}" does not exist.'.format(filename))
            sys.exit()



