#!/usr/bin/env python2.7
from verbose import *
from config import Config
from pidlock import PidLock
from filelinker import FileLinker
from dbfilelinker import DbFileLinker
from datetime import datetime
import os, shutil
from subprocess import check_output, CalledProcessError

class ArGyver(object):
    
    config = None
    sources = []
    
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
            for [dst, src] in self.sources.iteritems():
                self.rsync(src, dst)
                self.update_db_snapshot()
                self.archive()
                self.link_files()
            self.update_db_repository()
# TODO:     self.update_db_history()
            self.remove_tmp_folder()

            # Remove some garbage
            
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

        rsync = [cmd] + opt + ['--delete'] + bu + [src] + [snapshot]
        
        debug(' '.join(rsync))

        try:
            # Execute the rsync command and capture the output.
            output = check_output([cmd] + opt + ['--delete'] + bu + [src] + [snapshot])

        except CalledProcessError as e:
            # Display an error if the rsync command fails.
            error(str(e))

        else:
            # Or display a debug if the rsync command was succesfull.
            notice(output)

        notice("Synchronisation of \"%s\" (%s) finished." % (src, dst))

    def update_db_snapshot(self):
        db = self.config.get_server_database()
        if db == None:
            debug("Database is disabled.")
            return
        db.connect()
        db.delete_old_items(self.config.get_server_snapshot(), self.config.get_server_tmp())
        db.add_new_items(self.config.get_server_snapshot())
        db.close()
    
    def update_db_repository(self):
        db = self.config.get_server_database()
        if db == None:
            debug("Database is disabled.")
            return
        if self.config.get_server_repository() == None:
            debug("File linker is disabled.")
            return
        db.connect()
        db.add_new_repository_entries(self.config.get_server_repository())
        db.update_inodes(self.config.get_server_snapshot())
        db.close()

    def update_db_history(self):
        db = self.config.get_server_database()
        if db == None:
            debug("Database is disabled.")
            return
        db.connect()
        db.update_history()
        db.close()

    def archive(self):
    
        # If the archivation is disabled, do nothing
        if self.config.get_server_archive() == None:
            debug("Archivation is disabled.")
            return

        notice("Starting archivation.")

        # Construct the absolute archive path and the absolute temparory path.
        arch_root = self.config.get_server_archive()
        tmp_root = self.config.get_server_tmp()

        # Walk through all temporary folders recursively.
        for (path, _folders, files) in os.walk(tmp_root):

            # Extract the path of the temporary folder relative to the tmp_root.
            path = os.path.relpath(path, tmp_root)
            if path == '.':
                path = ''

            # Make sure this folter exists in the archive folder or create it if it doesn't.
            if not os.path.isdir(os.path.join(arch_root, path)):
                try:
                    debug("Make dir \"%s\"" % path)
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
                debug("Move \"%s\" to \"%s\"" % (os.path.join(path, tmp_name), os.path.join(path, arch_name)))
                try:
                    os.rename(tmp_path, arch_path)
                except Exception as e:
                    error("Tried to move \"%s\" to \"%s\" ... FAILED" % (tmp_path, arch_path))
                    error(str(e))

        notice("Archivation of finished.")

    def link_files(self):

        # If data linking is disabled, do nothing
        if self.config.get_server_repository() == None:
            debug("File linking is disabled.")
            return

        # Construct the absolute folder and repository
        snapshot = self.config.get_server_snapshot()
        repository = self.config.get_server_repository() 

        # Create a data linker instance and let it do the work
        db = self.config.get_server_database()
        if db == None:
            notice("Starting fs based file linking.")
            linker = FileLinker(snapshot, repository)
            linker.run()
        else:
            notice("Starting db based file linking.")
            db.connect()
            linker = DbFileLinker(snapshot, repository, db)
            linker.run()
            db.close()

        notice("File linking finished.")
        notice(str(linker))

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

    def rebuild_repository(self):
        warning("rebuild_repository() should update all inode references in a database.")
        fatal("rebuild_repository() not implemented!")

# These three lines let the ArGyver actually do something
if __name__ == '__main__':
    A = ArGyver()
    A.run()

