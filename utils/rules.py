from utils.common import Rule


class CleanCss(Rule):
    replace_patterns = ((r'\.css$', '.min.css'),)
    tool_name = 'clean_css'

class Concat(Rule):
    group_file_in = True

class Copy(Rule):
    pass

class GZip(Rule):
    group_file_in = True

class Jshint(Rule):
    pass

class Patch(Rule):
    pass

class PngCrush(Rule):
    pass

class Pylint(Rule):
    pass

class Stylus(Rule): 
    replace_patterns = ((r'\.styl$', '.css'),)

class UglifyJS(Rule):
    replace_patterns = ((r'\.js$', '.min.js'),)
