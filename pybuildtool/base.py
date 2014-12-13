import os, re
from time import time
from waflib.Task import Task as BaseTask

class Rule(object):
    conf = None
    file_in = []
    file_out = []
    token_in = []
    token_out = []

    def __init__(self, group, config, file_in, file_out, token_in, token_out):
        self.conf = config
        self.file_in = file_in
        self.file_out = file_out
        self.token_in = token_in
        self.token_out = token_out
        # expands wildcards (using ant_glob)
        bld = group.context
        for_removal = []
        for_insertion = []
        for f in self.file_in:
            if not ('*' in f or '?' in f):
                continue
            for_removal.append(f)
            if os.path.isabs(f):
                paths = bld.root.ant_glob(f[1:])
                for_insertion += (node.abspath() for node in paths)
            else:
                paths = bld.path.ant_glob(f)
                for_insertion += (node.relpath() for node in paths)
        for f in for_removal:
            self.file_in.remove(f)
        self.file_in += for_insertion
        # `replace_patterns` must be a list
        replace_patterns = self.conf.get('replace_patterns', False)
        if replace_patterns and not is_non_string_iterable(replace_patterns):
            self.conf['replace_patterns'] = [replace_patterns]

    def _token_to_filename(self, token_name):
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
            if not self.conf.get('_target_sandboxed_', True):
                fo = os.path.realpath(fo)
            if is_dir:
                for fi in self.file_in:
                    foo = fi
                    replace_patterns = self.conf.get('replace_patterns', False)
                    if replace_patterns:
                        for (pat, rep) in replace_patterns:
                            foo = re.sub(pat, rep, foo)
                    result.append(os.path.join(fo, os.path.basename(foo)))
            else:
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
        for fo in self.file_out:
            is_dir = fo.endswith(os.path.sep)
            if not self.conf.get('_target_sandboxed_', True):
                fo = os.path.realpath(fo)
            if self.conf.get('_source_grouped_', False):
                result.append({
                    'file_in': self.file_in,
                    'file_out': [fo],
                    'token_in': token_in,
                    'token_out': token_out,
                })
            else:
                for fi in self.file_in:
                    if is_dir:
                        foo = fi
                        replace_patterns = self.conf.get('replace_patterns', False)
                        if replace_patterns:
                            for (pat, rep) in replace_patterns:
                                foo = re.sub(pat, rep, foo)
                        result.append({
                            'file_in': [fi],
                            'file_out': [os.path.join(fo, os.path.basename(foo))],
                            'token_in': token_in,
                            'token_out': token_out,
                        })
                    else:
                        result.append({
                            'file_in': [fi],
                            'file_out': [fo],
                            'token_in': token_in,
                            'token_out': token_out,
                        })
        if len(self.file_out) == 0 and token_out:
            result.append({
                'file_in': self.file_in,
                'token_in': token_in,
                'token_out': token_out,
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
            token_out=None, **config):
        bld = self.group.context
        task_class = bld.tools[self.name].Task
        conf = {}
        data_merge(conf, self.conf)
        data_merge(conf, task_class.conf)
        data_merge(conf, config)

        self.rule = Rule(self, conf, file_in, file_out, token_in, token_out)
        for r in self.rule.rules:
            # cls = type(task_class)(name,(task_class),{
            #   group:self.group, config:conf, env: bld.env})
            task = task_class(self.group, conf, env=bld.env)
            for f in r.get('file_in', []):
                if os.path.isabs(f):
                    if not os.path.exists(f):
                        continue
                    inp = bld.root.find_resource(f[1:])
                else:
                    inp = bld.path.find_resource(f)
                assert inp is not None, '"%s" does not exists' % f
                task.set_inputs(inp)
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
            if r.get('token_in', False):
                task.set_inputs([bld.path.find_or_declare(f) for f in r['token_in']])
            if r.get('token_out', False):
                task.set_outputs([bld.path.find_or_declare(f) for f in r['token_out']])
            bld.add_to_group(task)
        return self.rule


class Task(BaseTask):
    conf = {}
    group  = None
    file_in = None
    file_out = None
    token_in = None
    token_out = None

    def __init__(self, group, config, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self.conf = config
        self.group = group
        self.file_in = []
        self.file_out = []
        self.token_in = []
        self.token_out = []

    def prepare_args(self):
        return []

    def prepare_shadow_jutsu(self):
        bld = self.group.context
        source_exclude = []
        if '_source_excluded_' in self.conf:
            for f in self.conf['_source_excluded_']:
                f = f.format(**self.group.get_patterns())
                if os.path.isabs(f):
                    nodes = bld.root.ant_glob(f[1:])
                else:
                    nodes = bld.path.ant_glob(f)
                if nodes and len(nodes):
                    source_exclude += [n.abspath() for n in nodes]

        for node in self.inputs:
            path = node.abspath()
            if str(node.parent).startswith('.waf_flags_'):
                self.token_in.append(path)
            elif path in source_exclude:
                pass
            else:
                self.file_in.append(path)
        for node in self.outputs:
            if str(node.parent).startswith('.waf_flags_'):
                self.token_out.append(node.abspath())
            else:
                self.file_out.append(node.abspath())

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
                a.extend(b)
            else:
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
        if isinstance(obj, unicode):
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
