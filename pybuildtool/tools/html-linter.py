"""
HTML5 Linter based on Google Style Guide

Options:

    * disable : list:str, [], any combination of: doctype, entities,
                trailing_whitespace, tabs, charset, void_element,
                optional_tag, type_attribute, concerns_separation, protocol,
                names, capitalization, quotation, indentation, formatting,
                boolean_attribute, invalid_attribute, void_zero,
                invalid_handler, http_equiv, extra_whitespace

Requirements:

    * html-linter
      to install, run `pip install html-linter`

"""
from pybuildtool import BaseTask, make_list

tool_name = __name__

class Task(BaseTask):

    DISABLE_LIST = set(('doctype', 'entities', 'trailing_whitespace', 'tabs',
            'charset', 'void_element', 'optional_tag', 'type_attribute',
            'concerns_separation', 'protocol', 'names', 'capitalization',
            'quotation', 'indentation', 'formatting', 'boolean_attribute',
            'invalid_attribute', 'void_zero', 'invalid_handler', 'http_equiv',
            'extra_whitespace'))

    conf = {
        '_source_grouped_': True,
    }
    name = tool_name

    def prepare(self):
        cfg = self. conf
        args = self.args

        c = make_list(cfg.get('disable'))
        if c:
            invalid_disable_items = set(c) - self.DISABLE_LIST
            if invalid_disable_items:
                self.bld.fatal('invalid disable configuration items: ' +\
                        ', '.join(invalid_disable_items))
            args.append('--disable=' + ','.join(c))


    def perform(self):
        executable = self.env['%s_BIN' % tool_name.upper()]
        for file_in in self.file_in:
            return_code = self.exec_command(
                '{exe} {arg} {in_}'.format(
                exe=executable,
                arg=' '.join(self.args),
                in_=file_in,
            ))
            if return_code:
                print('Found syntax errors in %s\n' % file_in)
                return 1
        return 0


def configure(conf):
    bin_path = conf.find_program('html_lint.py')[0]
    conf.env['%s_BIN' % tool_name.upper()] = bin_path
