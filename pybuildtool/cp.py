""" Copy files. """

from base import Task as BaseTask
from shutil import copy

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one output' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' % tool_name.capitalize())

        if copy(self.file_in[0], self.file_out[0]):
            return 0
        return 1
