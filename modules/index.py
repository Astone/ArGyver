from verbose import *
import os
import pickle
import hashlib
from copy import copy

INITIAL_INDEX = {'inode_to_files':{}, 'hash_to_inode': {}}

BLOCK_SIZE = 2**20

class Index(object): 
    
    config = None
    index = None
        
    def __init__(self, config):
        self.config = config
        self.index = self.config.get_server_index()

    def rebuild(self):
        notice("Rebuilding index file")
        self.flush()
        self.update()
    
    def flush(self):
        notice("Flushing index file")
        self.index = INITIAL_INDEX

    def update(self):
        notice("Updating index file")

        for (hash, inode) in self.index['hash_to_inode'].items():
            for path in copy(self.index['inode_to_files'][inode]):
                if not os.path.exists(self.get_abs_path(path)):
                    debug("File \"%s\" no longer exists." % path)
                    self.remove_file(path, hash)
                            
        for root in [self.config.get_server_archive(), self.config.get_server_snapshot()]:
            for (path, dirs, files) in os.walk(root):
                for file in files:
                    file_path = os.path.join(path, file)
                    self.add_file(file_path)
        self.save()

    def add_file(self, path):
        inode = os.stat(path).st_ino
        relpath = self.get_rel_path(path)

        if not inode in self.index['inode_to_files']:
            debug("Inode %d (%s) is not in the index." % (inode, relpath))
            hash = self.hash(path)
            if hash in self.index['hash_to_inode']:
                inode = self.index['hash_to_inode'][hash]
                rel_unique_path = self.index['inode_to_files'][inode][0]
                unique_path = self.get_abs_path(rel_unique_path)
                debug("File \"%s\" with the same contents as \"%s\" is in the index." % (rel_unique_path, relpath))
                atime = max(os.stat(path).st_atime, os.stat(unique_path).st_atime)
                mtime = max(os.stat(path).st_mtime, os.stat(unique_path).st_mtime)
                os.remove(path)
                os.link(unique_path, path)
                os.utime(path, (atime, mtime))
                notice("\"%s\" linked to \"%s\"." % (relpath, rel_unique_path))
            else:
                self.index['hash_to_inode'][hash] = inode
                self.index['inode_to_files'][inode] = []
                notice("Inode %d (%s) added to the index." % (inode, relpath))

        if not relpath in self.index['inode_to_files'][inode]:
            debug("File \"%s\" is not in the index." % relpath)
            self.index['inode_to_files'][inode].append(relpath)
            notice("File \"%s\" added to the index." % relpath)
    
    def remove_file(self, path, hash = None):
        if hash == None:
            fatal("TODO: get hash key from file name in index.Index.remove_file()")

        inode = self.index['hash_to_inode'][hash]
        self.index['inode_to_files'][inode].remove(path)    
        notice("File \"%s\" removed from index." % path)

        if len(self.index['inode_to_files'][inode]) == 0:
            debug("No files with inode \"%d\" exist any longer." % inode)
            del self.index['inode_to_files'][inode]
            del self.index['hash_to_inode'][hash]
            notice("Inode \"%d\" removed from index." % inode)

    def move_file(self, src, dst, inode = None):
        if inode == None:
            if os.path.isfile(src):
                inode = os.stat(src).st_ino
            elif os.path.isfile(dst):
                inode = os.stat(dst).st_ino
            else:
                fatal("Both \"%s\" and \"%s\" do not exist." % (src, dst)) 
        src = self.get_rel_path(src)
        dst = self.get_rel_path(dst)
        notice("Move file \"%s\" (with inode %d) to \"%s\" in the index." % (src, inode, dst))
        self.index['inode_to_files'][inode].remove(src)
        if not dst in self.index['inode_to_files'][inode]:
            self.index['inode_to_files'][inode].append(dst)
            
    def get_rel_path(self, abspath):
        relpath = os.path.relpath(abspath, self.config.get_server_root())
        return relpath
    
    def get_abs_path(self, relpath):
        abspath = os.path.abspath(os.path.join(self.config.get_server_root(), relpath))
        return abspath
    
    def hash(self, path):
        hash = hashlib.new('md5')
        fp = open(path, 'rb')
        data = True
        while data:
            del data
            data = fp.read(BLOCK_SIZE)
            hash.update(data)
        fp.close
        return hash.digest()

    def get_inode(self, hash):
        if hash in self.index['hash_to_inode']:
            return self.index['hash_to_inode'][hash]
        else:
            return None

    def get_files(self, inode):
        if inode in self.index['inode_to_files']:
            return self.index['inode_to_files'][inode]
        else:
            return []

    def file_has_hash(self, path, hash):
        relpath = self.get_rel_path(path)
        inode = self.get_inode(hash)
        if inode:
            return relpath in self.get_files(inode)
        else:
            return False

    def save(self):
        idx = self.config.get_server_index_file()
        notice("Index saved to %s" % self.get_rel_path(idx))
        pickle.dump(self.index, open(idx, 'w'), 2)
