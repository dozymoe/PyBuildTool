"""
scp is secure copy (remote file copy program)

Options:

    * username     : str, None, use the user for authentication
    * identify_file: str, None, use the ssh private key file for authentication
    * host         : str, None, host name, URL or bookmark name
    * port         : int, None, use the port for connection

Requirements:

    * scp
      to install, for example run `apt-get install openssh`

"""
from pybuildtool import BaseTask, expand_resource

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_source_grouped_': True,
    }
    hoststr = None
    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        # identity file
        c = cfg.get('identity_file', None)
        if c:
            args.append('-i %s' % expand_resource(self.group, c))

        # port
        c = cfg.get('port', None)
        if c:
            args.append('-P %s' % c)

        # host
        h = cfg.get('host', None)
        if h:
            u = cfg.get('username', None)
            if u:
                self.hoststr = '%s@%s' % (u, h)
            else:
                self.hoststr = h
        else:
            self.bld.fatal('configuration "%s" is required for %s' % (
                    'host', tool_name))


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s only have one output' % tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            "{exe} {arg} {in_} {hst}:{out}".format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
            hst=self.hoststr,
        ))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('scp')[0]
