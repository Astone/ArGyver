#!/usr/bin/env python2.7

import os
import hashlib
import math
from verbose import *
from argparse import ArgumentParser

BUFF_SIZE = 4 * (2**16) # 4MB

class FileLinker(object):

    folder = None
    repository = None
    inodes = None
    new_bytes = 0
    linked_bytes = 0

    def __init__(self, folder=".", repository=".data", inodes=None):
        self.folder = os.path.abspath(folder)
        self.repository = os.path.abspath(repository)
        self.inodes = inodes

    def parse_arguments(self):
        parser = ArgumentParser(description='Save space by hardlinking identical files')

        parser.add_argument(
            '-s', dest='source', required=True,
            help='The folder containing the original files.')

        parser.add_argument(
            '-d', dest='dest', required=True,
            help='A (hidden) folder containing all original files in an indexed structure')

        parser.add_argument(
            '-l', dest='log_file',
            help='Log all actions to a log file')

        parser.add_argument(
            '-ll', dest='log_level', type=int, choices=range(0, 6), default=5,
            help='The verbosity level for the log file. 0=quiet, 1=fatal errors, 2=errors, 3=warnings, 4=notices, 5=debug')

        parser.add_argument(
            '-v', dest='verbosity', type=int, choices=range(0, 6), default=4,
            help='The verbosity level. 0=quiet, 1=fatal errors, 2=errors, 3=warnings, 4=notices, 5=debug')

        args = parser.parse_args()
        self.folder = os.path.abspath(args.source)
        self.repository = os.path.abspath(args.dest)
        set_log_file(args.log_file, args.log_level)
        set_verbosity(args.verbosity)

    def run(self):
        inodes = self.get_inodes()
        for (path, folders, files) in os.walk(self.folder):

            # Walk trough the file system
            for file_name in files:

                # COntruct a proper path
                file_path = os.path.join(path, file_name)

                # This might seem strange, but if the file is a symbolic link to
                # non existing location (or a folder) this would cause us trouble.
                if not os.path.isfile(file_path):
                    continue

                stats = os.stat(file_path)
                # If the file is not linked to the repository, it should to be indexed and linked
                if not stats.st_ino in inodes:

                    # Retrieve a unique index path based on the file's contents
                    idx_path = self.get_index_path(file_path)
                
                    if idx_path == None:
                        continue

                    # If the file is not yet in the index, store it, otherwise just link to the indexed file                    
                    if not os.path.isfile(idx_path):
                        if not os.path.islink(file_path):
                            self.store_file(file_path, idx_path)
                            inodes[stats.st_ino] = None
                    else:
                        self.link_file(file_path, idx_path)

    def get_inodes(self):
        if self.inodes == None:
            debug("Loading repository")
            self.inodes = {}
            for (path, folders, files) in os.walk(self.repository):
                for file in files:
                    self.inodes[os.stat(os.path.join(path, file)).st_ino] = None
            debug("%d inodes loaded" % len(self.inodes))
        return self.inodes

    def store_file(self, file_path, idx_path):
        debug("Storing %s at %s" % (os.path.relpath(file_path, self.folder), os.path.relpath(idx_path, self.repository)))
        idx_dir = os.path.dirname(idx_path)
        if not os.path.isdir(idx_dir):
            debug("Make dir %s" % os.path.relpath(idx_dir, self.repository))
            os.makedirs(idx_dir)
        try:
            os.link(file_path, idx_path)
        except Exception as e:
            os.rename(tmp_path, file_path)
            error("Tried to store %s to %s." % (file_path, idx_path))
            error(str(e))
        self.new_bytes += os.stat(idx_path).st_size

    def link_file(self, file_path, idx_path):
        debug("Linking %s to %s" % (os.path.relpath(file_path, self.folder), os.path.relpath(idx_path, self.repository)))
        file_stats = os.stat(file_path)
        idx_stats = os.stat(idx_path)
        atime = max(file_stats.st_atime, idx_stats.st_atime)
        mtime = max(file_stats.st_mtime, idx_stats.st_mtime)
        tmp_path = file_path + '.tmp'
        os.rename(file_path, tmp_path)
        try:
            os.link(idx_path, file_path)
        except Exception as e:
            os.rename(tmp_path, file_path)
            error("Tried to link %s to %s." % (file_path, idx_path))
            error(str(e))
        else:
            os.unlink(tmp_path)
        try:
            os.utime(idx_path, (atime, mtime))
        except Exception as e:
            error("Tried to change the timestamp of %s to atime=%d, mtime=%d." % (file_path, atime, mtime))
            error(str(e))
        self.linked_bytes += idx_stats.st_size

    def get_index_path(self, file_path):
        file_hash = self.get_file_hash(file_path)
        if file_hash == None:
            return 
        return os.path.join(self.repository, file_hash[0:2], file_hash)

    def __str__(self):
        return "%s: %s added to the repository, %s saved by linking files." % (self.__class__.__name__, pretty_size(self.new_bytes), pretty_size(self.linked_bytes))
        
    @staticmethod
    def get_file_hash(file_path):
        try:
            filePointer = open(file_path, 'rb')
        except Exception as e:
            warning("Can't find file \"%s\"" % file_path)            
            return None
        md5 = hashlib.md5()
        while True:
            dataBlock = filePointer.read(BUFF_SIZE)                
            if not dataBlock:
                break
            md5.update(dataBlock)
        filePointer.close()
        return md5.hexdigest()

def pretty_size(size):
    size = float(size)
    if (size > 1000 * 2**40): return "%.2f PB" % (size / 2**50) 
    if (size > 1000 * 2**30): return "%.2f TB" % (size / 2**40) 
    if (size > 1000 * 2**20): return "%.2f GB" % (size / 2**30) 
    if (size > 1000 * 2**10): return "%.2f MB" % (size / 2**20) 
    if (size > 1000):         return "%.2f KB" % (size / 2**10) 
    return "%d bytes" % size;

if __name__ == "__main__":
    linker = FileLinker()
    linker.parse_arguments()
    linker.run()
    print linker

