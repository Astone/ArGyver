#!/usr/bin/env python

import os
from verbose import *
from filelinker import FileLinker

class DbFileLinker(FileLinker):

    root = None
    db = None

    def __init__(self, folder, repository, root, db):
        super(DbFileLinker, self).__init__(folder, repository)
        self.root = root
        self.db = db

    def run(self):
        inodes = self.get_inodes()
        for (rel_path,) in self.get_unlinked_files():

            # Contruct a proper path
            abs_path = os.path.join(self.root, rel_path.encode('utf-8'))

            # This might seem strange, but if the file is a symbolic link to
            # non existing location (or a folder) this would cause us trouble.
            if not os.path.isfile(abs_path):
                warning("Skipping %s, file could not be found." % rel_path)
                continue

            stats = os.stat(abs_path)
            # If the file is not linked to the repository, it should to be indexed and linked
            if not stats.st_ino in self.inodes:

                # Retrieve a unique index path based on the file's contents
                idx_path = self.get_index_path(abs_path)
            
                if os.path.islink(abs_path):
                    warning("Skipping %s, it is a symbolic link." % rel_path)
                    continue

                if idx_path == None:
                    warning("Skipping %s, unable to create a checksum." % rel_path)
                    continue

                # If the file is not yet in the index, store it, otherwise just link to the indexed file                    
                if not os.path.isfile(idx_path):
                    self.store_file(abs_path, idx_path)
                    self.inodes[stats.st_ino] = None
                else:
                    self.link_file(abs_path, idx_path)               

    def get_inodes(self):
        if self.inodes == None:
            debug("Loading repository")
            result = self.db.execute('SELECT id FROM repository;')
            if result == None:
                return {}
            else:
               result = result.fetchall()
            inodes = [row[0] for row in result]
            self.inodes = dict(zip(inodes, [None]*len(inodes)))
            debug("%d inodes loaded" % len(self.inodes))
        return self.inodes

    def get_unlinked_files(self):
        debug("Loading unlinked files")
        result = self.db.execute(' \
            SELECT paths.path \
            FROM paths \
            INNER JOIN versions ON (versions.path = paths.id) \
            LEFT JOIN repository ON (repository.id = versions.inode) \
    		WHERE hash IS NULL \
    		AND NOT SUBSTR(paths.path, -1, 1) = ?', os.path.sep)
        if result == None:
            return []
        else:
           return result

