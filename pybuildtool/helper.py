import os
import re
from base import Group, is_non_string_iterable

# make dictionary loaded by yaml has order of dictionary keys equal to how it
# was written
# see http://stackoverflow.com/q/13297744/319817
import yaml
import yaml.constructor

try:
    # included in standard lib from Python 2.7
    from collections import OrderedDict
except ImportError:
    # try importing the backported drop-in replacement
    # it's available on PyPI
    from ordereddict import OrderedDict

class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


def prepare_targets(conf, bld):
    groups = {}
    constant_regex = re.compile(r'^[A-Z_]+$')

    def parse_group(group_name, group, level, parent_group):
        if 'options' in group:
            options = group['options']
            del group['options']
        else:
            options = {}

        is_leaf = 'file_in' in group or 'file_out' in group or \
            'token_in' in group or 'token_out' in group

        g = Group(group_name, parent_group, **options)
        if parent_group is None:
            g.context = bld

        groups[g.get_name()] = g
        pattern = g.get_patterns()
                
        if is_leaf:
            file_in = []
            raw_file_in = group.get('file_in', [])
            if not is_non_string_iterable(raw_file_in):
                raw_file_in = [raw_file_in]
            for f in raw_file_in:
                f = f.format(**pattern)
                if f.startswith('@'):
                    file_in += groups[f[1:]].rule.files
                    continue
                if not ('*' in f or '?' in f):
                    file_in.append(f)
                    continue
                # expands wildcards (using ant_glob)
                if os.path.isabs(f):
                    paths = bld.root.ant_glob(f[1:])
                    file_in += (node.abspath() for node in paths)
                else:
                    paths = bld.path.ant_glob(f)
                    file_in += (node.relpath() for node in paths)
            
            file_out = []
            raw_file_out = group.get('file_out', [])
            if not is_non_string_iterable(raw_file_out):
                raw_file_out = [raw_file_out]
            for f in raw_file_out:
                f = f.format(**pattern)
                file_out.append(f)

            token_in = []
            raw_token_in = group.get('token_in', [])
            if not is_non_string_iterable(raw_token_in):
                raw_token_in = [raw_token_in]
            for f in raw_token_in:
                f = f.format(**pattern)
                if f.startswith('@'):
                    token_in += groups[f[1:]].rule.tokens
                else:
                    token_in.append(f)

            token_out = []
            raw_token_out = group.get('token_out', [])
            if not is_non_string_iterable(raw_token_out):
                raw_token_out = [raw_token_out]
            for f in raw_token_out:
                f = f.format(**pattern)
                token_out.append(f)

            g(file_in=file_in, file_out=file_out, token_in=token_in,
                    token_out=token_out)
            return

        for subgroup in group:
            parse_group(subgroup, group[subgroup], level + 1, g)

    for group in conf:
        if constant_regex.match(group):
            continue
        parse_group(group, conf[group], 1, None)

    bld.task_gen_cache_names = groups


def get_source_files(conf, bld):
    files = []
    groups = {}
    constant_regex = re.compile(r'^[A-Z_]+$')

    def parse_group(group_name, group, level, sandboxed):
        groups['_%s' % level] = group_name

        if 'file_in' in group or 'file_out' in group or \
                'token_in' in group or 'token_out' in group:
            # is leaf
            if sandboxed or 'file_in' not in group:
                return

            if is_non_string_iterable(group['file_in']):
                group_files = group['file_in']
            else:
                group_files = [group['file_in']]

            for f in group_files:
                f = f.format(**groups)
                if f.startswith('@'):
                    continue
                if not ('*' in f or '?' in f):
                    files.append(os.path.realpath(f))
                    continue
                # expands wildcards (using ant_glob)
                if os.path.isabs(f):
                    paths = bld.root.ant_glob(f[1:])
                else:
                    paths = bld.path.ant_glob(f)
                files.extend(node.abspath() for node in paths)
            return
        
        for subgroup in group:
            if subgroup == 'options':
                continue
            sandboxed = 'options' in group[subgroup] and \
                group[subgroup]['options'].get('_source_sandboxed_',
                        sandboxed)

            parse_group(subgroup, group[subgroup], level + 1, sandboxed)

    for group in conf:
        if constant_regex.match(group):
            continue
        sandboxed = 'options' in conf[group] and \
            conf[group]['options'].get('_source_sandboxed_', True)
        parse_group(group, conf[group], 1, sandboxed)

    return files
