"""
create and edit fonts in many formats: OpenType, TrueType, AAT, PostScript,
Multiple Master, CID-Keyed, SVG and various bitmap formats

Requirements:

    * fontforge
      to install, run `apt-get install fontforge` (for example)

"""
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_replace_patterns_': ((r'\.woff$', '.ttf'), (r'\.woff2$', '.ttf'))
    }
    name = tool_name

    def prepare(self):
        args = self.args
        args.append('-lang ff')
        args.append("-c 'Open($1); Generate($2)'")


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_} {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ))


def configure(conf):
    bin_path = conf.find_program('fontforge')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
