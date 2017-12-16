""" Implements watchdog.
"""
import os
import re
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

class FileChangeHandler(FileSystemEventHandler):

    app = None
    file_patterns = None

    def __init__(self, app):
        super(FileChangeHandler, self).__init__()
        self.app = app
        self.file_patterns = []


    def on_any_event(self, event):
        if event.is_directory:
            return

        if event.src_path == self.app.config_file:
            self.app.reload = True

        else:
            filters = self.file_patterns
            for name in event.src_path.split(os.path.sep):
                filters = self.filter_reduce(name, filters)

            filters = [f for f in filters if len(f) == 0 or f[0] != '**']
            if len(filters):
                self.app.rebuild = True


    def set_files(self, files):
        self.file_patterns = [self.parse_pattern(f) for f in files]


    @staticmethod
    def parse_pattern(x):
        filter_ = []
        x = x.replace('\\', '/').replace('//', '/')
        if x.endswith('/'):
            x += '**'

        for k in x.split('/'):
            if k == '**':
                filter_.append(k)
            else:
                k = k.replace('.', '[.]').replace('*','.*').replace('?', '.').\
                        replace('+', '\\+')

                k = '^%s$' % k
                exp = re.compile(k)
                filter_.append(exp)

        return filter_


    @staticmethod
    def filter_reduce(name, filters):
        ret_filters = []
        for lst in filters:
            if not lst:
                pass
            elif lst[0] == '**':
                ret_filters.append(lst)
                if len(lst) > 1:
                    if lst[1].match(name):
                        ret_filters.append(lst[2:])
                else:
                    ret_filters.append([])
            elif lst[0].match(name):
                ret_filters.append(lst[1:])

        return ret_filters


class FileObserver(object):

    app = None
    observers = None
    handler = None

    def __init__(self, app):
        self.app = app
        self.observers = []
        self.handler = FileChangeHandler(app)


    def open(self, files):
        self.handler.set_files(files)

        dirnames = set()
        dirnames.add(os.path.dirname(self.app.config_file))

        for filename in files:
            while True:
                filename = os.path.dirname(os.path.realpath(filename))
                if os.path.exists(filename) or not filename:
                    break

            if filename:
                for dirname in dirnames:
                    if os.path.commonprefix([filename, dirname]) != dirname:
                        dirnames.add(filename)

        for dirname in dirnames:
            observer = Observer()
            observer.schedule(self.handler, dirname, recursive=True)
            observer.start()

            self.observers.append(observer)


    def close(self):
        for observer in self.observers:
            observer.stop()

        for observer in self.observers:
            observer.join()

        self.observers = []
