"""
Compile jinja2 templates.

This tool will accept multiple file_in, but only the first one will be
processed, the others are treated as dependency.

Options:

    * search_dir    : str, [], directories to search for templates
    * template_name : str, None, main template file to search in search_dir
                      and rendered by jinja2, required
    * variables     : any, {}, variables to be used in template
"""
from base import Task as BaseTask, expand_resource, is_non_string_iterable
from jinja2 import Environment, FileSystemLoader

tool_name = __name__

class Task(BaseTask):

    conf = {
        '_source_grouped_': True,
    }
    name = tool_name
    search_dir = ['.']
    template_name = None
    variables = None

    def prepare(self):
        cfg = self.conf

        # Change current directory
        c = cfg.get('search_dir')
        if c:
            if not is_non_string_iterable(c):
                c = [c]
            self.search_dir = [expand_resource(self.group, f) for f in c]
        else:
            self.bld.fatal(('"search_dir" is required configuration '
                'for %s') % tool_name.capitalize())

        self.variables = cfg.get('variables', {})


    def perform(self):
        template_name = self.file_in[0]
        for s in self.search_dir:
            if not template_name.startswith(s):
                continue
            template_name = template_name[len(s):].strip('/')
            break

        loader = FileSystemLoader(self.search_dir)
        env = Environment(loader=loader)
        template = env.get_template(template_name)
        rendered = template.render(self.variables)
        for out in self.file_out:
            with open(out, 'w') as f:
                f.write(rendered)
        return 0
