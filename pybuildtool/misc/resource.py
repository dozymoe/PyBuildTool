import hashlib
import mmap
import os
import re
from ..core.group import Group
from .collections_utils import make_list

def get_filehash(filename):
    if not os.path.exists(filename):
        return None
    hasher = hashlib.sha1()
    with open(filename, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ) as mm:
            hasher.update(mm)
    return hasher.digest()


def get_source_files(conf, bld):
    """Collect raw file inputs."""
    groups = {}
    constant_regex = re.compile(r'^[A-Z_]+$')

    def parse_group(group_name, config, level):
        groups['_%s' % level] = group_name

        options = config.pop('options', {})
        if group_is_leaf(config, options):
            group_files = make_list(config.get('raw_file_in')) +\
                    make_list(config.get('raw_depend_in'))

            for f in group_files:
                f = f.format(**groups)
                if os.path.isabs(f):
                    yield f
                else:
                    yield os.path.join(bld.top_dir, f)

            return

        for subgroup in config:
            for f in parse_group(subgroup, config[subgroup], level + 1):
                yield f

    for group in conf:
        if constant_regex.match(group):
            continue

        for f in parse_group(group, conf[group], 1):
            yield f


def group_is_leaf(group, options):
    """The lowests in the group tree are the tools."""

    return any(x in group for x in ('file_in', 'raw_file_in', 'file_out',
            'raw_file_out', 'depend_in', 'raw_depend_in', 'extra_out',
            'raw_extra_out', 'rule_in'))\
            or options.get('_no_io_', False)


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
                file_list.append(f + os.path.sep)
            elif '*' in f or '?' in f:
                for node in bld.root.ant_glob(f.lstrip('/')):
                    file_list.append(node.abspath())
            else:
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
                for node in bld.root.ant_glob(f.lstrip('/')):
                    yield node.abspath()
            else:
                for node in bld.path.ant_glob(f):
                    yield node.relpath()


    def parse_group(group_name, config, level, parent_group):
        try:
            options = config.pop('options', {})
        except Exception as e:
            print((parent_group.get_name(), group_name, dict(config), level))
            raise e

        g = Group(group_name, parent_group, options)
        if parent_group is None:
            g.context = bld

        groups[g.get_name()] = g
        pattern = g.get_patterns()

        if group_is_leaf(config, options):
            original_file_in = make_list(config.get('file_in'))
            file_in = list(_parse_input_listing(original_file_in, pattern))
            _add_raw_files(make_list(config.get('raw_file_in')), file_in,
                    pattern)

            original_depend_in = make_list(config.get('depend_in'))
            depend_in = list(_parse_input_listing(original_depend_in, pattern))
            _add_raw_files(make_list(config.get('raw_depend_in')), depend_in,
                    pattern)

            original_file_out = make_list(config.get('file_out'))
            file_out = [x.format(**pattern) for x in original_file_out]
            _add_raw_files(make_list(config.get('raw_file_out')), file_out,
                    pattern)

            original_extra_out = make_list(config.get('extra_out'))
            extra_out = [x.format(**pattern) for x in original_extra_out]
            _add_raw_files(make_list(config.get('raw_extra_out')), extra_out,
                    pattern)

            rules_in = [x.format(**pattern) for x in make_list(
                    config.get('rule_in'))]

            for rule_in in rules_in:
                try:
                    token_names = bld._token_names[rule_in]
                    for f in token_names:
                        depend_in.append(f)
                except (KeyError, AttributeError):
                    print((parent_group.get_name(), group_name, dict(config),
                            level))

                    if hasattr(bld, '_token_names'):
                        bld.fatal("rule '%s' not found in: %s" % (rule_in,
                                ', '.join(bld._token_names.keys())))
                    else:
                        bld.fatal("rule '%s' not found" % rule_in +\
                                ", does it have *_in or *_out?")

            g(file_in=file_in, file_out=file_out, depend_in=depend_in,
                    extra_out=extra_out)
            return

        for subgroup in config:
            parse_group(subgroup, config[subgroup], level + 1, g)

    for group in conf:
        if constant_regex.match(group):
            continue
        parse_group(group, conf[group], 1, None)

    bld.task_gen_cache_names = groups
