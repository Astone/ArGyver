from verbose import *
from datetime import datetime
import re

class Sync(object):
    
    config = None
    index = None

    def __init__(self, config, index):
        self.config = config
        self.index = index
        self.ssh = config.get_client_ssh()
        self.server_root = config.get_server_root()
        self.client_root = config.get_client_root()

    def update(self):
        for [name, path] in self.config.get_client_src_list().iteritems():    
            tree = self.ssh.tree(path)
            self.archive_removed_and_changed_files(name, path, tree)
            self.download_files(name, path, tree)
            self.index.save()
        
    def archive_removed_and_changed_files(self, relroot, client_root, tree):
        debug("Archive folder \"%s\"" % relroot)
        snapshot = os.path.join(self.config.get_server_snapshot(), relroot)
        archive = os.path.join(self.config.get_server_archive(), relroot)
        for item in os.listdir(snapshot):
            server_path = os.path.join(snapshot, item)
            client_path = os.path.join(self.client_root, client_root, item)
            if os.path.isdir(server_path):
                if item in tree:
                    self.archive_removed_and_changed_files(os.path.join(relroot, item), client_path, tree[item])
                else:
                    self.archive_removed_and_changed_files(os.path.join(relroot, item), client_path, {})
                    notice("Folder \"%s\" is removed" % os.path.relpath(server_path, self.server_root))
                    os.rmdir(server_path)
            else:
                mtime = os.stat(server_path).st_mtime
                if not item in tree or abs(mtime - tree[item]) > 30:
                    if item in tree:
                        client_hash = self.ssh.md5(client_path)
                    else:
                        client_hash = None
                    if self.index.file_has_hash(server_path, client_hash):
                        debug("Timestamps of \"%s\" (server) and \"%s\" (client) differ, but the contents are te same." % (os.path.relpath(server_path, self.server_root), os.path.relpath(client_path, self.client_root)))
                        os.utime(server_path, (os.stat(server_path).st_atime, tree[item]))
                        debug("Timestamp of \"%s\" updated" % os.path.relpath(server_path, self.server_root))
                    else:
                        arch_item = item.split('.')
                        arch_item.insert(max(len(arch_item) - 1, 1), datetime.fromtimestamp(mtime).strftime('%Y%m%d.%H%M%S'))
                        arch_item = '.'.join(arch_item)
                        arch_path = os.path.join(archive, arch_item)
                        notice("Snapshot \"%s\" is archived to \"%s\"" % (os.path.relpath(server_path), os.path.relpath(arch_path, self.server_root)))
                        if not os.path.isdir(archive):
                            os.makedirs(archive)
                        if os.path.isfile(arch_path):
                            os.remove(arch_path)
                        os.rename(server_path, arch_path)
                        self.index.move_file(server_path, arch_path)

    def download_files(self, relroot, client_root, tree):
        debug("Download folder \"%s\"" % client_root)
        server_root = os.path.join(self.config.get_server_snapshot(), relroot)
        for (node, subtree) in tree.iteritems():
            if subtree.__class__ == dict:
                self.download_files(os.path.join(relroot, node), os.path.join(client_root, node), subtree)
            else:
                server_path = os.path.join(server_root, node)
                client_path = os.path.join(client_root, node)
                if not os.path.isfile(server_path):
                    if not os.path.isdir(server_root):
                        os.makedirs(server_root)
                    client_hash = self.ssh.md5(client_path)
                    duplicates = self.index.get_files(client_hash)
                    if len(duplicates) > 0:
                        debug("Copying file \"%s\" as substitute for \"%s\"." % (duplicates[0], client_path))
                        os.link(duplicates[0], server_path)
                    else:
                        debug("Downloading file \"%s\"" % client_path)
                        self.ssh.download(client_path, server_path)
                    self.index.add_file(server_path)
