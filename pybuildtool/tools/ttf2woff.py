"""
convert existing TrueType/OpenType fonts to WOFF format (subject to
appropriate licensing)

Requirements:

    * sfnt2woff
      to install, download/compile from http://people.mozilla.org/~jkew/woff/

"""
import re
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_replace_patterns_': ((r'\.ttf$', '.woff'), (r'\.otf$', '.woff'))
    }
    name = tool_name

    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        ret = self.exec_command(
            '{exe} {arg} {in_}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
        ))

        if ret == 0:
            # success exit code
            move_executable = self.env['MV_BIN']
            converted_file = self.file_in[0]
            for (pat, rep) in self.conf['_replace_patterns_']:
                converted_file = re.sub(pat, rep, converted_file)
            ret = self.exec_command(
                '{exe} {in_} {out}'.format(
                exe=move_executable,
                in_=converted_file,
                out=self.file_out[0],
            ))

        return ret


def configure(conf):
    if not conf.env.MV_BIN:
        conf.env.MV_BIN = conf.find_program('mv')[0]

    bin_path = conf.find_program('sfnt2woff')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
