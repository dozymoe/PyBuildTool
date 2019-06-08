"""
rsync is a file transfer program capable of efficient remote update
via a fast differencing algorithm.

Options:

    * target : str, None
             : rsync destination

    * work_dir : str, None
               : change current directory before rsync

    * verbose : bool, None
              : increase verbosity

    * info : str, None
           : fine-grained informational verbosity

    * debug : str, None
            : fine-grained debug verbosity

    * msgs2stderr : bool, None
                  : special output handling for debugging

    * quiet : bool, None
            : suppress non-error messages

    * no_MOTD : bool, None
              : suppress daemon-mode MOTD (see manpage caveat)

    * checksum : bool, None
               : skip based on checksum, not mod-time & size

    * archive : bool, None
              : archive mode; equals -rlptgoD (no -H,-A,-X)

    * no_OPTION : list, None
                : turn off an implied OPTION (e.g. --no-D)

    * recursive : bool, None
                : recurse into directories

    * relative : bool, None
               : use relative path names

    * no_implied_dirs : bool, None
                      : don't send implied dirs with --relative

    * backup : bool, None
             : make backups (see --suffix & --backup-dir)

    * backup_dir : str, None
                 : make backups into hierarchy based in DIR

    * suffix : str, None
             : set backup suffix (default ~ w/o --backup-dir)

    * update : bool, None
             : skip files that are newer on the receiver

    * inplace : bool, None
              : update destination files in-place (SEE MAN PAGE)

    * append : bool, None
             : append data onto shorter files

    * append_verify : bool, None
                    : like --append, but with old data in file checksum

    * dirs : bool, None
           : transfer directories without recursing

    * links : bool, None
            : copy symlinks as symlinks

    * copy_links : bool, None
                 : transform symlink into referent file/dir

    * copy_unsafe_links : bool, None
                        : only "unsafe" symlinks are transformed

    * safe_links : bool, None
                 : ignore symlinks that point outside the source tree

    * munge_links : bool, None
                  : munge symlinks to make them safer (but unusable)

    * copy_dirlinks : bool, None
                    : transform symlink to a dir into referent dir

    * keep_dirlinks : bool, None
                    : treat symlinked dir on receiver as dir

    * hard_links : bool, None
                 : preserve hard links

    * perms : bool, None
            : preserve permissions

    * executability : bool, None
                    : preserve the file's executability

    * chmod : str, None
            : affect file and/or directory permissions

    * acls : bool, None
           : preserve ACLs (implies --perms)

    * xattrs : bool, None
             : preserve extended attributes

    * owner : bool, None
            : preserve owner (super-user only)

    * group : bool, None
            : preserve group

    * devices : bool, None
              : preserve device files (super-user only)

    * specials : bool, None
               : preserve special files

    * times : bool, None
            : preserve modification times

    * omit_dir_times : bool, None
                     : omit directories from --times

    * omit_link_times : bool, None
                      : omit symlinks from --times

    * super : bool, None
            : receiver attempts super-user activities

    * fake_super : bool, None
                 : store/recover privileged attrs using xattrs

    * sparse : bool, None
             : handle sparse files efficiently

    * preallocate : bool, None
                  : allocate dest files before writing them

    * dry_run : bool, None
              : perform a trial run with no changes made

    * whole_file : bool, None
                 : copy files whole (without delta-xfer algorithm)

    * one_file_system : bool, None
                      : don't cross filesystem boundaries

    * block_size : int, None
                 : force a fixed checksum block-size

    * rsh : str, None
          : specify the remote shell to use

    * rsync_path : str, None
                 : specify the rsync to run on the remote machine

    * existing : bool, None
               : skip creating new files on receiver

    * ignore_existing : bool, None
                      : skip updating files that already exist on receiver

    * remove_source_files : bool, None
                          : sender removes synchronized files (non-dirs)

    * delete : bool, None
             : delete extraneous files from destination dirs

    * delete_before : bool, None
                    : receiver deletes before transfer, not during

    * delete_during : bool, None
                    : receiver deletes during the transfer

    * delete_delay : bool, None
                   : find deletions during, delete after

    * delete_after : bool, None
                   : receiver deletes after transfer, not during

    * delete_excluded : bool, None
                      : also delete excluded files from destination dirs

    * ignore_missing_args : bool, None
                          : ignore missing source args without error

    * delete_missing_args : bool, None
                          : delete missing source args from destination

    * ignore_errors : bool, None
                    : delete even if there are I/O errors

    * force : bool, None
            : force deletion of directories even if not empty

    * max_delete : int, None
                 : don't delete more than NUM files

    * max_size : int, None
               : don't transfer any file larger than SIZE

    * min_size : int, None
               : don't transfer any file smaller than SIZE

    * partial : bool, None
              : keep partially transferred files

    * partial_dir : str, None
                  : put a partially transferred file into DIR

    * delay_updates : bool, None
                    : put all updated files into place at transfer's end

    * prune_empty_dirs : bool, None
                       : prune empty directory chains from the file-list

    * numeric_ids : bool, None
                  : don't map uid/gid values by user/group name

    * usermap : str, None
              : custom username mapping

    * groupmap : str, None
               : custom groupname mapping

    * chown : str, None
            : simple username/groupname mapping

    * timeout : int, None
              : set I/O timeout in seconds

    * contimeout : int, None
                 : set daemon connection timeout in seconds

    * ignore_times : bool, None
                   : don't skip files that match in size and mod-time

    * remote-option : str, None
                    : send OPTION to the remote side only

    * size_only : bool, None
                : skip files that match in size

    * modify_window : int, None
                    : compare mod-times with reduced accuracy

    * temp_dir : str, None
               : create temporary files in directory DIR

    * fuzzy : bool, None
            : find similar file for basis if no dest file

    * compare_dest : str, None
                   : also compare destination files relative to DIR

    * copy_dest : str, None
                : ... and include copies of unchanged files

    * link_dest : str, None
                : hardlink to files in DIR when unchanged

    * compress : bool, None
               : compress file data during the transfer

    * compress_level : int, None
                     : explicitly set compression level

    * skip_compress : list, None
                    : skip compressing files with a suffix in LIST

    * cvs_exclude : bool, None
                  : auto-ignore files the same way CVS does

    * filter : list, None
             : add a file-filtering RULE

    * exclude : list, None
              : exclude files matching PATTERN

    * exclude_from : str, None
                   : read exclude patterns from FILE

    * include : list, None
              : don't exclude files matching PATTERN

    * include_from : str, None
                   : read include patterns from FILE

    * files_from : str, None
                 : read list of source-file names from FILE

    * from0 : bool, None
            : all *-from/filter files are delimited by 0s

    * protect_args : bool, None
                   : no space-splitting; only wildcard special-chars

    * address : str, None
              : bind address for outgoing socket to daemon

    * port : int, None
           : specify double-colon alternate port number

    * sockopts : str, None
               : specify custom TCP options

    * blocking_io : bool, None
                  : use blocking I/O for the remote shell

    * stats : bool, None
            : give some file-transfer stats

    * 8_bit_output : bool, None
                   : leave high-bit chars unescaped in output

    * human_readable : bool, None
                     : output numbers in a human-readable format

    * progress : bool, None
               : show progress during transfer

    * itemize_changes : bool, None
                      : output a change-summary for all updates

    * out_format : str, None
                 : output updates using the specified FORMAT

    * log_file : str, None
               : log what we're doing to the specified FILE

    * log_file_format : str, None
                      : log updates using the specified FMT

    * password_file : str, None
                    : read daemon-access password from FILE

    * list_only : bool, None
                : list the files instead of copying them

    * bwlimit : int, None
              : limit socket I/O bandwidth

    * outbuf : str, None
             : set output buffering to None, Line, or Block

    * write_batch : str, None
                  : write a batched update to FILE

    * only_write_batch : str, None
                       : like --write-batch but w/o updating destination

    * read_batch : str, None
                 : read a batched update from FILE

    * protocol : int, None
               : force an older protocol version to be used

    * iconv : str, None
            : request charset conversion of filenames

    * checksum_seed : int, None
                    : set block/file checksum seed (advanced)

    * ipv4 : bool, None
           : prefer IPv4

    * ipv6 : bool, None
           : prefer IPv6


Requirements:

    * rsync
      to install, for example run `apt-get install rsync`

"""
import os
from pybuildtool import BaseTask, expand_resource, make_list

tool_name = __name__

class Task(BaseTask):

    name = tool_name
    conf = {
        '_source_grouped_': True,
    }
    target = None
    workdir = None

    def prepare(self):
        cfg = self.conf
        args = self.args

        c = cfg.get('target')
        if c is None:
            self.bld.fatal('"target" is required by %s' % tool_name)
        else:
            self.target = c.format(**self.group.get_patterns())

        c = cfg.get('work_dir')
        if c:
            self.workdir = expand_resource(self.group, c)

        self.add_bool_args('verbose', 'msgs2stderr', 'quiet', 'checksum',
                'archive', 'recursive', 'relative', 'no_implied_dirs', 'backup',
                'update', 'inplace', 'append', 'append_verify', 'dirs', 'links',
                'copy_links', 'copy_unsafe_links', 'safe_links', 'munge_links',
                'copy_dirlinks', 'keep_dirlinks', 'hard_links', 'perms',
                'executability', 'acls', 'xattrs', 'owner', 'group', 'devices',
                'specials', 'times', 'omit_dir_times', 'omit_link_times',
                'super', 'fake_super', 'sparse', 'preallocate', 'dry_run',
                'whole_file', 'one_file_system', 'existing', 'ignore_existing',
                'remove_source_files', 'delete', 'delete_before',
                'delete_during', 'delete_delay', 'delete_after',
                'delete_excluded', 'ignore_missing_args', 'delete_missing_args',
                'ignore-errors', 'force', 'partial', 'delay_updates',
                'prune_empty_dirs', 'numeric_ids', 'ignore_times', 'size_only',
                'fuzzy', 'compress', 'cvs_exclude', 'from0', 'protect_args',
                'blocking_io', 'stats', '8_bit_output', 'human_readable',
                'progress', 'itemize_changes', 'list_only', 'ipv4', 'ipv6')

        self.add_int_args('block_size', 'max_delete', 'max_size', 'min_size',
                'timeout', 'contimeout', 'modify_window', 'compress_level',
                'port', 'bwlimit', 'protocol', 'checksum_seed')

        self.add_list_args_join(',', 'skip_compress')

        self.add_list_args_multi('filter', 'exclude', 'include')

        self.add_path_args('backup_dir', 'exclude_from', 'include_from',
                'files_from', 'password_file', 'read_batch')

        self.add_str_args('info', 'debug', 'suffix', 'chmod', 'rsh',
                'rsync_path', 'partial_dir', 'usermap', 'groupmap', 'chown',
                'remote_option', 'temp_dir', 'compare_dest', 'copy_dest',
                'link_dest', 'address', 'sockopts', 'out_format', 'log_file',
                'log_file_format', 'write_batch', 'only_write_batch', 'iconv')

        c = cfg.get('no_MOTD')
        if c:
            args.append('--no-motd')

        c = make_list(cfg.get('no_OPTION'))
        for option in c:
            args.append('--no-' + option)

        c = cfg.get('outbuf')
        if c:
            args.append('--outbuf=' + c[1].upper())


    def perform(self):
        if not self.file_in:
            self.bld.fatal('%s needs input' % tool_name.capitalize())
        if self.file_out:
            self.bld.fatal("%s doesn't produce output" % tool_name.capitalize())

        if self.conf.get('relative') and self.workdir:
            inputs = [os.path.relpath(x, self.workdir) for x in self.file_in]
        else:
            inputs = self.file_in

        kwargs = {}
        if self.workdir is not None:
            kwargs['cwd'] = self.workdir

        executable = self.env['%s_BIN' % tool_name.upper()]
        return self.exec_command(
            "{exe} {arg} {in_} {out}".format(
            exe=executable,
            arg=' '.join(self.args),
            in_=' '.join(inputs),
            out=self.target,
        ),
        **kwargs)


def configure(conf):
    conf.env['%s_BIN' % tool_name.upper()] = conf.find_program('rsync')[0]
