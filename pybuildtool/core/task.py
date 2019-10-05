import os
from copy import deepcopy
import stringcase
from time import time
from uuid import uuid4
from waflib.Task import Task as BaseTask # pylint:disable=import-error

from ..misc.collections_utils import make_list
from ..misc.path import expand_resource

class Task(BaseTask):

    args = None
    args_case = 'spinal'
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
            if node.parent.name == '.tokens':
                self.token_in.append(path)
            elif getattr(node, 'is_virtual_in_' + task_uid, False):
                pass
            elif path in source_exclude:
                pass
            else:
                self.file_in.append(path)

        for node in self.outputs:
            path = node.abspath()
            if node.parent.name == '.tokens':
                self.token_out.append(path)
            elif getattr(node, 'is_virtual_out_' + task_uid, False):
                pass
            else:
                self.file_out.append(path)


    def finalize_shadow_jutsu(self):
        for filename in self.token_out:
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


    def stringcase_arg(self, option):
        return getattr(stringcase, self.args_case + 'case')(option)


    def _add_arg(self, option, value, sep):
        if sep == ' ':
            self.args.append(option)
            self.args.append(value)
        else:
            self.args.append(option + sep + value)


    def add_bool_args(self, *options):
        for option in options:
            value = self.conf.get(option)
            if not value:
                continue

            option = '--' + self.stringcase_arg(option)
            self.args.append(option)


    def add_dict_args(self, *options, **kwargs):
        opt_val_sep = kwargs.get('opt_val_sep', '=')
        key_val_sep = kwargs.get('key_val_sep', '=')

        for option in options:
            if option not in self.conf:
                continue

            for key, value in self.conf[option].items():
                value = value.format(**self.group.get_patterns())
                item = key + key_val_sep + value
                self._add_arg(option, item, opt_val_sep)


    def add_int_args(self, *options, **kwargs):
        opt_val_sep = kwargs.get('opt_val_sep', '=')

        for option in options:
            try:
                value = int(self.conf.get(option))
            except (TypeError, ValueError):
                continue

            option = '--' + self.stringcase_arg(option)
            self._add_arg(option, str(value), opt_val_sep)


    def add_list_args_join(self, separator, *options, **kwargs):
        opt_val_sep = kwargs.get('opt_val_sep', '=')

        for option in options:
            values = make_list(self.conf.get(option))
            if not values:
                continue

            option = '--' + self.stringcase_arg(option)
            value = separator.join(x.format(**self.group.get_patterns())\
                    for x in values)

            self._add_arg(option, value, opt_val_sep)


    def add_list_args_multi(self, *options, **kwargs):
        opt_val_sep = kwargs.get('opt_val_sep', '=')

        for option in options:
            values = make_list(self.conf.get(option))
            if not values:
                continue

            option = '--' + self.stringcase_arg(option)
            for value in values:
                value = value.format(**self.group.get_patterns())

                self._add_arg(option, value, opt_val_sep)


    def add_path_args(self, *options, **kwargs):
        opt_val_sep = kwargs.get('opt_val_sep', '=')

        for option in options:
            value = self.conf.get(option)
            if value is None:
                continue

            option = '--' + self.stringcase_arg(option)
            value = expand_resource(self.group, value)
            self._add_arg(option, value, opt_val_sep)


    def add_path_list_args_join(self, separator, *options, **kwargs):
        opt_val_sep = kwargs.get('opt_val_sep', '=')

        for option in options:
            values = make_list(self.conf.get(option))
            if not values:
                continue

            option = '--' + self.stringcase_arg(option)
            value = separator.join(expand_resource(self.group, x)\
                    for x in values)

            self._add_arg(option, value, opt_val_sep)


    def add_path_list_args_multi(self, *options, **kwargs):
        opt_val_sep = kwargs.get('opt_val_sep', '=')

        for option in options:
            values = make_list(self.conf.get(option))
            if not values:
                continue

            option = '--' + self.stringcase_arg(option)
            for value in values:
                value = expand_resource(self.group, value)
                self._add_arg(option, value, opt_val_sep)


    def add_str_args(self, *options, **kwargs):
        opt_val_sep = kwargs.get('opt_val_sep', '=')

        for option in options:
            value = self.conf.get(option)
            if value is None:
                continue

            option = '--' + self.stringcase_arg(option)
            value = value.format(**self.group.get_patterns())
            self._add_arg(option, value, opt_val_sep)
