"""
very quick commandline wrapper around OpenTypeUtilities.cpp from Chromium,
used to make EOT (Embeddable Open Type) files from TTF (TrueType/OpenType
Font) files

Requirements:

    * ttf2eot
      to install, download/compile from https://github.com/metaflop/ttf2eot

"""
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_replace_patterns_': ((r'\.ttf$', '.eot'), (r'\.otf$', '.eot'))
    }
    name = tool_name

    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        ret = self.exec_command(
            '{exe} {arg} < {in_} > {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ), stdout=None)

        return ret


def configure(conf):
    bin_path = conf.find_program('ttf2eot')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
