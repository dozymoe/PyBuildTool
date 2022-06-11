import os
import subprocess
import sys

def expand_resource(group, path):
    """Get real path of a resource."""

    bld = group.context
    # replacement pattern, {_N} will be replaced with group name of level N
    path = path.format(**group.get_patterns())
    path = os.path.expanduser(path)
    if os.path.isabs(path):
        if path.endswith(os.path.sep):
            node = bld.root.find_dir(path.lstrip('/'))
        else:
            node = bld.root.find_resource(path.lstrip('/'))
        if node:
            return node.abspath()
    else:
        if path.endswith(os.path.sep):
            node = bld.path.find_dir(path)
        else:
            node = bld.path.find_resource(path)
        if node:
            return node.abspath()
    return None


def expand_wildcard(group, path, **kwargs):
    """Get real path of a resource."""
    bld = group.context
    # replacement pattern, {_N} will be replaced with group name of level N
    path = path.format(**group.get_patterns())
    if '*' in path or '?' in path:
        # waf counts maxdepth from the root directory but we want it relative
        # to the wildcard template
        maxdepth = kwargs.get('maxdepth', 25)
        depth = path.rstrip(os.path.sep).count(os.path.sep)
        if os.path.isabs(path):
            files = [node.abspath() for node in\
                    bld.root.ant_glob(path.lstrip('/'),
                    maxdepth=depth + maxdepth)]
        else:
            depth += bld.out_dir.count(os.path.sep) + 1
            files = [node.abspath() for node in bld.path.ant_glob(path,
                    maxdepth=depth + maxdepth)]
        if path.endswith(os.path.sep):
            dirnames = set()
            for filename in files:
                dirnames.add(os.path.dirname(filename))
            files = list(dirnames)
        return files

    path = os.path.expanduser(path)
    if os.path.isabs(path):
        if path.endswith(os.path.sep):
            node = bld.root.find_dir(path.lstrip('/'))
        else:
            node = bld.root.find_resource(path.lstrip('/'))
        if node:
            return [node.abspath()]

    else:
        if path.endswith(os.path.sep):
            node = bld.path.find_dir(path)
        else:
            node = bld.path.find_resource(path)
        if node:
            return [node.abspath()]

    return []


def PATH(path):
    if sys.platform in ('cygwin', 'msys'):
        unix_path = subprocess.check_output(['cygpath', '-u', path])
        return unix_path.decode().rstrip()

    return path
