""" Merge files from sources into copious targets.
"""
import os
from shutil import copyfileobj
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_source_grouped_': True,
    }
    name = tool_name

    def perform(self):
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' %\
                    tool_name.capitalize())

        if os.path.isdir(self.file_out[0]):
            self.bld.fatal('cannot concat to a directory')

        try:
            with open(self.file_out[0], 'wb') as dest:
                for src in self.file_in:
                    copyfileobj(open(src, 'rb'), dest)
            return 0
        except OSError:
            return 1
