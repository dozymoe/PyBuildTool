"""
gzip compress files.

Requirements:

    * gzip

"""
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_replace_patterns_': ((r'$', '.gz'),),
    }
    name = tool_name

    def prepare(self):
        self.args = ['--stdout', '--best']


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' %\
                    tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_} > {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('gzip')[0]
