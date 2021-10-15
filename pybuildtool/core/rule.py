from hashlib import md5
import os
import re
#-
from ..misc.path import expand_resource


def token_to_filename(token_name, bld):
    return os.path.join(bld.variant_dir, '.tokens',
            token_name.replace('/', '__'))


class Rule():

    def __init__(self, group, config, file_in, file_out, depend_in, extra_out):
        self.conf = config or {}
        self.file_in = file_in or []
        self.file_out = file_out or []
        self.depend_in = depend_in or []
        self.extra_out = extra_out or []
        self.group = group
        self.bld = group.context

        # expands wildcards (using ant_glob)
        for fs in (self.file_in, self.depend_in):
            self._expand_input_wilcards(fs)

        # normalize `_replace_patterns_`, must be a list of list
        self.conf.setdefault('_replace_patterns_', [])


    def _expand_input_wilcards(self, items):
        for_removal = []
        for_insertion = []
        for f in items:
            if not ('*' in f or '?' in f):
                continue
            for_removal.append(f)
            if os.path.isabs(f):
                paths = self.bld.root.ant_glob(f.lstrip('/'))
                for_insertion += (node.abspath() for node in paths)
            else:
                paths = self.bld.path.ant_glob(f)
                for_insertion += (node.relpath() for node in paths)
        for f in for_removal:
            items.remove(f)
        items += for_insertion


    def _extra_plus_token(self, file_out=None):
        for f in self.extra_out:
            yield f

        token_out = token_to_filename(self.group.get_name(), self.bld)
        if file_out:
            if hasattr(file_out, 'encode'):
                token_out += '-' + md5(file_out.encode()).hexdigest()
            else:
                token_out += '-' + md5(file_out).hexdigest()

        group_name = self.group.get_name()
        try:
            token_names = self.bld._token_names[group_name]
        except KeyError:
            token_names = []
            self.bld._token_names[group_name] = token_names
        except AttributeError:
            token_names = []
            self.bld._token_names = {group_name: token_names}
        token_names.append(token_out)

        yield token_out


    @property
    def files(self):
        # returns the output files after being processes by this tool
        result = []
        #if not self.file_out:
        #    return result

        for fo in self.file_out:
            is_dir = fo.endswith(os.path.sep)
            if is_dir:
                for fi in self.file_in:
                    fofi = fi
                    for (pat, rep) in self.conf['_replace_patterns_']:
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
    def rules(self):
        result = []

        if self.extra_out and (len(self.file_out) > 1 or\
                (self.file_out and self.file_out[0].endswith(
                os.path.sep))):

            self.bld.fatal('Cannot use extra_out with multiple file_out')

        for fo in self.file_out:
            if not self.file_in:
                # okay this is weird, no file_in but there is a file_out
                # it is possible though, but shouldn't you use extra_out?
                result.append({
                    'file_in': self.file_in,
                    'file_out': [fo],
                    'depend_in': self.depend_in,
                    'extra_out': self._extra_plus_token(fo),
                })
                continue

            if self.conf.get('_source_grouped_', False):
                result.append({
                    'file_in': self.file_in,
                    'file_out': [fo],
                    'depend_in': self.depend_in,
                    'extra_out': self._extra_plus_token(fo),
                })
                continue

            is_dir = fo.endswith(os.path.sep)
            for fi in self.file_in:
                if not is_dir:
                    result.append({
                        'file_in': [fi],
                        'file_out': [fo],
                        'depend_in': self.depend_in,
                        'extra_out': self._extra_plus_token(fo),
                    })
                    continue

                fofi = fi
                for (pat, rep) in self.conf['_replace_patterns_']:
                    fofi = re.sub(pat, rep, fofi)
                # use basedir to produce file_out
                basedir = self.conf.get('_source_basedir_', False)
                if basedir:
                    basedir = expand_resource(self.group, basedir)
                if basedir and fofi.startswith(basedir):
                    fofi = fofi[len(basedir):].strip('/')
                else:
                    fofi = os.path.basename(fofi)

                fofi = os.path.join(fo, fofi)
                result.append({
                    'file_in': [fi],
                    'file_out': [fofi],
                    'depend_in': self.depend_in,
                    'extra_out': self._extra_plus_token(fofi),
                })

        if not self.file_out:
            result.append({
                'file_in': self.file_in,
                'depend_in': self.depend_in,
                'extra_out': self._extra_plus_token(),
            })

        return result
