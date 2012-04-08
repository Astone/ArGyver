#!/usr/bin/env python

import os
import hashlib
from verbose import *
from argparse import ArgumentParser

BUFF_SIZE = 4 * (2**16) # 4MB

class FileLinker(object):

    folder = None
    repository = None
    force = False
    for_real = True
    
    def __init__(self, folder=".", repository=".data"):
        self.folder = os.path.abspath(folder)
        self.repository = os.path.abspath(repository)

    def parse_arguments(self):
        parser = ArgumentParser(description='Save space by hardlinking identical files')

        parser.add_argument(
            '-s', dest='source', required=True,
            help='The folder containing the original files.')

        parser.add_argument(
            '-d', dest='dest', required=True,
            help='A (hidden) folder containing all original files in an indexed structure')

        parser.add_argument(
            '-f', dest='force', action="store_true"
            help='Force adding files even if they are allready hadlinked to another file')

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
        self.force = args.force
        set_log_file(args.log_file, args.log_level)
        set_verbosity(args.verbosity)

    def run(self):
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
                # If the file is not linked to any other file, it should to be indexed
                if self.force or stats.st_nlink == 1:

                    # Retrieve a unique index path based on the file's contents
                    idx_path = self.get_index_path(file_path)
                
                    if idx_path == None:
                        continue

                    # If the file is not yet in the index, store it, otherwise just link to the indexed file                    
                    if not os.path.isfile(idx_path):
                        if not os.path.islink(file_path):
                            self.store_file(file_path, idx_path)
                    else:
                        self.link_file(file_path, idx_path)               

    def store_file(self, file_path, idx_path):
        debug("Storing %s at %s" % (os.path.relpath(file_path, self.folder), os.path.relpath(idx_path, self.repository)))
        idx_dir = os.path.dirname(idx_path)
        if not os.path.isdir(idx_dir):
            debug("Make dir %s" % os.path.relpath(idx_dir, self.repository))
            if self.for_real:
                os.makedirs(idx_dir)
        if self.for_real:
            os.link(file_path, idx_path)

    def link_file(self, file_path, idx_path):
        debug("Linking %s to %s" % (os.path.relpath(file_path, self.folder), os.path.relpath(idx_path, self.repository)))
        file_stats = os.stat(file_path)
        idx_stats = os.stat(idx_path)
        atime = max(file_stats.st_atime, idx_stats.st_atime)
        mtime = max(file_stats.st_mtime, idx_stats.st_mtime)
        if self.for_real:
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

    def get_index_path(self, file_path):
        file_hash = self.get_file_hash(file_path)
        if file_hash == None:
            return 
        return os.path.join(self.repository, file_hash[0:2], file_hash)
        
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

if __name__ == "__main__":
    linker = FileLinker()
    linker.parse_arguments()
    linker.run()

