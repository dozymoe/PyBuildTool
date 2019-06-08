"""
Generate diagram.

Options:

    * work_dir : str, None
               : Change current directory before running

    * graph_attr : dict, None
                 : Set graph attribute 'name' to 'val'

    * node_attr  : dict, None
                 : Set node attribute 'name' to 'val'

    * edge_attr  : dict, None
                 : Set edge attribute 'name' to 'val'

    * output_format : str, None
                    : Set output format
                    : Possible values:
                    :   - bmp
                    :   - canon
                    :   - cmap
                    :   - cmapx
                    :   - cmapx_np
                    :   - dot
                    :   - eps
                    :   - fig
                    :   - gd
                    :   - gd2
                    :   - gif
                    :   - gtk
                    :   - gv
                    :   - ico
                    :   - imap
                    :   - imap_np
                    :   - ismap
                    :   - jpe
                    :   - jpeg
                    :   - jpg
                    :   - pdf
                    :   - pic
                    :   - plain
                    :   - plain-ext
                    :   - png
                    :   - pov
                    :   - ps
                    :   - ps2
                    :   - svg
                    :   - svgz
                    :   - tif
                    :   - tiff
                    :   - tk
                    :   - vml
                    :   - vmlz
                    :   - vrml
                    :   - wbmp
                    :   - x11
                    :   - xdot
                    :   - xdot1.2
                    :   - xdot1.4
                    :   - xlib

    * layout_engine : str, None
                    : Set layout engine
                    : Possible values:
                    :   - circo
                    :   - dot
                    :   - fdp
                    :   - neato
                    :   - nop
                    :   - nop1
                    :   - nop2
                    :   - osage
                    :   - patchwork
                    :   - sfdp
                    :   - twopi

    * library : list, None
              : Use external library

    * verbosity : int, None
                : Set level of message suppression (default=1)

    * scale : int, None
            : Scale input by n (default=72)

    * v_flip : bool, None
             : Invert y coordinate in output

    * no_layout : int, None
                : No layout mode n (default=1)

    * reduce_graph : bool, None
                   : Reduce graph

    * no_grid : bool, None
              : Don't use grid

    * old_attract : bool, None
                  : Use old attractive force

    * iteration : int, None
                : Set number of iterations to n

    * unscaled_factor : int, None
                      : Set unscaled factor to n

    * overlap_expansion_factor : int, None
                               : Set overlap expansion factor to n

    * temperature_factor : int, None
                         : Set temperature (temperature factor) to n

Requirements:

    * graphviz
      to install, for example run `apt-get install graphviz`

"""
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    workdir = None

    def prepare(self):
        cfg = self.conf
        arg = self.args

        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)

        c = cfg.get('graph_attr')
        if isinstance(c, dict):
            for key in c:
                arg.append('-G%s=%s' % (key, c[key]))
        elif c is not None:
            self.bld.fatal('graph_attr must be a dictionary.')

        c = cfg.get('node_attr')
        if isinstance(c, dict):
            for key in c:
                arg.append('-N%s=%s' % (key, c[key]))
        elif c is not None:
            self.bld.fatal('node_attr must be a dictionary.')

        c = cfg.get('edge_attr')
        if isinstance(c, dict):
            for key in c:
                arg.append('-E%s=%s' % (key, c[key]))
        elif c is not None:
            self.bld.fatal('edge_attr must be a dictionary.')

        c = cfg.get('output_format')
        if c:
            arg.append('-T' + c)

        c = cfg.get('layout_engine')
        if c:
            arg.append('-K' + c)

        c = cfg.get('library', [])
        for lib in c:
            arg.append('-l' + lib)

        c = cfg.get('verbosity')
        if c is not None:
            arg.append('-q' + c)

        c = cfg.get('scale')
        if c:
            arg.append('-s' + c)

        c = cfg.get('v_flip')
        if c:
            arg.append('-y')

        c = cfg.get('no_layout')
        if c:
            arg.append('-n' + c)

        c = cfg.get('reduce_graph')
        if c:
            arg.append('-x')

        c = cfg.get('no_grid')
        if c:
            arg.append('-Lg')

        c = cfg.get('old_attract')
        if c:
            arg.append('-LO')

        c = cfg.get('iteration')
        if c:
            arg.append('-Ln' + c)

        c = cfg.get('unscaled_factor')
        if c:
            arg.append('-LU' + c)

        c = cfg.get('overlap_expansion_factor')
        if c:
            arg.append('-LC' + c)

        c = cfg.get('temperature_factor')
        if c:
            arg.append('-LT' + c)


    def perform(self):
        if not self.file_in:
            self.bld.fatal('%s needs input' % tool_name)
        if len(self.file_out) != 1:
            self.bld.fatal('%s produces one output' % tool_name)

        kwargs = {}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command([executable, '-o' + self.file_out[0]] +\
                self.args + self.file_in, **kwargs)


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program(tool_name)[0]
