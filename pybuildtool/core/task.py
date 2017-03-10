import os
from copy import deepcopy
from time import time
from uuid import uuid4
from waflib.Task import Task as BaseTask # pylint:disable=import-error

from pybuildtool.misc.collections import make_list
from pybuildtool.misc.path import expand_resource

class Task(BaseTask):

    args = None
    conf = None
    group = None
    file_in = None
    file_out = None
    name = None
    token_in = None
    token_out = None

    _id = None

    def __init__(self, group, config, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self._id = uuid4().hex

        # Task's configuration can be declared higher in the build tree,
        # but it needs to be prefixed with its tool-name.
        # Tool-name however can only be defined by the tool's module by
        # observing predefined `__name__` variable, which value is the name
        # of the tool's module.
        if config:
            my_config = deepcopy(config)
            if self.name:
                name = self.name + '_'
                for key in config.keys():
                    if not key.startswith(name):
                        continue
                    task_conf = key[len(name):]
                    if task_conf in config:
                        continue
                    my_config[task_conf] = config[key]
        else:
            my_config = {}
        self.args = []
        self.conf = my_config
        self.group = group
        self.file_in = []
        self.file_out = []
        self.token_in = []
        self.token_out = []


    def prepare(self):
        pass


    def prepare_args(self):
        return []


    def prepare_shadow_jutsu(self):
        source_exclude = []
        for f in make_list(self.conf.get('_source_excluded_')):
            nodes = expand_resource(self.group, f)
            source_exclude += make_list(nodes)

        task_uid = self._id

        for node in self.inputs:
            path = node.abspath()
            if node.parent.name.startswith('.waf_flags_'):
                self.token_in.append(path)
            elif getattr(node, 'is_virtual_in_' + task_uid, False):
                pass
            elif path in source_exclude:
                pass
            else:
                self.file_in.append(path)

        for node in self.outputs:
            path = node.abspath()
            if node.parent.name.startswith('.waf_flags_'):
                self.token_out.append(path)
            elif getattr(node, 'is_virtual_out_' + task_uid, False):
                pass
            else:
                self.file_out.append(path)


    def finalize_shadow_jutsu(self, use_file_out=False):
        if use_file_out:
            filenames = self.file_out
        else:
            filenames = self.token_out
        for filename in filenames:
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError:
                pass
            with open(filename, 'w') as f:
                f.write(str(time()))


    def run(self):
        self.prepare_shadow_jutsu()
        self.prepare()
        ret = self.perform()
        if ret == 0:
            self.finalize_shadow_jutsu()
        return ret
