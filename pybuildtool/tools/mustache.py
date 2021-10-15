""" Render a mustache template with the given context.

Requirements:

    * pystache
      to install, run `pip install pystache`

"""
import os
from pystache import render
#-
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal("%s only need one input" % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal("%s can only have one output" %\
                    tool_name.capitalize())

        context = self.conf.get('context', {})
        os.makedirs(os.path.dirname(self.file_out[0]), exist_ok=True)
        with open(self.file_out[0], 'w', encoding='utf-8') as fout:
            with open(self.file_in[0], 'r', encoding='utf-8') as fin:
                fout.write(render(fin.read(), dict(context)))

        return 0
