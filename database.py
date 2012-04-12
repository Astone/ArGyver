#!/usr/bin/env python

import os
from verbose import *
from datetime import datetime
from time import mktime
import sqlite3 as sql

class Database(object):

    iteration = None
    path = None
    db = None

    def __init__(self, db_path):
        self.path = os.path.abspath(db_path)
        if not os.path.isfile(self.path):
            self.create()
            self.create_indexes()
        else:
            self.connect()
        self.iteration = self._add_iteration()
        debug("DB: Iteration #%d" % self.iteration)
        self.close()

    def connect(self):
        self.db = sql.connect(self.path)

    def close(self):
        debug("DB: Closing connection to database %s" % self.path)
        self.commit()
        self.db.close()

    def create(self):
        debug("DB: Creating empty database %s" % os.path.basename(self.path))
        self.db = sql.connect(self.path)
        self.execute(' \
            CREATE TABLE iterations ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                start INTEGER NOT NULL \
            );')
        self.execute(' \
            CREATE TABLE folders ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                parent INTEGER NOT NULL, \
                name TEXT NOT NULL \
            );')
        self.execute(' \
            CREATE TABLE paths ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                folder INTEGER, \
                path TEXT NOT NULL \
            );')
        self.execute(' \
            CREATE TABLE versions ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                path INTEGER NOT NULL, \
                inode INTEGER NULL, \
                previous_version INTEGER NULL, \
                created INTEGER NOT NULL, \
                deleted INTEGER NULL, \
                created_i INTEGER NOT NULL, \
                deleted_i INTEGER NULL \
            );')
        self.execute(' \
            CREATE TABLE repository ( \
                id INTEGER PRIMARY KEY NOT NULL, \
                checksum TEXT NOT NULL \
            );')

    def create_indexes(self):
        self.execute('CREATE UNIQUE INDEX idx_iterations_id ON iterations (id);')

        self.execute('CREATE UNIQUE INDEX idx_folders_id ON folders (id);')
        self.execute('CREATE INDEX idx_folders_parent ON folders (parent);')

        self.execute('CREATE UNIQUE INDEX idx_paths_id ON paths (id);')
        self.execute('CREATE INDEX idx_paths_folder ON paths (folder);')
        self.execute('CREATE INDEX idx_paths_path ON paths (path);')

        self.execute('CREATE UNIQUE INDEX idx_versions_id ON versions (id);')
        self.execute('CREATE INDEX idx_versions_path ON versions (path);')
        self.execute('CREATE INDEX idx_versions_inode ON versions (inode);')
        self.execute('CREATE INDEX idx_versions_previous ON versions (previous_version);')

        self.execute('CREATE UNIQUE INDEX idx_repository_id ON repository (id);')
        self.execute('CREATE UNIQUE INDEX idx_repository_checksum ON repository (checksum);')

    def execute(self, query, *args):
        cursor = self.db.cursor()
        try:
            cursor.execute(query, args)
        except Exception as e:
            error(str(e))
        return cursor

    def commit(self, commit=True):
        if commit:
            debug("DB: Commit #%d." % self.iteration)
            self.db.commit()

    def delete_old_paths(self, snapshot, temp, folder):
        # For all (sub)folders in the temporary folder (storing all deleted/changed files):
        for (path, folders, files) in os.walk(os.path.join(temp, folder)):
            # For each subfolder and file in the folder:
            for file_name in folders + files:
                # Construct the path to the folder or file in the snapshot and in the temporary folder
                temp_path = os.path.join(path, file_name)
                snap_path = os.path.join(snapshot, os.path.relpath(temp_path, temp))
                
                # If the source path is a symbolic link, ignore it
                if os.path.islink(temp_path):
                    debug("Tried to close %s in the DB, but it is a symbolic link." % temp_path)
                    continue

                # If the source path does not exist, 'throw' an error
                if not os.path.exists(temp_path):
                    error("Tried to close %s in the DB, but it doesn't exist on the disk." % aps_path)
                    continue

                if os.path.isdir(snap_path):
                    debug("Tried to close %s in the DB, but it is folder that stil exists in the snapshot." % temp_path)
                    continue

                # Get some folder/file statistics
                stat = os.stat(abs_path)

                # Try to determine the delition file (= the modification time of the new version)
                if os.path.exists(snap_path):
                    mtime = os.stat(snap_path).st_mtime
                # Set it to zero if the deletion time is unknow. It can be estimated afterwards from the iterations table
                else:
                    mtime = 0

                # Construct the relative path to store in the the database
                rel_path = os.path.relpath(snap_path, snapshot)
                
                # If it is a folder, add a slash
                if os.path.isdir(temp_path):
                    rel_path += os.path.sep

            
                # Check if the path is allready in the database
                pid = self._get_path_id(rel_path)

                # If it is not, throw a warning, otherwise close it
                if pid == None:
                    warning("Path id of %s could not be found in the database" % os.path.relpath(snap_path, snapshot))
                else:
                    self._close_version(pid, inode, mtime)

        # Save all changes to the database
        self.commit()
    
    def add_new_paths(self, root, folder):
        # For all (sub)folders in the destination folder:
        for (path, folders, files) in os.walk(os.path.join(root, folder)):
            # For each subfolder and file in the folder:
            for name in folders + files:
                # The absolute path is the path of the folder + the name of the subfolder or file
                abs_path = os.path.join(path, name)
                
                # If the source path is a symbolic link, ignore it
                if os.path.islink(abs_path):
                    debug("Tried to add path %s to the DB, but it is a symbolic link." % abs_path)
                    continue

                # If the source path does not exist, 'throw' an error
                if not os.path.exists(abs_path):
                    error("Tried to add path %s to the DB, but it doesn't exist on the disk." % abs_path)
                    continue

                # Get some folder/file statistics
                stat = os.stat(abs_path)

                # Determine the relative path to the snapshot folder                
                rel_path = os.path.relpath(abs_path, root)
                
                # Add a slash if it is a folder
                if os.path.isdir(abs_path):
                    rel_path += os.path.sep

                # Check if the path is allready in the database
                pid = self._get_path_id(rel_path)
                
                # If it is not, add it (parent folders are automatically added to the folders table)
                if pid == None:
                    pid = self._add_path(rel_path)

                    # If the path is a folder itself, add it to the folders table as well
                    if os.path.isdir(abs_path):
                        self._get_or_add_folder(rel_path.rstrip(os.path.sep))

                # If it didn't exist or it was removed earlier, add a new version
                if not self._path_is_open(pid):
                    self._add_version(pid, stat.st_ino, stat.st_mtime)

        # Save all changes to the database
        self.commit()

    def add_new_repository_entries(self, repository):
        # Walk through all folders in the repository
        for (path, folders, fs_checksums) in os.walk(repository):
            # For each folder walk through all files (checksums)
            if len(fs_checksums) > 0:

                # We do this in batches, so get the first two characters of the checksums in the current folder (= folder name)
                batch = os.path.basename(path)

                # Get all known checksums in this batch from the databse
                db_checksums = self._get_checksums(batch+'%')

                # Get the set difference to find out wich checksum files are on the disk but not in the database
                new_checksums = set(fs_checksums) - set(db_checksums)
                
                # Add all new checksums acompanied with their inode
                for checksum in new_checksums:                
                    self._add_checksum(checksum, os.stat(os.path.join(path, h)).st_ino)

        # Save all changes to the database
        self.commit()

    def update_inodes(self, root, folder):
    
        # Get a list of unlinked files (=versions) from the database
        unlinked_files = self._get_unlinked_files(folder+'/%');
        
        # For each unlinked version, link it
        for (version_id, rel_path) in unlinked_files:
            
            # Construct the absolute path
            abs_path = os.path.join(root, rel_path.encode('utf-8'))
            
                
            # If the source path is a symbolic link, ignore it
            if os.path.islink(abs_path):
                debug("Tried to close %s in the DB, but it is a symbolic link." % abs_path)
                continue

            #If the path doesn't exist, throw an error
            if not os.path.exists(abs_path):
                error("Path %s could not be found" % abs_path)
                continue

            # Get some folder/file statistics
            stat = os.stat(abs_path)

            # Set the inode
            self._set_inode(version_id, stat.st_ino)

        # Save all changes to the database
        self.commit()

    def update_history(self):
        warning("DB: update_history() is not implemented. This could be used to show if a file is moved, copied, deleted, etc in the GUI.")

    def _add_iteration(self):
        query = ' \
            INSERT INTO iterations \
            (start) VALUES (?);'
        result = self.execute(query, mktime(datetime.now().timetuple()))
        return result.lastrowid

    def _get_path_id(self, file_path):
        query = ' \
            SELECT id \
            FROM paths \
            WHERE path = ?;'
        row = self.execute(query, file_path.decode('utf-8')).fetchone()
        if row != None:
            return row[0]
        return None

    def _path_is_open(self, id):
        query = ' \
            SELECT * \
            FROM versions \
            WHERE path = ? \
            AND deleted IS NULL;'
        row = self.execute(query, id).fetchone()
        if row != None:
            return True
        return False

    def _add_path(self, file_path):
        debug("DB: Adding path %s" % file_path)
        folder_id = self._get_or_add_folder(os.path.dirname(file_path.rstrip(os.path.sep)))
        query = ' \
            INSERT INTO paths \
            (folder, path) VALUES (?, ?);'
        result = self.execute(query, folder_id, file_path.decode('utf-8'))
        return result.lastrowid

    def _get_or_add_folder(self, path):
        parent = 0
        path = path.split(os.path.sep)
        for folder in path:
            fid = self._get_folder(parent, folder)
            if fid == None:
                fid = self._add_folder(parent, folder)
            parent = fid
        return parent

    def _get_folder(self, parent, name):
        query = ' \
            SELECT id \
            FROM folders \
            WHERE parent = ? \
            AND name = ?;'
        row = self.execute(query, parent, name.decode('utf-8')).fetchone()
        if row != None:
            return row[0]
        return None

    def _add_folder(self, parent, name):
        debug("DB: Adding folder %s under %d" % (name, parent))
        query = ' \
            INSERT INTO folders \
            (parent, name) VALUES (?, ?);'
        result = self.execute(query, parent, name.decode('utf-8'))
        return result.lastrowid

    def _add_version(self, path_id, inode, time):
        debug("DB: Adding version (path=%d, inode=%d, created=%d)" % (path_id, inode, time))
        query = ' \
            INSERT INTO versions \
            (path, inode, created, created_i) VALUES (?, ?, ?, ?);'
        result = self.execute(query, path_id, inode, time, self.iteration)
        return result.lastrowid

    def _close_version(self, path_id, inode, time):
        debug("DB: Closing version (path=%d, inode=%d, deleted=%d)" % (path_id, inode, time))
        query = ' \
            UPDATE versions \
            SET deleted = ?, deleted_i = ? \
            WHERE path = ? \
            AND inode = ? \
            AND deleted IS NULL;'
        self.execute(query, time, self.iteration, path_id, inode)

    def _get_checksums(self, pattern):
        query = ' \
            SELECT checksum \
            FROM repository \
            WHERE checksum LIKE ? ;'
        return [row[0] for row in self.execute(query, pattern).fetchall()]

    def _add_checksum(self, file_checksum, inode):
        debug("DB: Adding checksum (inode=%d, checksum=%s)" % (inode, file_checksum))
        query = ' \
            INSERT INTO repository \
            (id, checksum) VALUES (?, ?);'
        self.execute(query, inode, file_checksum)

    def _get_unlinked_files(self, pattern):
        query = ' \
            SELECT versions.id, paths.path \
            FROM paths \
            INNER JOIN versions ON (versions.path = paths.id) \
            LEFT JOIN repository ON (repository.id = versions.inode) \
    		WHERE checksum IS NULL \
    		AND paths.path LIKE ? \
    		AND NOT SUBSTR(paths.path, -1, 1) = ? ;'
        return self.execute(query, pattern, os.path.sep)

    def _set_inode(self, version_id, inode):
        debug("DB: Set inode (version=%d, inode=%d)" % (version_id, inode))
        query = ' \
            UPDATE versions \
            SET inode = ? \
            WHERE id = ?;'
        self.execute(query, inode, version_id)


