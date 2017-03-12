import os
from waflib.Logs import debug # pylint:disable=import-error
from pybuildtool.core.rule import Rule
from pybuildtool.misc.collections import data_merge

class Group(object):

    name = None
    conf = None
    env = None
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


    def __exit__(self, type_, value, traceback):
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
            task = task_class(self.group, conf, env=bld.env)
            task_uid = task._id

            for f in r.get('file_in', []):
                if os.path.isabs(f):
                    if not os.path.exists(f):
                        continue
                    node = bld.root.find_resource(f.lstrip('/'))
                else:
                    node = bld.path.find_resource(f)
                if node is None:
                    bld.fatal('Source file "%s" does not exist' % f)

                debug('%s:%s: %s', 'input', 'file_in', str(node))
                task.set_inputs(node)

            for f in r.get('depend_in', []):
                if os.path.isabs(f):
                    if not os.path.exists(f):
                        continue
                    node = bld.root.find_resource(f.lstrip('/'))
                else:
                    node = bld.path.find_resource(f)
                if node is None:
                    bld.fatal('"%s" does not exists' % f)
                setattr(node, 'is_virtual_in_' + task_uid, True)

                debug('%s:%s: %s', 'input', 'depend_in', str(node))
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
                    d_node = bld.root.find_dir(f_dir)
                    node = d_node.make_node(os.path.basename(f))
                else:
                    node = bld.path.find_or_declare(f)

                debug('%s:%s: %s', 'output', 'file_out', str(node))
                task.set_outputs(node)

            for f in r.get('extra_out', []):
                if f.startswith(os.path.sep):
                    # create outside files
                    f_dir = os.path.dirname(f)
                    try:
                        os.makedirs(f_dir)
                    except OSError:
                    #except FileExistsError:
                        pass
                    d_node = bld.root.find_dir(f_dir)
                    node = d_node.make_node(os.path.basename(f))
                else:
                    node = bld.path.find_or_declare(f)
                setattr(node, 'is_virtual_out_' + task_uid, True)

                debug('%s:%s: %s', 'output', 'extra_out', str(node))
                task.set_outputs(node)

            for f in r.get('token_in', []):
                node = bld.path.find_or_declare(f)
                setattr(node, 'is_virtual_in_' + task_uid, True)

                debug('%s:%s: %s', 'input', 'token_in', str(node))
                task.set_inputs(node)

            for f in  r.get('token_out', []):
                node = bld.path.find_or_declare(f)
                setattr(node, 'is_virtual_out_' + task_uid, True)

                debug('%s:%s: %s', 'output', 'token_out', str(node))
                task.set_outputs(node)

            bld.add_to_group(task)
        return self.rule
