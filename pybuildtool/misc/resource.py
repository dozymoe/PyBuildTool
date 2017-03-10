import os
import re
from pybuildtool.core.group import Group
from pybuildtool.misc.collections import make_list

def get_source_files(conf, bld):
    """Collect raw file inputs."""

    files = []
    groups = {}
    constant_regex = re.compile(r'^[A-Z_]+$')

    def parse_group(group_name, group, level):
        groups['_%s' % level] = group_name

        if group_is_leaf(group):

            group_files = make_list(group.get('raw_file_in')) +\
                    make_list(group.get('raw_depend_in'))
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
            parse_group(subgroup, group[subgroup], level + 1)

    for group in conf:
        if constant_regex.match(group):
            continue
        parse_group(group, conf[group], 1)

    return files


def group_is_leaf(group):
    """The lowests in the group tree are the tools."""

    return any(x in group for x in ('file_in', 'raw_file_in', 'file_out',
            'raw_file_out', 'token_in', 'token_out', 'depend_in',
            'raw_depend_in', 'extra_out', 'raw_extra_out'))


def prepare_targets(conf, bld):
    """Create waf targets from predefined file input categories."""

    groups = {}
    constant_regex = re.compile(r'^[A-Z_]+$')

    def _add_raw_files(raw_file_list, file_list, pattern):
        for f in raw_file_list:
            f = f.format(**pattern)
            # because realpath() will remove the last path separator,
            # we need it to identify a directory
            is_dir = f.endswith(os.path.sep) or f.endswith('/')
            f = os.path.realpath(f)
            if is_dir and not f.endswith(os.path.sep):
                f += os.path.sep
            file_list.append(f)


    def _parse_input_listing(source_list, pattern):
        for f in source_list:
            f = f.format(**pattern)
            if f.startswith('@'):
                for x in groups[f[1:]].rule.files:
                    yield x
            elif not ('*' in f or '?' in f):
                yield f
            # expands wildcards (using ant_glob)
            elif os.path.isabs(f):
                for node in bld.root.ant_glob(f[1:]):
                    yield node.abspath()
            else:
                for node in bld.path.ant_glob(f):
                    yield node.relpath()


    def parse_group(group_name, group, level, parent_group):
        if 'options' in group:
            options = group['options']
            del group['options']
        else:
            options = {}

        g = Group(group_name, parent_group, **options)
        if parent_group is None:
            g.context = bld

        groups[g.get_name()] = g
        pattern = g.get_patterns()

        if group_is_leaf(group):
            original_file_in = make_list(group.get('file_in'))
            file_in = [x for x in _parse_input_listing(original_file_in,
                    pattern)]
            _add_raw_files(make_list(group.get('raw_file_in')), file_in,
                    pattern)

            original_depend_in = make_list(group.get('depend_in'))
            depend_in = [x for x in _parse_input_listing(original_depend_in,
                    pattern)]
            _add_raw_files(make_list(group.get('raw_depend_in')), depend_in,
                    pattern)

            original_file_out = make_list(group.get('file_out'))
            file_out = [x.format(**pattern) for x in original_file_out]
            _add_raw_files(make_list(group.get('raw_file_out')), file_out,
                    pattern)

            original_extra_out = make_list(group.get('extra_out'))
            extra_out = [x.format(**pattern) for x in original_extra_out]
            _add_raw_files(make_list(group.get('raw_extra_out')), extra_out,
                    pattern)

            original_token_in = make_list(group.get('token_in'))
            token_in = []
            for f in original_token_in:
                f = f.format(**pattern)
                if f.startswith('@'):
                    token_in += groups[f[1:]].rule.tokens
                else:
                    token_in.append(f)

            original_token_out = make_list(group.get('token_out'))
            token_out = [x.format(**pattern) for x in original_token_out]

            g(file_in=file_in, file_out=file_out, token_in=token_in,
                    token_out=token_out, depend_in=depend_in,
                    extra_out=extra_out)
            return

        for subgroup in group:
            parse_group(subgroup, group[subgroup], level + 1, g)

    for group in conf:
        if constant_regex.match(group):
            continue
        parse_group(group, conf[group], 1, None)

    bld.task_gen_cache_names = groups
