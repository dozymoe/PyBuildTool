import re
import types
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

                                        
# see http://stackoverflow.com/a/15836901
def data_merge(a, b):
    """merges b into a and return merged result

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen"""
    key = None
    # ## debug output
    # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
    try:
        if a is None or isinstance(a, str) or isinstance(a, unicode) or isinstance(a, int) or isinstance(a, long) or isinstance(a, float):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                a.extend(b)
            else:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise Exception('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise Exception('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError, e:
        raise Exception('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a


def is_non_string_iterable(data):
    try:
        iter(data) # this should raise TypeError if not
        return not isinstance(data, types.StringTypes)
    except TypeError:  pass
    return False


class Rule(object):
    group_file_in = False

    def __init__(self, rules, group, file_in, file_out=None, token_in=None,
                 token_out=None, replace_patterns=None):
        for o in group:
            setattr(self, o, group[o])
        self.file_in = file_in
        if not file_out is None:
            self.file_out = file_out
        if not token_in is None:
            self.token_in = token_in
        if not token_out is None:
            self.token_out = token_out
        if not replace_patterns is None:
            self.replace_patterns = replace_patterns

        data_merge(rules, self.rules)

    @property
    def files(self):
        # returns the output files after being processed by this tool
        if not hasattr(self, 'file_out'):
            return ()
        if is_non_string_iterable(self.file_in):
            file_ins = self.file_in
        else:
            file_ins = [self.file_in]
        if is_non_string_iterable(self.file_out):
            file_outs = self.file_out
        else:
            file_outs = [self.file_out]

        result = []
        for fo in file_outs:
            if fo.endswith(sep):
                for fi in file_ins:
                    if hasattr(self, 'replace_patterns'):
                        b = fi
                        for (pat, rep) in self.replace_patterns:
                            b = re.sub(pat, rep, b)
                    else:
                        b = path.basename(fi)
                    result.append(path.join(fo, b))
            else:
                result.append(fo)
        return result

    @property
    def tokens(self): return getattr(self, 'token_out')

    @property
    def tool_name(self):  return type(self).__name__.lower()

    @property
    def rules(self):
        # returns build rules
        t = self.tool_name
        result = {}
        result[t] = {}
        result[t][self.name] = {'items':[]}
        if hasattr(self, 'options'):
            result[t][self.name]['options'] = self.options

        if is_non_string_iterable(self.file_in):
            file_ins = self.file_in
        else:
            file_ins = [self.file_in]
        if not hasattr(self, 'file_out'):
            file_outs = ()
        elif is_non_string_iterable(self.file_out):
            file_outs = self.file_out
        else:
            file_outs = [self.file_out]
        if not hasattr(self, 'token_out'):
            token_outs = ()
        elif is_non_string_iterable(self.token_out):
            token_outs = self.token_out
        else:
            token_outs = [self.token_out]

        for fo in file_outs:
            if self.group_file_in:
                rule = {
                    'file-in': file_ins,
                    'file-out': fo,
                }
                if hasattr(self, 'token_in'):
                    rule['token-in'] = self.token_in
                result[t][self.name]['items'].append(rule)
            else:
                for fi in file_ins:
                    if fo.endswith(sep):
                        if hasattr(self, 'replace_patterns'):
                            b = fi
                            for (pat, rep) in self.replace_patterns:
                                b = re.sub(pat, rep, b)
                        else:
                            b = path.basename(fi)
                        rule = {
                            'file-in': fi,
                            'file-out': path.join(fo, b),
                        }
                    else:
                        rule = {
                            'file-in': fi,
                            'file-out': fo,
                        }
                    if hasattr(self, 'token_in'):
                        rule['token-in'] = self.token_in
                    result[t][self.name]['items'].append(rule)
        for to in token_outs:
            rule = {
                'file-in': file_ins,
                'token-out': to,
            }
            if hasattr(self, 'token_in'):
                rule['token-in'] = self.token_in
            result[t][self.name]['items'].append(rule)

        return result

