import logging
import os, re
from copy import deepcopy
from time import time
from waflib.Task import Task as BaseTask

class Rule(object):

    def __init__(self, group, config, file_in, file_out, token_in, token_out,
            depend_in, extra_out):
        self.conf = config or {}
        self.file_in = file_in or []
        self.file_out = file_out or []
        self.token_in = token_in or []
        self.token_out = token_out or []
        self.depend_in = depend_in or []
        self.extra_out = extra_out or []
        self.bld = group.context

        # token_out should only contain one item, can't really think of a
        # reason otherwise
        if len(self.token_out) > 1:
            self.bld.fatal('A rule may only produce one token')

        # expands wildcards (using ant_glob)
        for fs in (self.file_in, self.depend_in):
            self._expand_input_wilcards(fs)

        # normalize `replace_patterns`, must be a list
        replace_patterns = self.conf.get('replace_patterns', False)
        if replace_patterns and not is_non_string_iterable(replace_patterns):
            self.conf['replace_patterns'] = [replace_patterns]


    def _expand_input_wilcards(self, items):
        for_removal = []
        for_insertion = []
        for f in items:
            if not ('*' in f or '?' in f):
                continue
            for_removal.append(f)
            if os.path.isabs(f):
                paths = self.bld.root.ant_glob(f[1:])
                for_insertion += (node.abspath() for node in paths)
            else:
                paths = self.bld.path.ant_glob(f)
                for_insertion += (node.relpath() for node in paths)
        for f in for_removal:
            items.remove(f)
        items += for_insertion


    def _token_to_filename(self, token_name):
        if '/' in token_name:
            self.bld.fatal('Invalid token name: "%s"'% token_name)
        return os.path.join('.waf_flags_token',
            token_name.replace(':', '__'))


    @property
    def files(self):
        # returns the output files after being processes by this tool
        result = []
        if not self.file_out:
            return result
        for fo in self.file_out:
            is_dir = fo.endswith(os.path.sep)
            if is_dir:
                for fi in self.file_in:
                    foo = fi
                    replace_patterns = self.conf.get('replace_patterns', False)
                    if replace_patterns:
                        for (pat, rep) in replace_patterns:
                            foo = re.sub(pat, rep, foo)
                    basedir = self.conf.get('_source_basedir_', False)
                    if basedir:
                        basedir = expand_resource(self.group, basedir)
                    if basedir and foo.startswith(basedir):
                        foo = foo[len(basedir):]
                    else:
                        foo = os.path.basename(foo)
                    result.append(os.path.join(fo, foo))
            else:
                result.append(fo)
        for fo in self.extra_out:
            result.append(fo)
        return result

    @property
    def tokens(self):
        return self.token_out

    @property
    def rules(self):
        result = []
        token_in = [self._token_to_filename(t) for t in self.token_in]
        token_out = [self._token_to_filename(t) for t in self.token_out]

        if len(self.extra_out) and (len(self.file_out) > 1 or\
                (len(self.file_out) and self.file_out[0].endswith(
                os.path.sep))):
            self.bld.fatal('Cannot use extra_out with multiple file_out')

        for fo in self.file_out:
            if self.conf.get('_source_grouped_', False):
                result.append({
                    'file_in': self.file_in,
                    'file_out': [fo],
                    'token_in': token_in,
                    'token_out': token_out,
                    'depend_in': self.depend_in,
                    'extra_out': self.extra_out,
                })
                continue

            is_dir = fo.endswith(os.path.sep)
            for fi in self.file_in:
                if not is_dir:
                    result.append({
                        'file_in': [fi],
                        'file_out': [fo],
                        'token_in': token_in,
                        'token_out': token_out,
                        'depend_in': self.depend_in,
                        'extra_out': self.extra_out,
                    })
                    continue

                foo = fi
                replace_patterns = self.conf.get('replace_patterns', False)
                if replace_patterns:
                    for (pat, rep) in replace_patterns:
                        foo = re.sub(pat, rep, foo)
                # use basedir to produce file_out
                basedir = self.conf.get('_source_basedir_', False)
                if basedir and foo.startswith(basedir):
                    foo = foo[len(basedir):]
                else:
                    foo = os.path.basename(foo)
                result.append({
                    'file_in': [fi],
                    'file_out': [os.path.join(fo, foo)],
                    'token_in': token_in,
                    'token_out': token_out,
                    'depend_in': self.depend_in,
                    'extra_out': self.extra_out,
                })

        if len(self.file_out) == 0 and token_out:
            result.append({
                'file_in': self.file_in,
                'token_in': token_in,
                'token_out': token_out,
                'depend_in': self.depend_in,
                'extra_out': self.extra_out,
            })

        return result


class Group(object):
    name = None
    conf = None
    env  = None
    context = None
    group = None
    level = 1
    rule = None

    def __init__(self, name, group, **config):
        self.name = name
        self.conf = config
        if group is not None:
            self.group = group
            self.level = group.level + 1
            self.context = group.context
            data_merge(self.conf, group.conf)
        data_merge(self.conf, config)

    def get_name(self):
        names = [self.name]
        parent = self.group
        while parent:
            names.append(parent.name)
            parent = parent.group
        names.reverse()
        return ':'.join(names)
        
    def get_patterns(self):
        patterns = {}
        parent = self
        while parent:
            patterns['_%s' % parent.level] = parent.name
            parent = parent.group
        return patterns

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __call__(self, file_in=None, file_out=None, token_in=None,
            token_out=None, depend_in=None, extra_out=None, **config):
        bld = self.group.context
        try:
            task_class = bld.tools[self.name].Task
        except KeyError:
            bld.fatal('Unknown tool: ' + self.name)
        conf = {}
        data_merge(conf, self.conf)
        data_merge(conf, task_class.conf)
        data_merge(conf, config)

        self.rule = Rule(self, conf, file_in, file_out, token_in, token_out,
                depend_in, extra_out)
        for r in self.rule.rules:
            # cls = type(task_class)(name,(task_class),{
            #   group:self.group, config:conf, env: bld.env})
            task = task_class(self.group, conf, env=bld.env)
            for f in r.get('file_in', []):
                if os.path.isabs(f):
                    if not os.path.exists(f):
                        continue
                    node = bld.root.find_resource(f[1:])
                else:
                    node = bld.path.find_resource(f)
                assert node is not None, '"%s" does not exists' % f
                task.set_inputs(node)
            for f in r.get('depend_in', []):
                if os.path.isabs(f):
                    if not os.path.exists(f):
                        continue
                    node = bld.root.find_resource(f[1:])
                else:
                    node = bld.path.find_resource(f)
                assert node is not None, '"%s" does not exists' % f
                node.is_virtual_in = True
                task.set_inputs(node)
            for f in r.get('file_out', []):
                if f.startswith(os.path.sep):
                    # create outside files
                    f_dir = os.path.dirname(f)
                    try:
                        os.makedirs(f_dir)
                    except OSError:
                    #except FileExistsError:
                        pass
                    f_node = bld.root.find_dir(f_dir)
                    task.set_outputs(f_node.make_node(os.path.basename(f)))
                else:
                    task.set_outputs(bld.path.find_or_declare(f))
            for f in r.get('extra_out', []):
                if f.startswith(os.path.sep):
                    # create outside files
                    f_dir = os.path.dirname(f)
                    try:
                        os.makedirs(f_dir)
                    except OSError:
                    #except FileExistsError:
                        pass
                    f_node = bld.root.find_dir(f_dir)
                    f_node = f_node.make_node(os.path.basename(f))
                else:
                    f_node = bld.path.find_or_declare(f)
                f_node.is_virtual_out = True
                task.set_outputs(f_node)
            for f in r.get('token_in', []):
                node = bld.path.find_or_declare(f)
                node.is_virtual_in = True
                task.set_inputs(node)
            for f in  r.get('token_out', []):
                node = bld.path.find_or_declare(f)
                node.is_virtual_out = True
                task.set_outputs(node)
            bld.add_to_group(task)
        return self.rule


class Task(BaseTask):
    args = None
    conf = {}
    group  = None
    file_in = None
    file_out = None
    name = None
    token_in = None
    token_out = None

    def __init__(self, group, config, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
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

        for node in self.inputs:
            path = node.abspath()
            if str(node.parent).startswith('.waf_flags_'):
                self.token_in.append(path)
            elif getattr(node, 'is_virtual_in', False):
                pass
            elif path in source_exclude:
                pass
            else:
                self.file_in.append(path)
        for node in self.outputs:
            if str(node.parent).startswith('.waf_flags_'):
                self.token_out.append(node.abspath())
            elif getattr(node, 'is_virtual_out', False):
                pass
            else:
                self.file_out.append(node.abspath())

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


# see http://stackoverflow.com/a/15836901
def data_merge(a, b):
    """merges b into a and return merged result

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen"""
    key = None
    # ## debug output
    # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
    try:
        #if a is None or isinstance(a, str) or isinstance(a, unicode) or isinstance(a, int) or isinstance(a, long) or isinstance(a, float):
        if a is None or isinstance(a, str) or isinstance(a, int) or isinstance(a, float):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                for c in b:
                    if not c in a:
                        a.append(c)
            elif not b in a:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise Exception('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise Exception('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError as e:
        raise Exception('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a


def is_non_string_iterable(data):
    # http://stackoverflow.com/a/17222092
    try:
        if isinstance(data, unicode) or isinstance(data, str):
            return False
    except NameError:
        pass
    if isinstance(data, bytes):
        return False
    try:
        iter(data)
    except TypeError:
        return False
    try:
        hasattr(None, data)
    except TypeError:
        return True
    return False
    #
    #try:
    #    iter(data) # this should raise TypeError if not
    #    return not isinstance(data, types.StringTypes)
    #except TypeError:  pass
    #return False

def expand_resource(group, path):
    bld = group.context
    path = path.format(**group.get_patterns())
    if os.path.isabs(path):
        if path.endswith(os.path.sep):
            node = bld.root.find_dir(path[1:])
        else:
            node = bld.root.find_resource(path[1:])
        if node:
            return node.abspath()
    else:
        if path.endswith(os.path.sep):
            node = bld.path.find_dir(path)
        else:
            node = bld.path.find_resource(path)
        if node:
            return node.abspath()


def make_list(items, nodict=False):
    if items is None:
        return []
    elif not is_non_string_iterable(items):
        return [items]
    elif nodict and isinstance(items, dict):
        return [items]
    else:
        return items
