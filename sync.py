from verbose import *
from config import Config
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
        notice("Synchronisation started for \"%s\" (%s)." % (src, dst))
        cmd = 'rsync'
        opt = self.config.get_rsync_options().split()
        bu = ['--delete', '-b', '--backup-dir=%s' % os.path.join(self.config.get_server_tmp(), dst)]
        snapshot = os.path.join(self.config.get_server_snapshot(), dst)
        try:
            notice(check_output([cmd] + opt + bu + [src] + [snapshot]))
        except CalledProcessError as e:
            error(str(e))

    def archive(self, folder):
        notice("Archivation started for \"%s\"." % (folder))
        archive_root = os.path.join(self.config.get_server_archive(), folder)
        tmp_root = os.path.join(self.config.get_server_tmp(), folder)
        for (path, _folders, files) in os.walk(tmp_root):
            tmp_path = os.path.join(tmp_root, path)
            print tmp_path, files
        