"""
Lint reStructuredText files.

Options:

    * encoding         : str, 'utf-8'
                         File encoding, argument to python open()
    * ignore_directives: list, []
                         Ignore errors about unknown directives.
    * ignore_roles     : list, []
                         Ignore errors about unknown roles.

Requirements:

    * pygments
      to install, run `pip install pygments`
    * restructuredtext-lint
      to install, run `pip install restructuredtext-lint`

"""
import os
import re
from pybuildtool import BaseTask, make_list

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    encoding = None
    regex_ignores = None

    def prepare(self):
        cfg = self.conf

        # Encoding of the input file (e.g. utf-8)
        self.encoding = cfg.get('encoding', 'utf-8')

        self.regex_ignores = []

        # Ignore unknown directives
        unknown = make_list(cfg.get('ignore_directives'))
        if unknown:
            self.regex_ignores.append(re.compile('^Unknown directive type "(' +\
                    '|'.join(unknown) + ')".*'))

            self.regex_ignores.append(re.compile('^No directive entry for "(' +\
                    '|'.join(unknown) + ')".*'))

        # Ignore unknown roles
        unknown = make_list(cfg.get('ignore_roles'))
        if unknown:
            self.regex_ignores.append(re.compile('^Unknown interpreted text ' +\
                    'role "(' + '|'.join(unknown) + ')".*'))

            self.regex_ignores.append(re.compile('^No role entry for "(' +\
                    '|'.join(unknown) + ')".*'))


    def perform(self):
        from restructuredtext_lint import lint_file # pylint:disable=import-error,import-outside-toplevel

        result = 0
        for filename in self.file_in:
            errors = lint_file(filename, encoding=self.encoding)
            if not errors:
                continue

            relpath = os.path.relpath(filename)
            if relpath.startswith('.'):
                relpath = filename

            print_filename = True
            for error in errors:
                ignored = False
                for re_ignore in self.regex_ignores:
                    if re_ignore.match(error.message):
                        ignored = True
                        break

                if ignored:
                    continue

                if print_filename:
                    print('************* File ' + relpath)
                    print_filename = False

                if error.level > 2:
                    result += 1

                message = error.message.replace('\n', ' ')
                print('%s: %i: %s' % (error.type[0], error.line, message))

        return result


def configure(conf):
    conf.start_msg("Checking for python module '%s'" % tool_name)
    try:
        import restructuredtext_lint # pylint:disable=unused-import,unused-variable,import-outside-toplevel
    except ImportError:
        conf.end_msg('not found', color='YELLOW')
