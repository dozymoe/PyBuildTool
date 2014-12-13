import os
import signal
from threading import Thread
from time import sleep
from waflib import Context
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from yaml import load as yaml_load
from helper import get_source_files

conf_file = ''
files = []
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


def thread_callback():
    global rebuild
    while running:
        if rebuild:
            rebuild = False
            os.system('waf build_dev')
        sleep(10)


def watch_files(bld):
    with open(conf_file) as f:
        conf = yaml_load(f)
    files = get_source_files(conf, bld)
    files.append(conf_file)
    return files


def watch(bld):
    global files, conf_file, running
    conf_file = os.path.join(bld.path.abspath(), 'build_rules.yml') 
    files = watch_files(bld)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    event_handler = FileChangeHandler(bld)
    observer = Observer()
    observer.schedule(event_handler, bld.path.abspath(), recursive=True)
    observer.start()
    print('We are WATCHING your every moves ...')
    worker = Thread(target=thread_callback)
    worker.start()

    while running:
        try:
            sleep(1)
        except:
            running = False
    observer.stop()
    observer.join()
    worker.join()


Context.g_module.__dict__['watch'] = watch
