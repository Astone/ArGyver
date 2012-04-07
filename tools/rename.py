#!/usr/bin/env python

"""
This is a simple tool to remove time/date tags from file names (and save only the newest file).
This can be usefull when you want to restore a (part of) the directory tree from an ArGyver 1.0 archive folder.

1. Copy the part of the archive tree you want to restore to its destination
2. Run rename.py: ./rename.py -f /path/to/the/destination -v

NOTE: Be carefull not to use the original ArGyver archive folder!

"""

import os, re
from argparse import ArgumentParser

class Renamer(object):
    pattern = r'\.\d{8}\.\d{6}'
    argparser = None
    args = {}    

    def __init__(self):
        self.parse_arguments()

    def parse_arguments(self):
        self.argparser = ArgumentParser(description='Remove time date/tags from file names (and save only the newest file)')

        self.argparser.add_argument(
            '-f', dest='folder', required=True,
            help='Specify the folder that contains a copy of (part of) the archive folder.')

        self.argparser.add_argument(
            '-v', '--verbose', action='store_true',
            help='Verbose output')

        self.args = self.argparser.parse_args()

    def rename(self):
        for (path, dirs, files) in os.walk(self.args.folder):
        
            # Note that the files are ordered alphabetically and thereby multiple versions of the same file are ordered by date and time.
            # The newest versions wil be renamed last, overwriting the earlier versions.
            for filename in sorted(files):

                path_in = os.path.join(path, filename)

                # If the filename has a timestamp, remove the timestamp
                if re.search(self.pattern, path_in):
                    path_out = re.sub(self.pattern, '', path_in)
                    if self.args.verbose:
                        print "`%s` -> `%s`" % (path_in, path_out)
                    os.rename(path_in, path_out)

                else:
                    if self.args.verbose:
                        print "Skipping `%s`" % path_in
               

if __name__ == '__main__':
    r = Renamer();
    r.rename()
