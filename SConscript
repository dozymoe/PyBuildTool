from os import environ, getcwd, path
from PyBuildTool.utils.common import get_config_filename, read_config
from SCons.Node.FS import FS


Import('env ROOT_DIR BUILD_DIR')


# support different build stages (development, production, etc.).
AddOption('--stage', dest='stage', type='string',
          action='store', default='default',
          help='Build workflow stages, for example development' \
               ' or production')
env['ENV']['STAGE'] = GetOption('stage')


# support different type of configuration files (py and yml).
AddOption('--filetype', dest='filetype', 
          action='store', default='auto', choices=['auto', 'py', 'yml'],
          help='File type or file extension of main configuration file,'\
               ' for example SConsfile.yml with yml as the value.')

# support watch command.
AddOption('--watch', dest='watch', action='store_true', default=False,
          help='Watch file changes and automatically invoke scons build' \
               ' per group.')

# populate scons' shell-environment-variable $PATH with system's $PATH.
for p in environ['PATH'].split(':'):
    env.AppendENVPath('PATH', p)


# tell SCons where to find our tools.
toolpath = env.get('toolpath', [])
toolpath.append(path.join(getcwd(), 'tools'))
env['toolpath'] = toolpath


# setup sandbox for temporary build files.
prefix = path.join(BUILD_DIR, env['ENV']['STAGE'])
env.VariantDir(prefix, ROOT_DIR)


# if `watch` argument specified, exit stage left.
if GetOption('watch'):
    from PyBuildTool.utils.watch import Watch

    watch = Watch(env=env, root_dir=ROOT_DIR,
                  stage=env['ENV']['STAGE'],
                  filetype=GetOption('filetype'))
    watch.run()
    exit(0)


# read build-configuration (files to process).
config_file = get_config_filename(root=ROOT_DIR,
                                  stage=env['ENV']['STAGE'],
                                  filetype=GetOption('filetype'))
config = read_config(basefilename=config_file[0],
                     filetype=config_file[1],
                     env=env, root_dir=ROOT_DIR)
                                  
# main function, process build config into tasks.
for tool_name in config:
    env.Tool(tool_name)

    tool = getattr(env, tool_name)
    tool_nodes = []

    for group_name in config[tool_name]:
        group = config[tool_name][group_name]

        group_nodes = []
        group_alias = '%s:%s' % (tool_name, group_name)
        group_dependencies = group.get('depends', [])
        group_options = group.get('options', {})

        for item in group['files']:
            # reconstruct files into list
            target_raw = item.get('dest', [])
            if not isinstance(target_raw, list):
                target_raw = [target_raw]

            source_raw = item.get('src', [])
            if not isinstance(source_raw, list):
                source_raw = [source_raw]

            if tool.builder.target_factory is None or \
               tool.builder.target_factory.im_self.__class__ is FS:
                # files are either relative to build dir, or relative
                # to ROOT_DIR.
                # ROOT_DIR is where SConsfile.yml lies.
                if group_options.get('_target_sandboxed_', True):
                    target = [path.join(prefix, dest)
                              for dest in target_raw if dest]
                else:
                    target = [path.join(ROOT_DIR, dest)
                              for dest in target_raw if dest]
            else:
                target = target_raw

            if tool.builder.source_factory is None or \
               tool.builder.source_factory.im_self.__class__ is FS:
                source = [path.join(prefix, src)
                          for src in source_raw if src]
            else:
                source = source_raw

            nodes = tool(target, source, TOOLCFG=Value(group_options))

            group_nodes.extend(nodes)
        tool_nodes.extend(env.Alias(group_alias, group_nodes))
    env.Alias(tool_name, tool_nodes)
