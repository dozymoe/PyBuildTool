""" Copy files.
"""
from shutil import copyfile, Error
from pybuildtool import BaseTask
from pybuildtool.misc.resource import get_filehash

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_noop_retcodes_': 666,
    }
    name = tool_name

    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input, got %s' % (
                    tool_name.capitalize(), repr(self.file_in)))

        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output, got %s' % (
                    tool_name.capitalize(), repr(self.file_out)))

        try:
            source_hash = get_filehash(self.file_in[0])
            if source_hash and source_hash == get_filehash(self.file_out[0]):
                return 666
            copyfile(self.file_in[0], self.file_out[0])
            return 0
        except Error:
            self.bld.fatal('tried to copy file to itself')
        except IOError:
            self.bld.fatal('destination location cannot be written')
        return 1
