#!/usr/bin/env python2.7
from verbose import *
from config import Config
from pidlock import PidLock
from filelinker import FileLinker
from dbfilelinker import DbFileLinker
from datetime import datetime
import os, shutil
from subprocess import Popen, PIPE, CalledProcessError

MIN_DISK_SPACE = 10 * (2**30) # 10 GB

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
            warning("ArGyver already running with pid %d!" % lock.pid())
        else:
        
            # Create a lock file in the /tmp folder
            lock.lock()

            # For each source folder: synchronize, archive, free disk space
            for [dst, src] in self.sources.iteritems():
                self.rsync(src, dst)
                self.update_db_snapshot(dst)
                self.archive()
                self.link_files()
            self.update_db_versions()
            self.update_db_repository()
# TODO:     self.update_db_history()
            self.remove_tmp_folder()
            self.finish()
            
            # Remove the lock file
            lock.unlock()

    def rsync(self, src, dst):

        notice(">>> Synchronizing \"%s\" (%s)." % (src, dst))

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
            rsync = Popen([cmd] + opt + ['--delete'] + bu + [src] + [snapshot], stdout=PIPE, stderr=PIPE, shell=False)
            while rsync.poll() == None:
                output = rsync.stdout.readline().strip()
                if output:
                    debug(output)
                """
                err = rsync.stderr.readline().strip()
                if err:
                    error(err)

                disk = os.statvfs(snapshot)
                if disk.f_bsize * disk.f_bavail < MIN_DISK_SPACE:
                    error('Almost out of disk space! (%s of %s used)' % (pretty_size(disk.f_bsize * (disk.f_blocks - disk.f_bavail)), pretty_size(disk.f_bsize * disk.f_blocks)))
                    rsync.terminate()
                    output = rsync.stdout.read().strip()
                    if output:
                        debug(output)
                    err = rsync.stderr.read().strip()
                    if err:
                        error(err)
                    rsync.wait()
                """
            if output:
                notice(output)

        except CalledProcessError as e:
            # Display an error if the rsync command fails.
            error(str(e))

        notice("<<< Synchronisation of \"%s\" (%s) finished.\n" % (src, dst))

    def update_db_snapshot(self, folder):
        db = self.config.get_server_database()
        if db == None:
            debug("Database is disabled.")
            return
        db.connect()
        notice(">>> Removing old files from the database (%s)." % (folder))
        db.delete_old_items(self.config.get_server_snapshot(), self.config.get_server_tmp(), folder)
        notice("<<< Removing old files finished (%s).\n" % (folder))
        notice(">>> Adding new files to the database (%s)." % (folder))
        db.add_new_items(self.config.get_server_snapshot(), folder)
        notice("<<< Adding new files finished (%s).\n" % (folder))
        db.close()
    
    def update_db_versions(self):
        db = self.config.get_server_database()
        if db == None:
            debug("Database is disabled.")
            return
        db.connect()
        notice(">>> Propagating sizes and timestamps trough the database")
        db.propagate_changes()
        notice("<<< Propagating sizes and timestamps finished\n")
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
        notice(">>> Adding new repository entries to the database")
        db.add_new_repository_entries(self.config.get_server_repository())
        notice("<<< Ading repository entries finished\n")
        notice(">>> Updating inodes in the database")
        db.update_inodes(self.config.get_server_snapshot())
        notice("<< Updating inodes finished\n")
        db.close()

    def update_db_history(self):
        db = self.config.get_server_database()
        if db == None:
            debug("Database is disabled.")
            return
        db.connect()
        notice(">>> Updating database history")
        db.update_history()
        notice("<< Updating database history finished\n")
        db.close()

    def archive(self):
    
        # If the archivation is disabled, do nothing
        if self.config.get_server_archive() == None:
            debug("Archivation is disabled.")
            return

        notice(">>> Starting archivation.")

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

        notice("<<< Archivation finished\n")

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
            notice(">>> Starting fs based file linking.")
            linker = FileLinker(snapshot, repository)
            linker.run()
        else:
            notice(">>> Starting db based file linking.")
            db.connect()
            linker = DbFileLinker(snapshot, repository, db)
            linker.run()
            db.close()

        notice(str(linker))
        notice("<<< File linking finished\n")

    def remove_tmp_folder(self):

        # Remove the temporary folder (if it is defined)
        tmp_root = self.config.get_server_tmp()

        if tmp_root == None:
            return

        debug(">>> Removing temporary folder \"%s\" recursively" % tmp_root)

        try:
            shutil.rmtree(tmp_root)
        except Exception as e:
            error("Tried to remove temporary folder \"%s\"... FAILED" % tmp_root)
            error(str(e))

        debug("<<< Removing temporary folder finished\n")

    def finish(self):
        db = self.config.get_server_database()
        if db == None:
            debug("Database is disabled.")
            return
        db.connect()
        db.finish()
        db.close()

    def rebuild_repository(self):
        warning("rebuild_repository() should update all inode references in a database.")
        fatal("rebuild_repository() not implemented!")


def pretty_size(size):
    size = float(size)
    if (size > 1000 * 2**40): return "%.2f PB" % (size / 2**50)
    if (size > 1000 * 2**30): return "%.2f TB" % (size / 2**40)
    if (size > 1000 * 2**20): return "%.2f GB" % (size / 2**30)
    if (size > 1000 * 2**10): return "%.2f MB" % (size / 2**20)
    if (size > 1000):         return "%.2f KB" % (size / 2**10)
    return "%d bytes" % size;

# These three lines let the ArGyver actually do something
if __name__ == '__main__':
    import cProfile
    command = "A = ArGyver(); A.run()"
    cProfile.runctx( command, globals(), locals(), filename="logs/%s.profile" % datetime.now() );
    
