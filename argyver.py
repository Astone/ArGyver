#!/usr/bin/env python

from verbose import *
from config import Config
from datetime import datetime
import os, shutil
from subprocess import check_output, CalledProcessError

class ArGyver(object):
    
    config = None
    index = None

    def __init__(self):

	# Load configuration file and parse arguments.
        self.config = Config()

	# Retreive a list of all the source locations.
	# This function will also check if all these locations are accessible.
        self.sources = self.config.get_sources()

    def run(self):
        for [dst, src] in iter(sorted(self.sources.iteritems())):
            self.rsync(src, dst)
            self.archive(dst)

    def rsync(self, src, dst):

        notice("Starting synchronisation of \"%s\" (%s)." % (src, dst))

	# Construct the rsync command.
	# Files that have changed or are deleted are backuped in a temporary folder,
        # archive() will handle these files later on.
        cmd = 'rsync'
        opt = self.config.get_rsync_options().split()
        bu = ['--delete', '-b', '--backup-dir=%s' % os.path.join(self.config.get_server_tmp(), dst)]

	# Construct the absolute snapshot path.
	snapshot = os.path.join(self.config.get_server_snapshot(), dst)
        try:
            # Execute the rsync command and capture the output.
            output = check_output([cmd] + opt + bu + [src] + [snapshot])
        except CalledProcessError as e:
            # Display an error if the rsync command fails.
            error(str(e))
        else:
            # Or display a notice if the rsync command was succesfull.
            notice(check_output([cmd] + opt + bu + [src] + [snapshot]))

        notice("Synchronisation of \"%s\" (%s) finished." % (src, dst))

    def archive(self, folder):
        notice("Starting archivation of \"%s\"." % (folder))

        # Construct the absolute archive path and the absolute temparory path.
        arch_root = os.path.join(self.config.get_server_archive(), folder)
        tmp_root = os.path.join(self.config.get_server_tmp(), folder)

	# Walk through all temporary folders recursively.
        for (path, _folders, files) in os.walk(tmp_root):

            # Extract the path of the temporary folder relative to the tmp_root.
            path = os.path.relpath(path, tmp_root)
            if path == '.':
                path = ''

            # Make sure this folter exists in the archive folder or create it if it doesn't.
            if not os.path.isdir(os.path.join(arch_root, path)):
                try:
                    notice("Make dir \"%s\"" % path)
                    os.makedirs(os.path.join(arch_root, path), os.stat(os.path.join(tmp_root, path)).st_mode)
                except Exception as e:
                    error(str())

            # Move each temporary file to the archive folder using a timestamp as suffix for the filename.
            for tmp_name in files:

                # Construct the absolute path of the temporary file.
                tmp_path = os.path.join(tmp_root, path, tmp_name)

                # Extract the timestamp of the file in the format "YYYYMMDD.HHMMSS".
                try:
                    tmp_time = datetime.fromtimestamp(os.stat(tmp_path).st_mtime).strftime('%Y%m%d.%H%M%S')
                except Exception as e:
                    error(str(e))
                    tmp_time = '00000000.000000'

                # Split the original filename on each period to create a list of file name parts.
                arch_parts = tmp_name.split('.')

                # Insert the timestamp just before the last element of the list (the file extension),
                # or as the last element of the list if the file has no extension.
                arch_parts.insert(max(len(arch_parts) - 1, 1), tmp_time)

                # Combine all elements separated by a period into a string.
                arch_name = '.'.join(arch_parts)

                # Move the temporary file to the archive folder
                arch_path = os.path.join(arch_root, path, arch_name)
                notice("Move \"%s\" to \"%s\"" % (os.path.join(path, tmp_name), os.path.join(path, arch_name)))
                try:
                    os.rename(tmp_path, arch_path)
                except Exception as e:
                    error("Tried to move \"%s\" to \"%s\" ... FAILED" % (tmp_path, arch_path))
                    error(str(e))

        # Remove the entire temporary folder tree for the current source location
        if os.path.isdir(tmp_root):
            notice("Remove temporary folder \"%s\" recursively" % tmp_root)
            try:
                shutil.rmtree(tmp_root)
            except Exception as e:
                error("Tried to remove temporary folder \"%s\"... FAILED" % tmp_root)
                error(str(e))

        notice("Archivation of \"%s\" finished." % (folder))


# These three lines are used to let the ArGyver actually do something
if __name__ == '__main__':
    A = ArGyver()
    A.run()

