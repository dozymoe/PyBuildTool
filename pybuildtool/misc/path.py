import os

def expand_resource(group, path):
    """Get real path of a resource."""

    bld = group.context
    # replacement pattern, {_N} will be replaced with group name of level N
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
