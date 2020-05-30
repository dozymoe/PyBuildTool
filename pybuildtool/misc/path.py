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


def expand_wildcard(group, path):
    """Get real path of a resource."""

    bld = group.context
    # replacement pattern, {_N} will be replaced with group name of level N
    path = path.format(**group.get_patterns())
    if '*' in path or '?' in path:
        if os.path.isabs(path):
            return [node.abspath() for node in\
                    bld.root.ant_glob(path.lstrip('/'))]
        return [node.abspath() for node in bld.path.ant_glob(path)]

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
