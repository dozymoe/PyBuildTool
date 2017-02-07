'''
Watch files for changes and run build

add option `browser-notifier`, see the tool `browser_reload_notifier`
'''
import os
import signal
from collections import OrderedDict
from threading import Thread
from time import sleep
from waflib import Context
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from yaml import load as yaml_load

from pybuildtool.misc.resource import get_source_files

conf_file = ''
files = []
browser_notifier = None
rebuild = True
running = True

class FileChangeHandler(FileSystemEventHandler):
    bld = None

    def __init__(self, bld):
        super(FileChangeHandler, self).__init__()
        self.bld = bld


    def on_any_event(self, event):
        global files, rebuild
        if event.is_directory:
            return
        if event.src_path in files:
            rebuild = True
            if event.src_path == conf_file:
                files = watch_files(self.bld)


def signal_handler(signum, frame):
    global running
    running = False


def thread_callback(context):
    global rebuild
    while running:
        if rebuild:
            rebuild = False
            os.system(' '.join([
                'waf',
                # my build tool is broken ;(
                # I dunno why but the targets are not rebuild when missing,
                # always clean before build for now
                #'clean_%s' % context.variant,
                'build_%s' % context.variant,
                '--jobs=%s' % context.options.jobs,
            ]))
            if browser_notifier:
                browser_notifier.trigger()
        sleep(10)


def watch_files(bld):
    with open(conf_file) as f:
        conf = yaml_load(f)
    files = get_source_files(conf, bld)
    files.append(conf_file)
    # see http://stackoverflow.com/a/17016257
    return list(OrderedDict.fromkeys(os.path.realpath(f) for f in files))


def watch(bld):
    global browser_notifier, files, conf_file, running
    conf_file = os.path.join(bld.path.abspath(), 'build.yml') 
    files = watch_files(bld)

    if bld.options.browser_notifier:
        from pybuildtool.addons.watch_files.browser_reload_notifier import\
                BrowserReloadNotifier

        browser_notifier = BrowserReloadNotifier('0.0.0.0')

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if browser_notifier:
        browser_notifier.start()
    event_handler = FileChangeHandler(bld)
    observer = Observer()
    observer.schedule(event_handler, bld.path.abspath(), recursive=True)
    observer.start()
    print('We are WATCHING your every moves ...')
    worker = Thread(target=thread_callback, kwargs={'context': bld})
    worker.start()

    while running:
        try:
            sleep(1)
        except:
            running = False
    observer.stop()
    observer.join()
    worker.join()
    if browser_notifier:
        browser_notifier.stop()


def options(opt):
    opt.add_option('--browser-notifier', action='store_true', default=False,
            help='watch command will also start browser notifier')


Context.g_module.__dict__['watch'] = watch
