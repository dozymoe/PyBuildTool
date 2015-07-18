'''
Run ansible module

Options:

    * module        : str, None, ansible module name to run
    * args          : dict, None, arguments for the module
    * with_items    : str, None, dot separated dictionary keys for `context`
    * hosts         : list, None, host names from ANSIBLE_HOSTS file
    * hosts_pattern : str, '*', limit target hosts to a pattern
    * forks         : int, None, maximum number of processes to spawn
    * connect_timeout : int, None, ssh timeout
    * context_python: str, None, python scripts containing context for template
                      if it has __init__.py in the same directory it will be
                      added to sys.path
                      it must have variable type dict named: `export`
    * context_yaml  : str, None, yaml file containing context for template
    * context       : any, {}, context to be used in template

Requirements:

    * ansible
      to install, run `pip install ansible`

'''

import os
import six
import sys

from waflib import Logs
from yaml import safe_load as yaml_load

from base import Task as BaseTask, expand_resource, make_list

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    context = {}
    items = []

    def prepare(self):
        c = self.conf.get('module')
        if c is None:
            self.bld.fatal('"module" option in required')
        elif os.path.sep in c:
            c = expand_resource(self.bld, c)
            dirname, basename = os.path.split(c)
            modulename, extname = os.path.splitext(basename)
            assert extname == '.py'
            self.args.append(('module_path', dirname))
            self.args.append(('module_name', modulename))
        else:
            self.args.append(('module_name', c))

        c = self.conf.get('args')
        if c:
            assert isinstance(c, dict)
            self.args.append(('complex_args', c))

        c = self.conf.get('forks')
        if c:
            try:
                c = int(c)
            except ValueError:
                self.bld.fatal('"forks" option must be numeral')
            self.args.append(('forks', c))

        c = self.conf.get('connect_timeout')
        if c:
            try:
                c = int(c)
            except ValueError:
                self.bld.fatal('"timeout" option must be numeral')
            self.args.append(('timeout', c))

        c = self.conf.get('hosts_pattern', '*')
        self.args.append(('pattern', c))

        c = make_list(self.conf.get('hosts'))
        if c:
            self.args.append(('run_hosts', c))

        # do not run async
        self.args.append(('background', 0))

        ## context

        # Yaml context
        c = self.conf.get('context_yaml')
        if c:
            yaml_file = expand_resource(self.group, c)
            if yaml_file is None:
                self.bld.fatal('"context_yaml" for %s has invalid value' %\
                        tool_name.capitalize())
            with open(yaml_file, 'r') as f:
                self.context.update(yaml_load(f))

        # Python context
        c = self.conf.get('context_python')
        if c:
            python_file = expand_resource(self.group, c)
            if python_file is None:
                self.bld.fatal('"context_python" for %s has invalid value' %\
                        tool_name.capitalize())
            dirname, filename = os.path.split(python_file)
            filebase, fileext = os.path.splitext(filename)
            if os.path.exists(os.path.join(dirname, '__init__.py')):
                sys.path.append(dirname)
                mod = __import__(filebase)
            else:
                try:
                    from importlib.machinery import SourceFileLoader
                    mod = SourceFileLoader('context_python',
                            python_file).load_module()
                except ImportError:
                    import imp
                    mod = imp.load_source('context_python', python_file)
                python_export = mod.export
            self.context.update(python_export)

        self.context.update(self.conf.get('context', {}))
        self.args.append(('play_vars', self.context))

        # with_items
        c = self.conf.get('with_items')
        if isinstance(c, list):
            self.items = [{'item': item for item in c}]
        elif c:
            c = c.split('.')
            wi = self.context
            for wi_idx in c:
                wi = wi[wi_idx]
            assert isinstance(wi, list)
            for wi_item in wi:
                if isinstance(wi_item, dict):
                    self.items.append(wi_item)
                else:
                    self.items.append({'item': wi_item})


    def perform(self):
        import ansible.runner

        def log_error(data):
            Logs.error('Got "{msg}" from {host}'.format(
                tool=tool_name, **data))

        def extract_errors(result):
            print(result)
            success = True
            for host in result['contacted']:
                if result['contacted'][host].get('failed'):
                    log_error({
                        'host': host,
                        'msg': result['contacted'][host]['msg'],
                    })
                    success = False
            return success

        if len(self.items):
            success = True
            args = dict(self.args)
            kwargs = args['complex_args']
            for item in self.items:
                item_kwargs = {}
                for field in kwargs:
                    if isinstance(kwargs[field], six.string_types):
                        item_kwargs[field] = kwargs[field] % item
                    else:
                        item_kwargs[field] = kwargs[field]
                args['complex_args'] = item_kwargs
                result = ansible.runner.Runner(**args).run()
                success = success and extract_errors(result)
        else:
            result = ansible.runner.Runner(**dict(self.args)).run()
            success = extract_errors(result)

        if success:
            return 0
        else:
            return 1


def configure(conf):
    conf.start_msg("Checking for python module '%s'" % tool_name)
    try:
        import ansible # pylint: disable=unused-import
    except ImportError:
        conf.end_msg('not found', color='YELLOW')
