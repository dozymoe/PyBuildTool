'''
Watch files for changes and run build

add option `browser-notifier`, see the tool `browser_reload_notifier`
'''
import signal
from waflib import Context # pylint:disable=import-error

from .application import Application
from .file_observer import FileObserver


def watch(bld):
    app = Application(bld)
    signal.signal(signal.SIGINT, app.stop)
    signal.signal(signal.SIGTERM, app.stop)

    print('We are WATCHING your every moves ...')
    app.run()


Context.g_module.__dict__['watch'] = watch
