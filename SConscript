from os import environ, getcwd, path, sep
from PyBuildTool.utils.common import (get_config_filename,
                                      read_config,
                                      get_shadow_name_jutsu)
from SCons import Node


Import('env ROOT_DIR BUILD_DIR')


#env.Decider('MD5-timestamp')
#env.Decider('timestamp-match')

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

        target_sandboxed = group_options.get('_target_sandboxed_', True)

        for item in group['items']:
            shadow = {}
            source = []
            target = []
            
            source_in = item.get('in', [])
            if isinstance(source_in, list):
                source += source_in
            else:
                source.append(source_in)

            target_out = item.get('out', [])
            if isinstance(target_out, list):
                target += target_out
            else:
                target.append(target_out)

            # assume target ended with `os.sep` as directory
            # and containing `*` as wildcard
            source_file_in = item.get('file-in', [])
            if not isinstance(source_file_in, list):
                source_file_in = [source_file_in]

            for src in source_file_in:
                if src.endswith(sep):
                    src_shadow = get_shadow_name_jutsu(
                        src,
                        Node.FS.Dir,
                        prefix,
                    )
                    src_resolved = path.join(prefix, src)
                    shadow[src_shadow] = src_resolved
                    src_final = src_shadow
                else:
                    src_resolved = path.join(prefix, src)
                    if '*' in src_resolved:
                        src_final = Glob(src_resolved)
                    else:
                        src_final = src_resolved
                source.append(src_final)

            # parse Alias sources.
            source_alias_in = item.get('alias-in', [])
            if not isinstance(source_alias_in, list):
                source_alias_in = [source_alias_in]
                
            for alias in source_alias_in:
                alias_shadow = get_shadow_name_jutsu(
                    alias,
                    Node.Alias.Alias,
                    prefix,
                )
                shadow[alias_shadow] = alias
                source.append(alias_shadow)

            # parse Value sources.
            source_value_in = item.get('value-in', [])
            if not isinstance(source_value_in, list):
                source_value_in = [source_value_in]

            for value in source_value_in:
                value_shadow = get_shadow_name_jutsu(
                    value,
                    Node.Python.Value,
                    prefix,
                )
                shadow[value_shadow] = value
                source.append(value_shadow)


            # files are either relative to build dir, or relative
            # to ROOT_DIR.
            # ROOT_DIR is where SConsfile.yml lies.
            #
            # assume target ended with `os.sep` as directory
            target_file_out = item.get('file-out', [])
            if not isinstance(target_file_out, list):
                target_file_out = [target_file_out]

            for dest in target_file_out:
                if dest.endswith(sep):
                    dest_shadow = get_shadow_name_jutsu(
                        dest,
                        Node.FS.Dir,
                        prefix,
                    )
                    if target_sandboxed:
                        dest_resolved = path.join(prefix, dest)
                    else:
                        dest_resolved = path.join(ROOT_DIR, dest)

                    shadow[dest_shadow] = dest_resolved
                    dest_final = dest_shadow
                else:
                    if target_sandboxed:
                        dest_resolved = path.join(prefix, dest)
                    else:
                        dest_resolved = path.join(ROOT_DIR, dest)
                    dest_final = dest_resolved
                target.append(dest_final)

            # parse Alias targets.
            target_alias_out = item.get('alias-out', [])
            if not isinstance(target_alias_out, list):
                target_alias_out = [target_alias_out]
                
            for alias in target_alias_out:
                alias_shadow = get_shadow_name_jutsu(
                    alias,
                    Node.Alias.Alias,
                    prefix,
                )
                shadow[alias_shadow] = alias
                target.append(alias_shadow)

            # parse Value sources.
            target_value_out = item.get('value-out', [])
            if not isinstance(target_value_out, list):
                target_value_out = [target_value_out]

            for value in target_value_out:
                value_shadow = get_shadow_name_jutsu(
                    value,
                    Node.Python.Value,
                    prefix,
                )
                shadow[value_shadow] = value
                target.append(value_shadow)


            nodes = tool(
                target,
                source,
                ROOT_DIR=ROOT_DIR,
                TOOLCFG=Value(group_options),
                SHADOWLIST=Value(shadow),
            )

            group_nodes.extend(nodes)
        
        Depends(group_alias, Alias(group.get('depends', [])))

        tool_nodes.extend(env.Alias(group_alias, group_nodes))
    env.Alias(tool_name, tool_nodes)
