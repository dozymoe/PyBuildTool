"""
lftp is sophisticated file transfer progam

Options:

    * username: str, None, use the user for authentication
    * password: str, None, use the password for authentication
    * host    : str, None, host name, URL or bookmark name
    * port    : int, None, use the port for connection

Requirements:

    * lftp
      to install, for example run `apt-get install lftp`

"""

from pybuildtool import BaseTask

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

        # user and password
        u = cfg.get('username', None)
        if u:
            p = cfg.get('password', None)
            if p:
                authstr = '%s,%s' % (u, p)
            else:
                authstr = u
            args.append('-u %s' % authstr)

        # port
        c = cfg.get('port', None)
        if c:
            args.append('-p %s' % c)

        # host
        c = cfg.get('host', None)
        if c:
            self.hoststr = c
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
            "{exe} {arg} -e 'put {in_} -o {out}' {hst}".format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
            hst=self.hoststr,
        ))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('lftp')[0]
