"""
Convert google font's METADATA.json into css @font-face.

Options:

    * font_dir_url : str, ''
                     The directory url on where the file was going to be hosted.
                     The value should ends with '/'.
    * font_types   : list, ['ttf']
                     Print the stated font types.
    * font_svg_id  : str, None
                     Default is the font's PostScript name.

Requirements:

    * protobuf
      to install, run `pip install protobuf`

"""
import json
from pybuildtool import BaseTask, make_list

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    dir_url = None
    print_ttf = None
    print_eot = None
    print_woff = None
    print_svg = None
    svg_id = None

    def prepare(self):
        cfg = self.conf

        types = make_list(cfg.get('font_types', ['ttf']))
        self.print_ttf = 'ttf' in types
        self.print_eot = 'eot' in types
        self.print_woff = 'woff' in types
        self.print_svg = 'svg' in types

        self.dir_url = cfg.get('font_dir_url', '').format(**self.group.\
                get_patterns())

        self.svg_id = cfg.get('font_svg_id')


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only needs one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s only needs one output' % tool_name.capitalize())

        filename = self.file_in[0]
        if filename.endswith('.json'):
            with open(self.file_in[0], 'r', encoding='utf-8') as f:
                fonts = json.load(f)['fonts']
        elif filename.endswith('.pb'):
            fonts = self._get_fonts_from_protobuf(filename)
        else:
            self.bld.fatal('Unknown file format: ' + filename)

        with open(self.file_out[0], 'w', encoding='utf-8') as f:
            for font in fonts:
                f.write('@font-face {\n')
                f.write('    font-family: "%s";\n' % font['name'])
                f.write('    font-style: %s;\n' % font['style'])
                f.write('    font-weight: %i;\n' % font['weight'])
                f.write('    src:\n')
                f.write('        local("%s")' % font['fullName'])

                arg = {'dir': self.dir_url, 'name': font['postScriptName']}

                if self.print_eot:
                    f.write((',\n        url({dir}{name}.eot?#iefix) ' +\
                            'format("embedded-opentype")').format(**arg))

                if self.print_woff:
                    f.write((',\n        url({dir}{name}.woff) ' +\
                            'format("woff")').format(**arg))

                if self.print_ttf:
                    f.write((',\n        url({dir}{name}.ttf) ' +\
                            'format("truetype")').format(**arg))

                if self.print_svg:
                    arg['id'] = self.svg_id or font['postScriptName']
                    f.write((',\n        url({dir}{name}.svg#{id}) ' +\
                            'format("svg")').format(**arg))

                f.write(';\n}\n')


    @staticmethod
    def _get_fonts_from_protobuf(filename):
        from google.protobuf import text_format # pylint:disable=import-error,no-name-in-module,import-outside-toplevel
        from pybuildtool.vendor.fonts_public_pb2 import FamilyProto # pylint:disable=import-outside-toplevel

        message = FamilyProto()
        with open(filename, encoding='utf-8') as f:
            text_format.Merge(f.read(), message)

        for font in message.fonts:
            yield {t[0].json_name: t[1] for t in font.ListFields()}
