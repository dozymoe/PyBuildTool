import os
from waflib import Context, Errors # pylint:disable=import-error

class WatchContext(Context.Context):
    cmd = 'watch'
    fun = 'watch'
    variant = ''

    def __init__(self, **kw):
        super().__init__(**kw)

        self.top_dir = kw.get('top_dir', Context.top_dir)
        self.out_dir = kw.get('out_dir', Context.out_dir)

        if not(os.path.isabs(self.top_dir) and os.path.isabs(self.out_dir)):
            raise Errors.WafError('The project was not configured: ' +\
                    'run "waf configure" first!')
        self.path = self.srcnode = self.root.find_dir(self.top_dir)
        self.bldnode = self.root.make_node(self.variant_dir)


    def get_variant_dir(self):
        if not self.variant:
            return self.out_dir
        return os.path.join(self.out_dir, self.variant)

    variant_dir = property(get_variant_dir, None)
