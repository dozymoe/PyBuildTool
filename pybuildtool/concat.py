""" Merge files from sources into copious targets. """

from base import Task as BaseTask
from shutil import copyfileobj

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_source_grouped_': True,
    }
    name = tool_name

    def perform(self):
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' % tool_name.capitalize())

        try:
            with open(self.file_out[0], 'wb') as dest:
                for src in self.file_in:
                    copyfileobj(open(src, 'rb'), dest)
            return 0
        except OSError:
            return 1
