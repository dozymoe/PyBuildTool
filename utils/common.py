from os import makedirs, path, sep
from SCons import Node
from time import time


def get_shadow_name_jutsu(name, nodetype, prefix):
    """
    out of the box we cannot have directory as target.
    so we hack around pretending to target a `.scons` file
    inside the directory.
    update the file so as to change its MD5 signature.
    """
    if nodetype is Node.FS.Dir:
        return path.join(
            prefix,
            '.scons_flags_dir',
            name.rstrip(sep),
        )
    elif nodetype is Node.Alias.Alias:
        return path.join(
            prefix, 
            '.scons_flags_alias',
            name.replace(':', '__'),
        )
    elif nodetype is Node.Python.Value:
        return path.join(
            prefix,
            '.scons_flags_value',
            name.replace(':', '__'),
        )
    return name


def update_shadow_jutsu(target, source, env, remove_source=True,
                        remove_target=False):

    shadow = env['SHADOWLIST'].read()
    
    kill_list = []
    for s in source:
        s_name = path.join(env['ROOT_DIR'], str(s))
        if s_name in shadow:
            s.attributes.ActualName = shadow[s_name]
            s.attributes.HasShadow = True
            # treat directory special.
            if not shadow[s_name].endswith(sep):
                kill_list.append(s)
        else:
            s.attributes.ActualName = s_name
            s.attributes.HasShadow = False

    if remove_source:
        for k in kill_list:
            source.remove(k)

    kill_list = []
    for t in target:
        t_name = path.join(env['ROOT_DIR'], str(t))
        if t_name in shadow:
            #t.set_precious()
            t.attributes.ActualName = shadow[t_name]
            t.attributes.HasShadow = True
            # treat directory special
            if not shadow[t_name].endswith(sep):
                kill_list.append(t)

            # change the shadow file's MD5 signature.
            dirname = path.dirname(str(t))
            if not path.exists(dirname):
                makedirs(dirname)
            #import pdb; pdb.set_trace()
            with open(str(t), 'w') as f:
                f.write(str(time()))
        else:
            t.attributes.ActualName = t_name
            t.attributes.HasShadow = False

    if remove_target:
        for k in kill_list:
            target.remove(k)


def from_source_node_get_original(node):
    """
    out of the box we cannot have directory as target.
    so we hack around pretending to target a `.scons` file
    inside the directory.
    update the file so as to change its MD5 signature.
    """
    if not hasattr(node.attributes, 'ActualName'):
        node.attributes.ActualName = str(node)
        return node

    node_ori = node.attributes.ActualFactory(node.attributes.ActualName)
    return node_ori


def from_target_node_get_original(node):
    """
    out of the box we cannot have directory as target.
    so we hack around pretending to target a `.scons` file
    inside the directory.
    update the file so as to change its MD5 signature.
    """
    node_ori = from_source_node_get_original(node)

    node_str = str(node)
    node_ori_str = str(node_ori)
   
    if node_str != node_ori_str:
        dirname = path.dirname(node_str)
        if not path.exists(dirname):
            makedirs(dirname)
        with open(node_str, 'w') as f:
            f.write(str(time()))

    return node_ori


def get_config_filename(root, stage, filetype):
    """ oh my, there are several possibilities for our main
        configuration filename. """

    possible_types = ('py', 'yml') if filetype == 'auto' \
                     else (filetype,)
    possible_stage = ('_default', '') if stage == 'default' \
                     else ('_%s' % stage,)
    possible_confs = (('SConsfile%s' % p_stage, p_type) \
                      for p_stage in possible_stage \
                      for p_type in possible_types)

    for p_conf in possible_confs:
        if path.lexists(path.join(root, '.'.join(p_conf))):
            return p_conf

    raise Exception('Missing configuration file (SConsfile.STAGE.EXT)')


def read_config(basefilename, filetype, env, root_dir):
    if filetype == 'py':
        # our config dictionary would be the module level variable
        # `build_config` inside SConsfile.STAGE.py

        from copy import deepcopy
        from importlib import import_module
        myconfig = import_module(basefilename)

        initfunc = getattr(myconfig, 'init', None)
        if initfunc is not None:
            initfunc(env)
        mybuildconfig = getattr(myconfig, 'build_config')

        return deepcopy(mybuildconfig)

    elif filetype == 'yml':
        # our config dictionary would be the whole contents of
        # SConsfile.STAGE.yml

        from yaml import safe_load as yaml_load
        return yaml_load(open(path.join(root_dir,
                                        '.'.join((basefilename,
                                                 filetype)))))
