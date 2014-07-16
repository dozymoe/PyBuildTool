from glob import glob
from hashlib import md5
from os import makedirs, path, sep
from time import time


def silent_str_function(target, source, env):
    pass

def prepare_shadow_jutsu(name, nodetype, prefix):
    """
    out of the box we cannot have directory as target.
    so we hack around pretending to target a `.scons` file
    inside the directory.
    update the file so as to change its MD5 signature.
    """

    if nodetype == 'token':
        return path.join(
            prefix, 
            '.scons_flags_token',
            name.replace(':', '__'),
        )
    elif nodetype in ('dir',):
        hash_value = md5(name).hexdigest()
        # take the first 4 characters as directory name.
        flag_dir_name = hash_value[:4]
        flag_file_name = hash_value[4:]
        return path.join(
            prefix,
            '.scons_flags_%s' % nodetype,
            flag_dir_name,
            flag_file_name,
        )
    return name


def perform_shadow_jutsu(target, source, env):
    """
    out of the box we cannot have directory as target.
    so we hack around pretending to target a `.scons` file
    inside the directory.
    update the file so as to change its MD5 signature.
    """

    shadow = env['SHADOWLIST'].read()
    
    for s in source:
        s_name = path.join(env['ROOT_DIR'], str(s))
        if s_name in shadow:
            s.attributes.ItemName = shadow[s_name]
            s.attributes.HasShadow = True
            # treat directory special.
            if not shadow[s_name].endswith(sep):
                s.attributes.RealName = ''
            else:
                s.attributes.RealName = shadow[s_name]
            # expand glob
            if '*' in shadow[s_name]:
                glob_files = glob(shadow[s_name])
                for g in glob_files:
                    f = env.File(g)
                    f.attributes.ItemName = str(f)
                    f.attributes.RealName = str(f)
                    f.attributes.HasShadow = False
                    source.append(env.File(f))
        else:
            s.attributes.ItemName = s_name
            s.attributes.RealName = s_name
            s.attributes.HasShadow = False

    append_list = []
    for t in target:
        t_name = path.join(env['ROOT_DIR'], str(t))
        if t_name in shadow:
            t.set_precious()
            t.attributes.ItemName = shadow[t_name]
            t.attributes.HasShadow = True
            # treat directory special
            if not shadow[t_name].endswith(sep):
                t.attributes.RealName = ''
            else:
                t.attributes.RealName = shadow[t_name]
            # replace glob with its dirname
            if '*' in shadow[t_name]:
                dirname = path.dirname(shadow[t_name])
                if not path.exists(dirname):  makedirs(dirname)

                d = env.Dir(dirname)
                d.attributes.ItemName = dirname
                d.attributes.RealName = dirname
                d.attributes.HasShadow = False
                append_list.append(d)
        else:
            t.attributes.ItemName = t_name
            t.attributes.RealName = t_name
            t.attributes.HasShadow = False

    for a in append_list:
        target.append(a)


def finalize_shadow_jutsu(target, source, env):
    """
    out of the box we cannot have directory as target.
    so we hack around pretending to target a `.scons` file
    inside the directory.
    update the file so as to change its MD5 signature.
    """

    shadow = env['SHADOWLIST'].read()

    for t in target:
        t_name = path.join(env['ROOT_DIR'], str(t))
        if t_name in shadow:
            # change the shadow file's MD5 signature.
            dirname = path.dirname(t_name)
            if not path.exists(dirname):
                makedirs(dirname)
            with open(t_name, 'w') as f:
                f.write(str(time()))


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

    raise Exception('Missing configuration file (SConsfile_STAGE.EXT)')


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
