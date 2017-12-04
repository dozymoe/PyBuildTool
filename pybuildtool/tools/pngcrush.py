"""
pngcrush is a png compressor

Options:

    * already       : int,   None
                      Already_crushed_size [e.g., 8192]
    * bail          : bool,  False
                      Bail out of trial when size exceeds best size found
    * bit_depth     : int,   None
                      Bit depth to use in output file
    * blacken       : bool,  False
                      Zero samples underlying fully-transparent pixels
    * brute         : int,   148
                      Use brute-force: try 138 different methods [11-148]
    * color_type    : int,   None
                      Color_type of output file [0, 2, 4, or 6]
    * double_gamma  : bool,  False
                      Used for fixing gamma in PhotoShop 5.0/5.02 files
    * filter        : int,   None
                      user_filter [0-5] for specified method
    * fix           : bool,  True
                      Fix otherwise fatal conditions such as bad CRCs
    * force         : bool,  False
                      Write a new output file even if larger than input
    * gamma         : float, None
                      Gamma (float or fixed*100000, e.g., 0.45455 or 45455)
    * huffman       : bool,  False
                      Use only zlib strategy 2, Huffman-only
    * iccp          : int,   None
                      Length "Profile Name" iccp_file
    * itxt          : str,   None
                      b[efore_IDAT]|a[fter_IDAT] "keyword"
    * keep          : bool,  False
                      chunk_name
    * level         : int,   None
                      zlib_compression_level [0-9] for specified method
    * loco          : bool,  False
                      "loco crush" truecolor PNGs
    * method        : int,   None
                      method [1 through 200]
    * max           : int,   None
                      maximum_IDAT_size [default 8192]
    * mng           : bool,  False
                      Write a new MNG, do not crush embedded PNGs
    * nobail        : bool,  False
                      Do not bail out early from trial -- see "-bail"
    * nofilecheck   : bool,  False
                      Do not check for infile.png == outfile.png
    * nolimits      : bool,  False
                      Turns off limits on width, height, cache, malloc
    * noreduce      : bool,  False
                      Turns off "-reduce" operations
    * oldtimestamp  : bool,  False
                      Do not reset file modification time
    * reduce        : bool,  False
                      Do lossless color-type or bit-depth reduction
    * rem           : bool,  False
                      chunkname (or "alla" or "allb")
    * replace_gamma : float, None
                      Gamma (float or fixed*100000) even if it is present
    * resolution    : int,   None
                      Resolution in dpi
    * rle           : bool,  False
                      Use only zlib strategy 3, RLE-only
    * save          : bool,  False
                      Keep all copy-unsafe PNG chunks
    * srgb          : int,   None
                      [0, 1, 2, or 3]
    * ster          : int,   None
                      [0 or 1]
    * text          : str,   None
                      b[efore_IDAT]|a[fter_IDAT] "keyword" "text"
    * trns_array    : str,   None
                      n trns[0] trns[1] .. trns[n-1]
    * trns          : str,   None
                      index red green blue gray
    * window_size   : int,   None
                      compression_window_size [32, 16, 8, 4, 2, 1, 512]
    * zlib          : int,   None
                      zlib_strategy [0, 1, 2, or 3] for specified method
    * zmem          : int,   None
                      zlib_compression_mem_level [1-9, default 9]
    * zitxt         : str,   None
                      b|a "keyword" "lcode" "tkey" "text"
    * ztxt          : str,   None
                      b[efore_IDAT]|a[fter_IDAT] "keywrod" "text"
    * quiet         : bool,  True
                      quiet

Requirements:

    * pngcrush
      to install, for example run `apt-get install pngcrush`

"""
from pybuildtool import BaseTask

tool_name = __name__

class Task(BaseTask):

    name = tool_name

    def prepare(self):
        cfg = self.conf
        args = self.args

        # already_crushed_size [e.g., 8192]
        if cfg.get('already', None):
            args.append('-already=%i' % cfg['already'])

        # bail out of trial when size exceeds best size found
        if cfg.get('bail', False):
            args.append('-bail')

        # bit depth to use in output file
        if cfg.get('bit_depth', None):
            args.append('-bit_depth=%i' % cfg['bit_depth'])

        # zero samples underlying fully-transparent pixels
        if cfg.get('blacken', False):
            args.append('-blacken')

        # use brute-force: try 138 different methods [11-148]
        args.append('-brute=%i' % cfg.get('brute', 148))

        # color_type of output file [0, 2, 4, or 6]
        if cfg.get('color_type', None):
            args.append('-c=%i' % cfg['color_type'])

        # used for fixing gamma in PhotoShop 5.0/5.02 files
        if cfg.get('double_gamma', False):
            args.append('-double_gamma')

        # user_filter [0-5] for specified method
        if cfg.get('filter', None):
            args.append('-f=%i' % cfg['filter'])

        # fix otherwise fatal conditions such as bad CRCs
        if cfg.get('fix', True):
            args.append('-fix')

        # write a new output file even if larger than input
        if cfg.get('force', None):
            args.append('-force')

        # gamma (float or fixed*100000, e.g., 0.45455 or 45455)
        if cfg.get('gamma', None):
            args.append('-g=%s' % cfg['gamma'])

        # use only zlib strategy 2, Huffman-only
        if cfg.get('huffman', False):
            args.append('-huffman')

        # length "Profile Name" iccp_file
        if cfg.get('iccp', None):
            args.append('-iccp=%i' % cfg['iccp'])

        # b[efore_IDAT]|a[fter_IDAT] "keyword"
        if cfg.get('itxt', None):
            args.append('-itxt="%s"' % cfg['itxt'])

        # chunk_name
        if cfg.get('keep', False):
            args.append('-keep')

        # zlib_compression_level [0-9] for specified method
        if cfg.get('level', None):
            args.append('-l=%i' % cfg['level'])

        # "loco crush" truecolor PNGs
        if cfg.get('loco', False):
            args.append('-loco')

        # method [1 through 200]
        if cfg.get('method', None):
            args.append('-m=%i' % cfg['method'])

        # maximum_IDAT_size [default 8192]
        if cfg.get('max', None):
            args.append('-max=%i' % cfg['max'])

        # write a new MNG, do not crush embedded PNGs
        if cfg.get('mng', False):
            args.append('-mng')

        # do not bail out early from trial -- see "-bail"
        if cfg.get('nobail', None):
            args.append('-nobail')

        # do not check for infile.png == outfile.png
        if cfg.get('nofilecheck', False):
            args.append('-nofilecheck')

        # turns off limits on width, height, cache, malloc
        if cfg.get('nolimits', False):
            args.append('-nolimits')

        # turns off "-reduce" operations
        if cfg.get('noreduce', False):
            args.append('-noreduce')

        # do not reset file modification time
        if cfg.get('oldtimestamp', False):
            args.append('-oldtimestamp')

        # do lossless color-type or bit-depth reduction
        if cfg.get('reduce', True):
            args.append('-reduce')

        # chunkname (or "alla" or "allb")
        if cfg.get('rem', None):
            args.append('-rem="%s"' % cfg['rem'])

        # gamma (float or fixed*100000) even if it is present
        if cfg.get('replace_gamma', None):
            args.append('-replace_gamma=%s' % cfg['replace_gamma'])

        # resolution in dpi
        if cfg.get('resolution', None):
            args.append('-res=%i' % cfg['resolution'])

        # use only zlib strategy 3, RLE-only
        if cfg.get('rle', False):
            args.append('-rle')

        # keep all copy-unsafe PNG chunks
        if cfg.get('save', False):
            args.append('-save')

        # srgb
        if cfg.get('srgb', None):
            args.append('-srgb=%i' % cfg['srgb'])

        # ster
        if cfg.get('ster', None):
            args.append('-ster=%i' % cfg['ster'])

        # b[efore_IDAT]|a[fter_IDAT] "keyword" "text"
        if cfg.get('text', None):
            args.append('-text="%s"' % cfg['text'])

        # trns_array: n trns[0] trns[1] .. trns[n-1]
        if cfg.get('trns_array', None):
            args.append('-trns_array="%s"' % cfg['trns_array'])

        # index red green blue gray
        if cfg.get('trns', None):
            args.append('-trns="%s"' % cfg['trns'])

        # compression_window_size [32, 16, 8, 4, 2, 1, 512]
        if cfg.get('window_size', None):
            args.append('-w=%i' % cfg['window_size'])

        # zlib_strategy [0, 1, 2, or 3] for specified method
        if cfg.get('zlib', None):
            args.append('-z=%i' % cfg['zlib'])

        # zlib_compression_mem_level [1-9, default 9]
        if cfg.get('zmem', None):
            args.append('-zmem=%i' % cfg['zmem'])

        # b|a "keyword" "lcode" "tkey" "text"
        if cfg.get('zitxt', None):
            args.append('-zitxt="%s"' % cfg['zitxt'])

        # b[efore_IDAT]|a[fter_IDAT] "keywrod" "text"
        if cfg.get('ztxt', None):
            args.append('-ztxt="%s"' % cfg['ztxt'])

        # quiet
        if cfg.get('quiet', True):
            args.append('-q')


    def perform(self):
        if len(self.file_in) != 1:
            self.bld.fatal('%s only need one input' % tool_name.capitalize())
        if len(self.file_out) != 1:
            self.bld.fatal('%s can only have one output' %\
                    tool_name.capitalize())

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            '{exe} {arg} {in_} {out}'.format(
            exe=executable,
            arg=' '.join(self.args),
            in_=self.file_in[0],
            out=self.file_out[0],
        ))


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('pngcrush')[0]
