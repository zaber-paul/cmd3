#! /usr/bin/env python
from __future__ import print_function
"""
This project is about developing a dynamic CMD class based on cmd.CMD.
We assume the following directory structure::

  ./shell.py
  ./plugins/foo.py
  ./plugins/bar.py
  ./plugins/activate.py

We have provided examples of the classes in this document

foo and bar contain some classes that include he usual do_ methods. It
also includes an activate method that is called wih the acivation
module, so you can control its behavior upon startup.

To specify the plugins please use::

  plugins = ["foo", "bar","activate"]

Now you can set a name for your class::

  name = "CmCLI"

The rest is pretty simple::

  (cmd, plugin_objects) = DynamicCmd(name, plugins)
  cmd.activate(plugin_objects)
  cmd.cmdloop()

The activate method is not called automatically as to give more
flexibility during startup.

Here are the sample classes::

   class bar:

       def activate_bar(self):
           print "... activate bar"

       def do_that(self, arg):
           print "THAT", arg


   class foo:

       def do_this(self, arg):
           print "THIS", arg
           self.activate_status()

       def activate_foo(self):
           print "... activate foo"

   class activate:

       active = False

       def do_on(self, arg):
           self.active = True
           self.activate_status()

       def do_off(self, arg):
           self.active = False
           self.activate_status()

       def activate_status(self):
           print "Active:", self.active

       def activate(self, plugins):
           d = dir(self)
           result = []
           for key in d:
               if key.startswith("activate_"):
                   result.append(key)
           print result
           for key in result:
               print "> %s" % key.replace("_"," ")
               exec("self.%s()" % key)
"""

import textwrap
from compiler.ast import flatten
from docopt import docopt
from pprint import pprint
import cmd
import glob
import inspect
import logging
import os
import pkg_resources  # part of setuptools
import platform
if not platform.system().lower() == 'windows':
    import readline
import shlex
import sys
import textwrap
import traceback
from cloudmesh_base.ConfigDict import ConfigDict
from cmd3.console import Console
import cmd3
from cmd3.yaml_setup import create_cmd3_yaml_file
from cloudmesh_base.util import path_expand

# echo = False
echo = False



#
# SETTING UP A LOGGER
#

log = logging.getLogger('cmd3')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('CMD3: [%(levelname)s] %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log.addHandler(handler)

def path_into_cygpath(path):
    drive, destination = path.replace('\\','/').split(':')
    return '/cygdrive/' + drive.lower() + destination

#
# DYNAMIC COMMAND MANAGEMENT
#
#
# Gregor von Laszewski
#
# code insired from cyberaide and cogkit, while trying to develop a
# dynamic CMD that loads from plugin directory
#

def DynamicCmd(name, plugins):
    """
    Returns a cmd with the added plugins,
    
    :param name: TODO:
    :param plugins: list of plugins
    """
    exec('class %s(cmd.Cmd):\n    prompt="cm> "' % name)
    plugin_objects = []
    for plugin in plugins:
        classprefix = plugin['class']
        plugin_list = plugin['plugins']
        plugin_objects = plugin_objects + \
            load_plugins(classprefix, plugin_list)

    exec_command = make_cmd_class(name, *plugin_objects)()
    return (exec_command, plugin_objects)


def make_cmd_class(name, *bases):
    return type(cmd.Cmd)(name, bases + (cmd.Cmd,), {})


def get_plugins(directory):
    """
    returns the list of plugins from the specified directory
    :param directory: directory that contains the plugins. Files starting with _ will be ignored.
    """
    # not just plugin_*.py
    plugins = []
    files = glob.glob(directory + "/*.py")
    for p in files:
        p = p.replace(directory + "/", "").replace(".py", "")
        if not p.startswith('_'):
            plugins.append(p)
    # log.info("Loading Plugins from {0}".format(dir))
    # log.info("   {0}".format(str(plugins)))
    return plugins

try: 
    cygwin = os.environ['TERM']
    # print ("CCCCCCC", cygwin)
    cygwin = cygwin == 'cygwin'
    # print (cygwin)
except:
    # print ("NO CYGWIN")
    cygwin = False

def load_plugins(classprefix, plugin_list):
    """
    loads the plugins specified in the list
    :param classprefix: the class prefix
    :param plugin_list: the list of plugins
    """
    # classprefix "cmd3.plugins."
    plugins = []
    import_object = {}
    # log.info(str(list))
    for plugin in plugin_list:
        if cygwin:
            plugin = path_into_cygpath(plugin)
        # print ("PPPPP", classprefix, plugin)

        try:
            import_object[plugin] = __import__(
                classprefix + "." + plugin, globals(), locals(), [plugin], -1)
            # print ("TTT", import_object[plugin], type(import_object[plugin]))
            load_module = "cls = import_object['{0}'].{1}".format(plugin, plugin)
            # print ("LLL", load_module)
            exec(load_module)
            plugins.append(cls)
        except Exception as e:
            # if echo:
            Console.error("loading module {0} {1}".format(str(plugin), str(classprefix)))
            Console.error(70 * "=")
            print(e)
            Console.error(70 * "=")
            print(traceback.format_exc())
            Console.error(70 * "-")
            print(sys.exc_info()[0])
            Console.error(70 * "-")
            
    return plugins


#
# DECORATOR: COMMAND
#

def command(func):
    '''
    A decorator to create a function with docopt arguments. It also generates a help function
    
    @command
    def do_myfunc(self, args):
        """ docopts text """
        pass
        
    will create
    
    def do_myfunc(self, args, arguments):
        """ docopts text """
        ...
        
    def help_myfunc(self, args, arguments):
        ... prints the docopt text ...
    
    :param func: the function for the decorator
    '''
    classname = inspect.getouterframes(inspect.currentframe())[1][3]
    name = func.__name__
    help_name = name.replace("do_", "help_")
    doc = textwrap.dedent(func.__doc__)

    def new(instance, args):
                # instance.new.__doc__ = doc
        try:
            argv = shlex.split(args)
            arguments = docopt(doc, help=True, argv=argv)
            func(instance, args, arguments)
        except SystemExit:
            if args not in ('-h', '--help'):
                Console.error("Could not execute the command.")
            print(doc)
    new.__doc__ = doc
    return new
#
# DECORATOR: COMMAND
#


def function_command(main_func):
    def _function_command(func):
        # noinspection PySingleQuotedDocstring
        '''
                A decorator to create a function with docopt arguments. It also generates a help function

                @command
                def do_myfunc(self, args):
                    """ docopts text """
                    pass

                will create

                def do_myfunc(self, args, arguments):
                    """ docopts text """
                    ...

                def help_myfunc(self, args, arguments):
                    ... prints the docopt text ...

                :param func: the function for the decorator
                '''
        classname = inspect.getouterframes(inspect.currentframe())[1][3]
        name = func.__name__
        help_name = name.replace("do_", "help_")
        doc = textwrap.dedent(main_func.__doc__)

        def new(instance, args):
                    # instance.new.__doc__ = doc
            try:
                arguments = docopt(doc, help=True, argv=args)
                func(instance, args, arguments)
                # func.__doc__ = doc
            except SystemExit:
                if args not in ('-h', '--help'):
                    Console.error("Could not execute the command.")
                print(doc)
        new.__doc__ = doc
        return new
    return _function_command

#
# MAIN
#


def create_file(filename):
    """
    Creates a new file if the file name does not exists
    :param filename: the name of the file
    """

    expanded_filename = os.path.expanduser(os.path.expandvars(filename))
    if not os.path.exists(expanded_filename):
        open(expanded_filename, "a").close()


def create_dir(dir_path):
    """
    creates a director at the given path
    :param dir_path: the directory path
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def get_plugins_from_dir(dir_path, classbase):
    """dir_path/classbase/plugins"""

    if dir_path == "sys":
        dir_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'plugins'))
        dir_plugins = get_plugins(dir_path)
        return {"dir": dir_path, "plugins": dir_plugins, "class": classbase}

    if dir_path == ".":
        dir_path = os.path.expanduser(
            os.path.expandvars(os.path.join(os.getcwd(), 'plugins')))
        dir_plugins = get_plugins(dir_path)
        return {"dir": dir_path, "plugins": dir_plugins, "class": classbase}
    else:

        dir_path = os.path.expanduser(os.path.expandvars(dir_path))
        prefix = "{0}/{1}".format(dir_path, classbase)

        user_path = "{0}/plugins".format(prefix)

        create_dir(user_path)
        create_file("{0}/__init__.py".format(prefix))
        create_file("{0}/plugins/__init__.py".format(prefix))
        sys.path.append(os.path.expanduser(dir_path))
        dir_plugins = get_plugins(user_path)
        # pprint({"dir": dir_path, "plugins": dir_plugins, "class": classbase})
        return {"dir": dir_path, "plugins": dir_plugins, "class": classbase}


def get_plugins_from_module(name):
    cmd3_module = __import__(name)
    location = os.path.dirname(cmd3_module.__file__)
    package_location = os.path.dirname(location)
    class_name = os.path.basename(location)
    return dict(get_plugins_from_dir(package_location, class_name))


class plugin_manager:

    # TODO: verify, used to be just __init__():
    def __init__(self):
        plugins = []

    def add(self, plugin):
        plugins.append(plugin)


def main():
    """cm.

    Usage:
      cm [-q] help
      cm [-v] [-b] [--file=SCRIPT] [-i] [COMMAND ...]

    Arguments:
      COMMAND                  A command to be executed

    Options:
      --file=SCRIPT  -f  SCRIPT  Executes the script
      -i                 After start keep the shell interactive,
                         otherwise quit [default: False]
      -b                 surpress the printing of the banner [default: False]
    """

    echo = False
    
    try:
        arguments = docopt(main.__doc__, help=True)
        # fixing the help parameter parsing
        if arguments['help']:
            arguments['COMMAND'] = ['help']
            arguments['help'] = 'False'

        script_file = arguments['--file']
        interactive = arguments['-i']
        echo = arguments['-v']
        if echo:
            pprint(arguments)

    except:
        script_file = None
        interactive = False

        arguments = {'-b': True,
                     'COMMAND': [' '.join(sys.argv[1:])]}

    plugins = []

    plugins.append(dict(get_plugins_from_dir("sys", "cmd3")))
    # plugins.append(dict(get_plugins_from_dir("~/.cloudmesh", "cmd3local")))


    # if not os.path.exists(path_expand( "~/.cloudmesh/cmd3.yaml")):
    #     from cmd3.plugins.shell_core import create_cmd3_yaml_file
    #     create_cmd3_yaml_file()


    create_cmd3_yaml_file(force=False, verbose=False)
    filename = path_expand("~/.cloudmesh/cmd3.yaml")
    try:
        module_config = ConfigDict(filename=filename)
        modules = module_config["cmd3"]["modules"]
        properties = module_config["cmd3"]["properties"]
    except:
        modules = ['cloudmesh_cmd3.plugins']
    for module_name in modules:
        #print ("INSTALL", module_name)
        try:
            plugins.append(dict(get_plugins_from_module(module_name)))
        except:
            # print "WARNING: could not find", module_name
            pass

    # sys.exit()
    # plugins.append(dict(get_plugins_from_dir("~/.cloudmesh", "cmd3local")))
    
    # plugins.append(dict(get_plugins_from_dir (".", "dot")))

    for plugin in plugins:
        sys.path.append(os.path.expanduser(plugin['dir']))
    sys.path.append("../..")
    sys.path.append(".")
    sys.path.append("..")

    for plugin in plugins:
        plugin['class'] += ".plugins"

    # pprint(plugins)
    # pprint(sys.path)

    # sys.exit()
    name = "CmCli"

    #
    # not yet quite what i want, but falling back to a flatt array
    #

    (cmd, plugin_objects) = DynamicCmd(name, plugins)


    cmd.set_verbose(echo)
    cmd.activate()
    cmd.set_verbose(echo)

    cmd.set_debug(properties["debug"])

    if arguments['-b']:
        cmd.set_banner("")
    if script_file is not None:
        cmd.do_exec(script_file)

    if len(arguments['COMMAND']) > 0:
        try:            
            user_cmd = " ".join(arguments['COMMAND'])
            if echo:
                print(">", user_cmd)
            cmd.onecmd(user_cmd)
        except Exception as e:
            Console.error("")
            Console.error("ERROR: executing command '{0}'".format(user_cmd))
            Console.error("")
            print (70 * "=")
            print(e)
            print (70 * "=")
            print(traceback.format_exc())

        if interactive:
            cmd.cmdloop()
            
    elif not script_file or interactive:
        cmd.cmdloop()


def is_subcmd(opts, args):
    """if sys.argv[1:] does not match any getopt options,
    we simply assume it is a sub command to execute onecmd()"""

    if not opts and args:
        return True
    return False


def cmd3_call(f):
    """ calls a function defined with cmd3 arguments the function must be
        defined as f(arguments)"""
    
    arguments = docopt(f.__doc__)
    f(arguments)

if __name__ == "__main__":
    main()

