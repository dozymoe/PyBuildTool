""" Merge files from sources into copious targets.
"""
import os
from shutil import copyfileobj
from pybuildtool import BaseTask
from pybuildtool.misc.resource import get_filehash

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_source_grouped_': True,
        '_noop_retcodes_': 666,
    }
    name = tool_name

    def perform(self):
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' %\
                    tool_name.capitalize())

        if os.path.isdir(self.file_out[0]):
            self.bld.fatal('cannot concat to a directory')

        try:
            before_hash = get_filehash(self.file_out[0])
            with open(self.file_out[0], 'wb') as dest:
                for src_name in self.file_in:
                    with open(src_name, 'rb') as src:
                        copyfileobj(src, dest)

            if before_hash == get_filehash(self.file_out[0]):
                return 666
            return 0
        except OSError:
            return 1
