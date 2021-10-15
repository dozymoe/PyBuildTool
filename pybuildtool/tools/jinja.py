"""
Compile jinja2 templates.

This tool will accept multiple file_in, but only the first one will be
processed, the others are treated as dependency.

Options:

    * search_dir    : str, [], directories to search for templates
    * context_python: str, [], python scripts containing context for template
                      if it has __init__.py in the same directory it will be
                      added to sys.path
                      it must have variable type dict named: `export`
    * context_yaml  : str, [], yaml file containing context for template
    * context_json  : str, [], json file containing context for template
    * context       : any, {}, context to be used in template

Requirements:

    * jinja2
      to install, run `pip install jinja2`

"""
from typing import Mapping, Sequence
from json import load as json_load
import os
import sys
from yaml import safe_load as yaml_load
from pybuildtool import BaseTask, expand_resource, make_list
from pybuildtool.misc.python import load_module_from_filename

tool_name = __name__


def dict_merge(destination, source):
    for k, v in source.items():
        if k not in destination:
            destination[k] = v
        elif isinstance(v, Mapping)\
                and isinstance(destination[k], Mapping):
            dict_merge(destination[k], v)
        elif isinstance(v, Sequence)\
                and isinstance(destination[k], Sequence):
            destination[k].extend(v)


class Task(BaseTask):

    name = tool_name
    search_dir = None
    context = {}

    def prepare(self):
        cfg = self.conf

        # Change current directory
        c = make_list(cfg.get('search_dir'))
        if c:
            c = [x for x in (expand_resource(self.group, f) for f\
                    in c) if x]
        if c:
            self.search_dir = c
        else:
            self.bld.fatal(('"search_dir" is required configuration '
                'for %s') % tool_name.capitalize())

        # Json context
        files = make_list(cfg.get('context_json'))
        if files:
            files = [x for x in (expand_resource(self.group, f) for f\
                    in files) if x]
        for json_file in files:
            with open(json_file, 'r', encoding='utf-8') as f:
                dict_merge(self.context, json_load(f))

        # Yaml context
        files = make_list(cfg.get('context_yaml'))
        if files:
            files = [x for x in (expand_resource(self.group, f) for f\
                    in files) if x]
        for yaml_file in files:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                dict_merge(self.context, yaml_load(f))

        # Python context
        files = make_list(cfg.get('context_python'))
        if files:
            files = [x for x in (expand_resource(self.group, f) for f\
                    in files) if x]
        for python_file in files:
            dirname, filename = os.path.split(python_file)
            filebase, _ = os.path.splitext(filename)
            if os.path.exists(os.path.join(dirname, '__init__.py')):
                sys.path.append(dirname)
                mod = __import__(filebase)
            else:
                mod = load_module_from_filename(python_file, filebase)
            dict_merge(self.context, mod.export)

        dict_merge(self.context, cfg.get('context', {}))


    def perform(self):
        from jinja2 import Environment, FileSystemLoader # pylint:disable=import-error,import-outside-toplevel

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
            with open(out, 'w', encoding='utf-8') as f:
                f.write(rendered)
        return 0
