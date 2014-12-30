"""
Compile jinja2 templates.

The template file to compile with jinja2 is actually in the configuration .__.
with `template_name` configuration directive.
Later we would let jinja search in `search_dir`, luls.
`file_in` are only used for dependency to trigger automatic rebuild.

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

    args = []
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

        if 'template_name' not in cfg:
            self.bld.fatal(('"template_name" is required configuration '
                'for %s') % tool_name.capitalize())
        self.template_name = cfg['template_name']

        self.variables = cfg.get('variables', {})


    def perform(self):
        loader = FileSystemLoader(self.search_dir)
        env = Environment(loader=loader)
        template = env.get_template(self.template_name)
        rendered = template.render(self.variables)
        for out in self.file_out:
            with open(out, 'w') as f:
                f.write(rendered)
        return 0
