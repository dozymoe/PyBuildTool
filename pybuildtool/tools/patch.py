"""
Patch apply changes to a file

Options:

    * patch_file : str, None, location of patch file (can be made using this
                   command `diff -Naur original_file current_file` > patch_file

Requirements:

    * patch

"""
import os
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        if cfg.get('patch_file') is None:
            self.bld.fatal('InvalidOptions: "patch_file" is missing')
        args.append('-i ' + os.path.realpath(cfg['patch_file']))


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' %\
                    tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} -o {out} {in_}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('patch')[0]
