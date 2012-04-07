#!/usr/bin/env python

from verbose import *
from config import Config
from pidlock import PidLock
from filelinker import FileLinker
from datetime import datetime
import os, shutil
from subprocess import check_output, CalledProcessError

class ArGyver(object):
    
    config = None
    
    def __init__(self):

        # Load configuration file and parse arguments.
        self.config = Config()

        # Retrieve a list of all the source locations.
        # This function will also check if all these locations are accessible.
        self.sources = self.config.get_sources()

    def run(self):
        # Assure that only one instance of ArGyver is running.
        lock = PidLock(server_root=self.config.get_server_root())
        if lock.locked():
            warning("ArGyver already running with pid %d, stopping" % lock.pid())
        else:
        
            # Create a lock file in the /tmp folder
            lock.lock()

            # For each source folder: synchronize, archive, free disk space
            for [dst, src] in iter(sorted(self.sources.iteritems())):
                self.rsync(src, dst)
                self.update_db_snapshot(dst)
                self.archive(dst)
                self.link_files(dst)
                self.update_db_repository(dst)

            # Remove some garbage
            self.remove_tmp_folder()
            
            # Remove the lock file
            lock.unlock()

    def rsync(self, src, dst):

        notice("Starting synchronisation of \"%s\" (%s)." % (src, dst))

        # Construct the rsync command.
        # Files that have changed or are deleted are backuped in a temporary
        # folder, archive() will handle these files later on (if this function
        # is enbled in the config file

        cmd = 'rsync'

        opt = self.config.get_rsync_options().split()

        if self.config.get_server_tmp():
            bu = ['-b', '--backup-dir=%s' % os.path.join(self.config.get_server_tmp(), dst)]
        else:
            bu = []

        # Construct the absolute snapshot path.
        snapshot = os.path.join(self.config.get_server_snapshot(), dst)

        try:
            # Execute the rsync command and capture the output.
            output = check_output([cmd] + opt + ['--delete'] + bu + [src] + [snapshot])

        except CalledProcessError as e:
            # Display an error if the rsync command fails.
            error(str(e))

        else:
            # Or display a notice if the rsync command was succesfull.
            notice(output)

        notice("Synchronisation of \"%s\" (%s) finished." % (src, dst))

    def update_db_snapshot(self, folder):
        db = self.config.get_server_database()
        if db == None:
            notice("Database is disabled.")
            return
        notice("Updating database (stage 1) for %s." % folder)
        db.connect()
        db.add_new_files(self.config.get_server_snapshot(), folder)
        db.delete_old_files(self.config.get_server_snapshot(), self.config.get_server_tmp(), folder)
        db.close()
        notice("Updating database (stage 1) for %s finished." % folder)
    
    def update_db_repository(self, folder):
        db = self.config.get_server_database()
        if db == None:
            notice("Database is disabled.")
            return
        notice("Updating database (stage 2) for %s." % folder)
        db.connect()
        db.add_new_repository_entries(self.config.get_server_repository())
        db.link_files_to_repository(self.config.get_server_snapshot(), folder)
        db.close()
        notice("Updating database (stage 2) for %s finished." % folder)

    def archive(self, folder):
    
        # If the archivation is disabled, do nothing
        if self.config.get_server_archive() == None:
            notice("Archivation is disabled.")
            return

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

        notice("Archivation of \"%s\" finished." % (folder))

    def link_files(self, folder):

        # If data linking is disabled, do nothing
        if self.config.get_server_repository() == None:
            notice("File linking is disabled.")
            return

        notice("Starting file linking in \"%s\"." % (folder))

        # Construct the absolute folder and repository
        folder = os.path.join(self.config.get_server_snapshot(), folder)
        repository = self.config.get_server_repository() 

        # Create a data linker instance and let it do the work
        linker = FileLinker(folder, repository)
        linker.run()

        notice("File linking in \"%s\" finished." % (folder))

    def remove_tmp_folder(self):

        # Remove the temporary folder (if it is defined)
        tmp_root = self.config.get_server_tmp()

        if tmp_root == None:
            return

        debug("Removing temporary folder \"%s\" recursively" % tmp_root)

        try:
            shutil.rmtree(tmp_root)
        except Exception as e:
            error("Tried to remove temporary folder \"%s\"... FAILED" % tmp_root)
            error(str(e))

# These three lines let the ArGyver actually do something
if __name__ == '__main__':
    A = ArGyver()
    A.run()

