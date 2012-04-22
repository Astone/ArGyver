#!/usr/bin/env python

import os
from verbose import *
from filelinker import FileLinker
from datetime import datetime
from time import mktime

class DbFileLinker(FileLinker):

    db = None

    def __init__(self, snapshot, repository, db):
        super(DbFileLinker, self).__init__(snapshot, repository)
        self.db = db

    def run(self):
        inodes = self.get_inodes()
        for record in self.db._get_unlinked_files():
            rel_path = self.db._get_path_by_item_id(record['fid'])

            # Contruct a proper path
            abs_path = os.path.join(self.folder, rel_path)

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
            result = self.db._get_inodes_in_repository()
            if result == None:
                return {}
            else:
               result = result.fetchall()
            inodes = [row['inode'] for row in result]
            self.inodes = dict(zip(inodes, [None]*len(inodes)))
            debug("%d inodes loaded" % len(self.inodes))
        return self.inodes

