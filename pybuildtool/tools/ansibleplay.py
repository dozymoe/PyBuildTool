'''
Run ansible module

Options:

    * module        : str, None, ansible module name to run
    * args          : dict, None, arguments for the module
    * free_form     : str, None, modules like `shell` and `command`, besides
                      args, also take in free_form arg
                      we facilitate this to provide direct access to
                      `modules_args`, our args option will actually be send as
                      `complex_args`
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
import sys
import six
from waflib import Logs # pylint:disable=import-error
from yaml import safe_load as yaml_load
#-
from pybuildtool import BaseTask, expand_resource, make_list
from pybuildtool.misc.python import load_module_from_filename

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    context = None
    items = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = {}
        self.items = []


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

        c = self.conf.get('free_form')
        if c:
            self.args.append(('module_args', c))

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
            with open(yaml_file, 'r', encoding='utf-8') as f:
                self.context.update(yaml_load(f))

        # Python context
        c = self.conf.get('context_python')
        if c:
            python_file = expand_resource(self.group, c)
            if python_file is None:
                self.bld.fatal('"context_python" for %s has invalid value' %\
                        tool_name.capitalize())
            dirname, filename = os.path.split(python_file)
            filebase, _ = os.path.splitext(filename)
            if os.path.exists(os.path.join(dirname, '__init__.py')):
                sys.path.append(dirname)
                mod = __import__(filebase)
            else:
                mod = load_module_from_filename(python_file, filebase)
            python_export = mod.export
            self.context.update(python_export)

        self.context.update(self.conf.get('context', {}))
        self.args.append(('play_vars', self.context))

        # with_items
        c = self.conf.get('with_items')
        if isinstance(c, list):
            wi = list(c)
        elif c:
            c = c.split('.')
            wi_ctx = self.context
            for wi_idx in c:
                wi = wi_ctx[wi_idx]
            wi = make_list(wi, nodict=True)
        else:
            wi = []

        for wi_item in wi:
            if isinstance(wi_item, dict):
                self.items.append(wi_item)
            else:
                self.items.append({'item': wi_item})


    def perform(self):
        import ansible.runner # pylint:disable=import-error,import-outside-toplevel

        def log_error(data):
            Logs.error('Got "{msg}" from {host}'.format(
                tool=tool_name, **data))

        def extract_errors(result):
            print(result)
            changed = False
            success = True
            for host in result['contacted']:
                if result['contacted'][host].get('failed'):
                    log_error({
                        'host': host,
                        'msg': result['contacted'][host]['msg'],
                    })
                    success = False
                if result['contacted'][host].get('changed'):
                    changed = True
            return success, changed

        success = True
        changed = False
        if self.items:
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
                was_success, was_changed = extract_errors(result)
                success = success and was_success
                changed = changed or was_changed
        else:
            result = ansible.runner.Runner(**dict(self.args)).run()
            was_success, was_changed = extract_errors(result)
            success = success and was_success
            changed = changed or was_changed

        #if changed:
        #    self.finalize_shadow_jutsu(use_file_out=True)
        #elif success:
        #    for fo in self.file_out:
        #        if not os.path.exists(fo):
        #            self.finalize_shadow_jutsu(use_file_out=True)
        #            break

        if success:
            return 0
        return 1


def configure(conf):
    conf.start_msg("Checking for python module '%s'" % tool_name)
    try:
        import ansible # pylint: disable=unused-import,import-outside-toplevel
    except ImportError:
        conf.end_msg('not found', color='YELLOW')
