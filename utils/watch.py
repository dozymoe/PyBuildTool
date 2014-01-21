from os import path
from PyBuildTool.utils.common import get_config_filename, read_config
from pyinotify import (ALL_EVENTS, IN_MODIFY, Notifier, ProcessEvent,
                       WatchManager)
from subprocess import call as subprocess_call
from time import time


class OnWriteHandler(ProcessEvent):
    class Meta:
        lastfired = {}

    def my_init(self, cwd, stage, filetype, alias):
        self.alias = alias
        self.cwd = cwd
        self.filetype = filetype
        self.stage = stage

    def process_IN_MODIFY(self, event):
        lastfired = self.Meta.lastfired.get(self.alias, 0)
        if time() - lastfired < 1:
            return
        self.Meta.lastfired[self.alias] = time()

        subprocess_call(['scons',
                         '--stage=%s' % self.stage,
                         '--filetype=%s' % self.filetype,
                         self.alias],
                        cwd=self.cwd, shell=True)


class Watch(object):
    class Meta:
        lastfired = 0

    def __init__(self, env, root_dir, stage, filetype):
        self.env = env
        self.root_dir = root_dir
        self.stage = stage
        self.filetype = filetype

        self.wm = WatchManager()
        self.notifier = Notifier(self.wm)

    def main_config_modified(self, event):
        if time() - self.Meta.lastfired < 1:
            return
        self.Meta.lastfired = time()

        for wd in self.wm.watches.keys():
            self.wm.del_watch(wd)
        subprocess_call(['scons',
                         '--stage=%s' % self.stage,
                         '--filetype=%s' % self.filetype],
                        cwd=self.root_dir, shell=True)
        self.setup()

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
                handler = OnWriteHandler(cwd=self.root_dir,
                                         stage=self.stage,
                                         filetype=self.filetype,
                                         alias=group_alias)
                
                for item in group['files']:
                    # only monitor files marked with _source_sandboxed_==False
                    if 'options' not in group:
                        continue
                    if group['options'].get('_source_sandboxed_', True):
                        continue

                    # reconstruct files into list
                    if not isinstance(item['src'], list):
                        item['src'] = [item['src']]

                    for src_file in (path.join(self.root_dir, src)
                                     for src in item['src']):
                        self.wm.add_watch(src_file, ALL_EVENTS,
                                          proc_fun=handler,
                                          do_glob=True, rec=True,
                                          auto_add=True)

    def run(self):
        print('We are WATCHING your every moves ...')
        self.setup()
        self.notifier.loop()
