from os import path


def get_config_filename(root, stage, filetype):
    """ oh my, there are several possibilities for our main
        configuration filename. """

    possible_types = ('py', 'yml') if filetype == 'auto' \
                     else (filetype,)
    possible_stage = ('.default', '') if stage == 'default' \
                     else ('.%s' % stage,)
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
