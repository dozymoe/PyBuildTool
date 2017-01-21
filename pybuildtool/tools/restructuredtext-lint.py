"""
Lint reStructuredText files.

Options:

    * format : str, None, report format (text, json)
    * encoding: str, None, file encoding (utf-8)

Requirements:

    * pygments
      to install, run `pip install pygments`
    * restructuredtext-lint
      to install, run `pip install restructuredtext-lint`

"""

from pybuildtool.core.task import Task as BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        # Format of the output (e.g. text, json)
        c = cfg.get('format', None)
        if c:
            args.append('--format=' % c)

        # Encoding of the input file (e.g. utf-8)
        c = cfg.get('encoding', None)
        if c:
            args.append('--encoding=' % c)


    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=' '.join(self.file_in),
        ))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program(tool_name)[0]
