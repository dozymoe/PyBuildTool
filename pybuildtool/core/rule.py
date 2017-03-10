import os
import re
from pybuildtool.misc.collections import make_list
from pybuildtool.misc.path import expand_resource

class Rule(object):

    def __init__(self, group, config, file_in, file_out, token_in, token_out,
            depend_in, extra_out):

        self.conf = config or {}
        self.file_in = file_in or []
        self.file_out = file_out or []
        self.token_in = token_in or []
        self.token_out = token_out or []
        self.depend_in = depend_in or []
        self.extra_out = extra_out or []
        self.group = group
        self.bld = group.context

        # token_out should only contain one item, can't really think of a
        # reason otherwise
        if len(self.token_out) > 1:
            self.bld.fatal('A rule may only produce one token')

        # expands wildcards (using ant_glob)
        for fs in (self.file_in, self.depend_in):
            self._expand_input_wilcards(fs)

        # normalize `replace_patterns`, must be a list
        self.conf['replace_patterns'] = make_list(
                self.conf.get('replace_patterns'))


    def _expand_input_wilcards(self, items):
        for_removal = []
        for_insertion = []
        for f in items:
            if not ('*' in f or '?' in f):
                continue
            for_removal.append(f)
            if os.path.isabs(f):
                paths = self.bld.root.ant_glob(f[1:])
                for_insertion += (node.abspath() for node in paths)
            else:
                paths = self.bld.path.ant_glob(f)
                for_insertion += (node.relpath() for node in paths)
        for f in for_removal:
            items.remove(f)
        items += for_insertion


    def _token_to_filename(self, token_name):
        if '/' in token_name:
            self.bld.fatal('Invalid token name: "%s"'% token_name)

        return os.path.join('.waf_flags_token',
                token_name.replace(':', '__'))


    @property
    def files(self):
        # returns the output files after being processes by this tool
        result = []
        if not self.file_out:
            return result

        for fo in self.file_out:
            is_dir = fo.endswith(os.path.sep)
            if is_dir:
                for fi in self.file_in:
                    fofi = fi
                    replace_patterns = self.conf.get('replace_patterns', False)
                    if replace_patterns:
                        for (pat, rep) in replace_patterns:
                            fofi = re.sub(pat, rep, fofi)
                    basedir = self.conf.get('_source_basedir_', False)
                    if basedir:
                        basedir = expand_resource(self.group, basedir)
                    if basedir and fofi.startswith(basedir):
                        fofi = fofi[len(basedir):].strip('/')
                    else:
                        fofi = os.path.basename(fofi)
                    result.append(os.path.join(fo, fofi))
            else:
                result.append(fo)
        for fo in self.extra_out:
            result.append(fo)
        return result


    @property
    def tokens(self):
        return self.token_out


    @property
    def rules(self):
        result = []
        token_in = [self._token_to_filename(t) for t in self.token_in]
        token_out = [self._token_to_filename(t) for t in self.token_out]

        if len(self.extra_out) and (len(self.file_out) > 1 or\
                (len(self.file_out) and self.file_out[0].endswith(
                os.path.sep))):

            self.bld.fatal('Cannot use extra_out with multiple file_out')

        for fo in self.file_out:
            if self.conf.get('_source_grouped_', False):
                result.append({
                    'file_in': self.file_in,
                    'file_out': [fo],
                    'token_in': token_in,
                    'token_out': token_out,
                    'depend_in': self.depend_in,
                    'extra_out': self.extra_out,
                })
                continue

            is_dir = fo.endswith(os.path.sep)
            for fi in self.file_in:
                if not is_dir:
                    result.append({
                        'file_in': [fi],
                        'file_out': [fo],
                        'token_in': token_in,
                        'token_out': token_out,
                        'depend_in': self.depend_in,
                        'extra_out': self.extra_out,
                    })
                    continue

                fofi = fi
                replace_patterns = self.conf.get('replace_patterns', False)
                if replace_patterns:
                    for (pat, rep) in replace_patterns:
                        fofi = re.sub(pat, rep, fofi)
                # use basedir to produce file_out
                basedir = self.conf.get('_source_basedir_', False)
                if basedir:
                    basedir = expand_resource(self.group, basedir)
                if basedir and fofi.startswith(basedir):
                    fofi = fofi[len(basedir):].strip('/')
                else:
                    fofi = os.path.basename(fofi)
                result.append({
                    'file_in': [fi],
                    'file_out': [os.path.join(fo, fofi)],
                    'token_in': token_in,
                    'token_out': token_out,
                    'depend_in': self.depend_in,
                    'extra_out': self.extra_out,
                })

        if len(self.file_out) == 0 and token_out:
            result.append({
                'file_in': self.file_in,
                'token_in': token_in,
                'token_out': token_out,
                'depend_in': self.depend_in,
                'extra_out': self.extra_out,
            })

        return result
