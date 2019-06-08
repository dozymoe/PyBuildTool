"""
Compile jinja2 templates.

This tool will accept multiple file_in, but only the first one will be
processed, the others are treated as dependency.

Options:

    * search_dir    : str, [], directories to search for templates
    * context_python: str, None, python scripts containing context for template
                      if it has __init__.py in the same directory it will be
                      added to sys.path
                      it must have variable type dict named: `export`
    * context_yaml  : str, None, yaml file containing context for template
    * context       : any, {}, context to be used in template

Requirements:

    * jinja2
      to install, run `pip install jinja2`

"""
import os
import sys
from yaml import safe_load as yaml_load
from pybuildtool import BaseTask, expand_resource, is_non_string_iterable
from pybuildtool.misc.python import load_module_from_filename

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_source_grouped_': True,
    }
    name = tool_name
    search_dir = ['.']
    context = {}

    def prepare(self):
        cfg = self.conf

        # Change current directory
        c = cfg.get('search_dir', [])
        if c:
            if not is_non_string_iterable(c):
                c = [c]
            c = [x for x in (expand_resource(self.group, f) for f\
                    in c) if x]
        if c:
            self.search_dir = c
        else:
            self.bld.fatal(('"search_dir" is required configuration '
                'for %s') % tool_name.capitalize())

        # Yaml context
        c = cfg.get('context_yaml')
        if c:
            yaml_file = expand_resource(self.group, c)
            if yaml_file is None:
                self.bld.fatal('"context_yaml" for %s has invalid value' %\
                        tool_name.capitalize())
            with open(yaml_file, 'r') as f:
                self.context.update(yaml_load(f))

        # Python context
        c = cfg.get('context_python')
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

        self.context.update(cfg.get('context', {}))


    def perform(self):
        from jinja2 import Environment, FileSystemLoader # pylint:disable=import-error

        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        template_name = self.file_in[0]
        for s in self.search_dir:
            if not template_name.startswith(s):
                continue
            template_name = template_name[len(s):].strip('/')
            break
        else:
            self.bld.fatal('input for %s must be within `search_dir' %\
                    tool_name.capitalize())

        loader = FileSystemLoader(self.search_dir)
        env = Environment(loader=loader)
        template = env.get_template(template_name)
        rendered = template.render(self.context)
        for out in self.file_out:
            with open(out, 'w') as f:
                f.write(rendered)
        return 0
