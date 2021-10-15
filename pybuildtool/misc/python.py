from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

def load_module_from_filename(filename, name):
    spec = spec_from_loader(name, SourceFileLoader(name, filename))
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
