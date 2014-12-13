""" Merge files from sources into copious targets. """

from base import Task as BaseTask

tool_name = __name__

class Task(BaseTask):
    conf = {
        '_source_grouped_': True,
    }

    def perform(self):
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_} > {out}'.format(
            exe=executable,
            arg=' '.join(self.prepare_args()),
            in_=' '.join(self.file_in),
            out=self.file_out[0],
        ))


def configure(conf):
    bin_path = conf.find_program('cat')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path