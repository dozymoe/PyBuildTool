from os import path
from pickle import loads as pickle_load, dumps as pickle_dump
from PyBuildTool.utils.common import get_config_filename, read_config
from pyinotify import (ALL_EVENTS, IN_MODIFY, ThreadedNotifier, ProcessEvent,
                       WatchManager)
from subprocess import call as subprocess_call
from time import sleep


build_state = {}


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


class OnWriteHandler(ProcessEvent):
    def my_init(self, stage, filetype, alias):
        self.alias = alias
        self.filetype = filetype
        self.stage = stage

    def process_IN_MODIFY(self, event):
        key = pickle_dump((self.stage, self.filetype, self.alias))
        build_state[key] = True



class Watch(object):
    wm = WatchManager()
    notifier = ThreadedNotifier(wm)


    def __init__(self, env, root_dir, stage, filetype):
        self.env = env
        self.root_dir = root_dir
        self.stage = stage
        self.filetype = filetype

    def main_config_modified(self, event):
        for wd in self.wm.watches.keys():
            self.wm.del_watch(wd)

        self.setup()
        key = pickle_dump((self.stage, self.filetype, ''))
        build_state[key] = True

    def setup(self):
        config_file = get_config_filename(root=self.root_dir,
                                          stage=self.stage,
                                          filetype=self.filetype)
        config = read_config(basefilename=config_file[0],
                             filetype=config_file[1],
                             env=self.env, root_dir=self.root_dir)

        self.wm.add_watch(path.join(self.root_dir, '.'.join(config_file)),
                          IN_MODIFY,
                          proc_fun=self.main_config_modified)

        for tool_name in config:
            for group_name in config[tool_name]:
                group = config[tool_name][group_name]

                group_alias = '%s:%s' % (tool_name, group_name)
                handler = OnWriteHandler(stage=self.stage,
                                         filetype=self.filetype,
                                         alias=group_alias)
                
                for item in group['items']:
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
                        self.wm.add_watch(src_file, ALL_EVENTS,
                                          proc_fun=handler,
                                          do_glob=True, rec=True,
                                          auto_add=True)


    def perform_build(self):
        for key in build_state:
            if not build_state[key]:
                continue
            build_state[key] = False
            stage, filetype, alias = pickle_load(key)
            process_build_files(stage, filetype, self.root_dir, alias)


    def run(self):
        process_build_files(self.stage, self.filetype, self.root_dir)
        print('We are WATCHING your every moves ...')
        self.setup()
        self.notifier.start()
        while True:
            try:
                sleep(2)
                self.perform_build()
            except:
                self.notifier.stop()
                break
