import signal
from os import path
from pickle import loads as pickle_load, dumps as pickle_dump
from PyBuildTool.utils.common import get_config_filename, read_config
from subprocess import call as subprocess_call
from threading import Thread, Lock
from time import sleep
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


storage = {
    'build_state': {
        'rebuild': True,
        'reset': False,
    },
    'build_state_lock': Lock(),
    'process_running': True,
}


def signal_handler(signum, frame):
    global storage
    storage['process_running'] = False

def run_build_thread_callback(self):
    global storage
    while storage['process_running']:
        if storage['build_state']['rebuild']:
            self.perform_build()
        sleep(5)

def process_build_files(stage, filetype, cwd, alias=''):
    # TODO: with alias set, we only build the targets under that alias,
    # um, forgot to also update targets which depends on this alias
    # target, this needs much better management of dependencies.
    cmd = ' '.join([
        'scons',
        '--stage=%s' % stage,
        '--filetype=%s' % filetype,
        #alias,
    ])
    subprocess_call(cmd, cwd=cwd, shell=True)


class OnFileModifiedHandler(PatternMatchingEventHandler):
    def __init__(self, stage, filetype, alias, patterns, reset=False):
        self.alias = alias
        self.filetype = filetype
        self.stage = stage
        self.reset = reset
        super(OnFileModifiedHandler, self).__init__(patterns=patterns)

    def on_modified(self, event):
        global storage
        with storage['build_state_lock']:
            if self.reset:
                storage['build_state']['reset'] = True
            key = pickle_dump((self.stage, self.filetype, self.alias))
            storage['build_state'][key] = True
            storage['build_state']['rebuild'] = True


class Watch(object):
    notifier = Observer()


    def __init__(self, env, root_dir, stage, filetype):
        self.env = env
        self.root_dir = root_dir
        self.stage = stage
        self.filetype = filetype

    def main_config_modified(self):
        self.notifier.unschedule_all()
        self.setup()

    def setup(self):
        config_file = get_config_filename(root=self.root_dir,
                                          stage=self.stage,
                                          filetype=self.filetype)
        config = read_config(basefilename=config_file[0],
                             filetype=config_file[1],
                             env=self.env, root_dir=self.root_dir)

        self.notifier.schedule(
            OnFileModifiedHandler(
                stage=self.stage,
                filetype=self.filetype,
                alias='',
                patterns=[path.join(self.root_dir, '.'.join(config_file))],
                reset=True,
            ),
            self.root_dir,
        )
        for tool_name in config:
            for group_name in config[tool_name]:
                group = config[tool_name][group_name]

                group_alias = '%s:%s' % (tool_name, group_name)
                
                items = group.get('items', [])
                if not isinstance(items, list):
                    items = [items]

                for item in items:
                    # only monitor files marked with _source_sandboxed_==False
                    if 'options' not in group:
                        continue
                    if group['options'].get('_source_sandboxed_', True):
                        continue

                    # reconstruct files into list
                    if not isinstance(item['file-in'], list):
                        item['file-in'] = [item['file-in']]

                    for src_file in (path.join(self.root_dir, src)
                                     for src in item['file-in']):
                        self.notifier.schedule(
                            OnFileModifiedHandler(
                                stage=self.stage,
                                filetype=self.filetype,
                                alias=group_alias,
                                patterns=[src_file],
                            ),
                            path.dirname(src_file),
                        )


    def perform_build(self):
        global storage
        with storage['build_state_lock']:
            for key in storage['build_state']:
                if not storage['build_state'][key]:
                    continue
                storage['build_state'][key] = False
                if key == 'reset':
                    self.main_config_modified()
                    continue
                elif key == 'rebuild':
                    continue
                stage, filetype, alias = pickle_load(key)
                process_build_files(stage, filetype, self.root_dir, alias)

    def run(self):
        global storage
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        process_build_files(self.stage, self.filetype, self.root_dir)
        print('We are WATCHING your every moves ...')
        self.setup()
        self.notifier.start()
        worker_thread = Thread(target=run_build_thread_callback,
                               args=(self,))
        worker_thread.start()
        while storage['process_running']:
            try:
                sleep(1)
            except Exception as e:
                storage['process_running'] = False
                print(e)
        self.notifier.stop()
        self.notifier.join()
        worker_thread.join()
