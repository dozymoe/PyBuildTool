import os
from pybuildtool.misc.resource import get_source_files
from subprocess import call
import sys
from time import sleep
import yaml

from .file_observer import FileObserver

class Application(object):

    bld = None
    observer = None

    rebuild = True
    reload = True
    running = True

    config_file = None
    sysargs = None

    def __init__(self, bld):
        self.bld = bld
        self.watchers = {}
        self.config_file = os.path.realpath(os.path.join(bld.path.abspath(),
                'build.yml'))

        self.sysargs = sys.argv[:]
        # Something from [fireh_runner](https://github.com/dozymoe/fireh_runner],
        # when running under PYTHONUSERBASE, let's use approriate python binary.
        python_bin = os.environ.get('PYTHON_BIN')
        if python_bin:
            self.sysargs.insert(0, python_bin)

        for ii in range(1, len(self.sysargs)):
            if self.sysargs[ii] == 'watch' or\
                    self.sysargs[ii].startswith('watch_'):

                self.sysargs[ii] = self.sysargs[ii].replace('watch',
                        'build', 1)
                break

        self.observer = FileObserver(self)


    def run(self):
        while self.running:
            if self.reload:
                self.do_reload()

            if self.rebuild:
                self.rebuild = False
                # On windows we'd be using waf.bat
                use_shell = os.name == 'nt'
                call(self.sysargs, shell=use_shell)

            count = 0
            while count < 10 and self.running:
                count += 1
                sleep(1)

        print('Closing files observers..')
        self.observer.close()


    def do_reload(self):
        self.reload = False
        self.observer.close()

        with open(self.config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        self.observer.open(list(os.path.realpath(f) for f in\
                get_source_files(config, self.bld)))

        self.rebuild = True


    def stop(self, *args):
        self.running = False
