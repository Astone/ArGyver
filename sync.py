from verbose import *
from config import Config
from datetime import datetime
import os
from subprocess import check_output, CalledProcessError

class Sync(object):
    
    config = None
    index = None

    def __init__(self):
        self.config = Config()
        self.sources = self.config.get_sources()

    def run(self):
        for [dst, src] in self.sources.iteritems():
            self.rsync(src, dst)
            self.archive(dst)

    def rsync(self, src, dst):
        notice("Starting synchronisation of \"%s\" (%s)." % (src, dst))
        cmd = 'rsync'
        opt = self.config.get_rsync_options().split()
        bu = ['--delete', '-b', '--backup-dir=%s' % os.path.join(self.config.get_server_tmp(), dst)]
        snapshot = os.path.join(self.config.get_server_snapshot(), dst)
        try:
            notice(check_output([cmd] + opt + bu + [src] + [snapshot]))
        except CalledProcessError as e:
            error(str(e))
        notice("Synchronisation of \"%s\" (%s) completed." % (src, dst))

    def archive(self, folder):
        notice("Starting archivation of \"%s\"." % (folder))
        arch_root = os.path.join(self.config.get_server_archive(), folder)
        tmp_root = os.path.join(self.config.get_server_tmp(), folder)
        for (path, _folders, files) in os.walk(tmp_root):
            path = os.path.relpath(path, tmp_root)
            if path == '.':
                path = ''
            if not os.path.isdir(os.path.join(arch_root, path)):
                try:
                    notice("Make dir \"%s\"" % path)
                    os.makedirs(os.path.join(arch_root, path), os.stat(os.path.join(tmp_root, path)).st_mode)
                except Exception as e:
                    error(str())

            for tmp_name in files:
                tmp_path = os.path.join(tmp_root, path, tmp_name)
                try:
                    tmp_time = datetime.fromtimestamp(os.stat(tmp_path).st_mtime).strftime('%Y%m%d.%H%I%M')
                except Exception as e:
                    error(str(e))
                    rmp_time = '00000000.000000'
                arch_parts = tmp_name.split('.')
                arch_parts.insert(max(len(arch_parts) - 1, 1), tmp_time)
                arch_name = '.'.join(arch_parts)
                arch_path = os.path.join(arch_root, path, arch_name)
                notice("Move \"%s\" to \"%s\"" % (os.path.join(path, tmp_name), os.path.join(path, arch_name)))
                try:
                    os.rename(tmp_path, arch_path)
                except Exception as e:
                    error("Tried to move \"%s\" to \"%s\" ... FAILED" % (tmp_path, arch_path))
                    error(str(e))
        notice("Archivation of \"%s\" completed." % (folder))
