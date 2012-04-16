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
                time INTEGER NOT NULL \
            );')
        self.execute(' \
            CREATE TABLE items ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                parent INTEGER, \
                name TEXT NOT NULL \
            );')
        self.execute(' \
            CREATE TABLE versions ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                item INTEGER NOT NULL, \
                inode INTEGER NULL, \
                time INTEGER NULL, \
                size INTEGER NOT NULL, \
                created INTEGER NOT NULL, \
                deleted INTEGER NULL, \
                previous_version INTEGER NULL \
            );')
        self.execute(' \
            CREATE TABLE repository ( \
                inode INTEGER NULL, \
                checksum TEXT NOT NULL, \
                size INTEGER NOT NULL \
            );')

    def create_indexes(self):
        self.execute('CREATE UNIQUE INDEX idx_iterations_id ON iterations (id);')

        self.execute('CREATE UNIQUE INDEX idx_items_id ON items (id);')
        self.execute('CREATE INDEX idx_items_parent ON items (parent);')
        self.execute('CREATE INDEX idx_items_name ON items (name);')

        self.execute('CREATE UNIQUE INDEX idx_versions_id ON versions (id);')
        self.execute('CREATE INDEX idx_versions_item ON versions (item);')
        self.execute('CREATE INDEX idx_versions_inode ON versions (inode);')
        self.execute('CREATE INDEX idx_versions_created ON versions (created);')
        self.execute('CREATE INDEX idx_versions_deleted ON versions (deleted);')
        self.execute('CREATE INDEX idx_versions_previous ON versions (previous_version);')

        self.execute('CREATE UNIQUE INDEX idx_repository_inode ON repository (inode);')
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
            for item_name in folders + files:

                # Construct the path to the folder or file in the snapshot and in the temporary folder
                temp_path = os.path.join(path, item_name)
                snap_path = os.path.join(snapshot, os.path.relpath(temp_path, temp))
                
                # If the source path is a symbolic link, ignore it
                if os.path.islink(temp_path):
                    debug("Tried to delete %s in the DB, but it is a symbolic link." % temp_path)
                    continue

                # If the source path does not exist, 'throw' an error
                if not os.path.exists(temp_path):
                    fatal("Tried to close %s in the DB, but it doesn't exist." % temp_path)
                    continue

                # Construct the relative path
                rel_path = os.path.relpath(snap_path, snapshot)
                
                # Get the item's id from the database
                fid = self._get_item_id_by_path(rel_path)

                # If it is not in the database, throw a error, otherwise close it
                if fid == None:
                    fatal("Path id of %s could not be found in the database" % rel_path)
                    continue
                
                version = self._get_current_version(fid)
                
                # If there is no open version, throw a error, otherwise close it
                if version == None:
                    fatal("There is no version of %s in the database" % rel_path)

                self._delete_version(version['id'])

                if os.path.isdir(snap_path):
                    self._add_folder_version(fid, version['time'], version['size'])

        # Remove deleted empty folders
        for fid in self._get_empty_folder_ids(folder):
            rel_path = self._get_path_by_item_id(fid)
            snap_path = os.path.join(snapshot, rel_path)
            if not os.path.exists(snap_path):
                debug("Closing empty folder %s" % rel_path)
                version = self._get_current_version(fid)
                # If there is no open version, throw a error, otherwise close it
                if version == None:
                    error("There is no version of %s in the database" % rel_path)
                self._delete_version(version['id'])
                


        # Save all changes to the database
        self.commit()
    
    def add_new_paths(self, root, folder):

        folder += os.path.sep

	# Make sure the root is in the database
        if self._get_path_id(folder) == None:
            stat = os.stat(os.path.join(root, folder))
            pid = self._add_path(folder)
            self._add_folder(0, folder.rstrip(os.path.sep), folder)
            self._add_version(pid, None, stat.st_mtime)

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
                    fatal("Tried to add path %s to the DB, but it doesn't exist on the disk." % abs_path)
                    continue

                # Get some folder/file statistics
                stat = os.stat(abs_path)
                inode = stat.st_ino
                time = stat.st_mtime

                # Determine the relative path to the snapshot folder                
                rel_path = os.path.relpath(abs_path, root)
                
                # Add a slash if it is a folder
                if os.path.isdir(abs_path):
                    rel_path += os.path.sep
                    inode = None

                # Check if the path is allready in the database
                fid = self._get_item_id_by_path(rel_path)
                
                # If it is not, add it (parent folders are automatically added table)
                if fid == None:
                    fid = self._add_item(rel_path)

                    # If the path is a folder itself, add it to the folders table as well
                    if os.path.isdir(abs_path):
                        self._find_or_add_folder(rel_path.rstrip(os.path.sep))

                # If it didn't exist or it was removed earlier, add a new version
                if not self._path_is_open(fid):
                    self._add_version(fid, inode, time)

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
                    stat = os.stat(os.path.join(path, checksum))
                    self._add_checksum(checksum, stat.st_ino, stat.st_size)

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
                fatal("Path %s could not be found" % abs_path)
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
        debug("DB: Adding iteration")
        query = 'INSERT INTO iterations (time) VALUES (?);'
        result = self.execute(query, mktime(datetime.now().timetuple()))
        return result.lastrowid

    def _add_folder_version(self, fid, time=None, size=0):
        debug("DB: Adding version (folder=%d)" % fid)
        query = 'INSERT INTO versions (item, time, size, created) VALUES (?, ?, ?, ?);'
        result = self.execute(query, fid, time, size, self.iteration)
        return result.lastrowid
        
    def _get_item_id_by_path(self, path, parent=0):
        if not isinstance(path, list):
            items = path.split(os.path.sep)
        query = 'SELECT id FROM items WHERE parent = ? AND name = ?;'
        record = self.execute(query, parent, items[0].decode('utf-8')).fetchone()
        if record != None:
            fid = record[0]
            if len(items) > 1:
                return self._get_item_id_by_path(items[1:], fid)
            else:
                return fid
        return None

    def _get_path_by_item_id(self, fid):
        query = 'SELECT name, parent FROM items WHERE id = ? ;'
        record = self.execute(query, fid).fetchone()
        if record == None:
            fatal("Item %d not found in the database." % fid)
            return None
        name = record[0].encode('utf-8')
        fid = record[1]
        if fid > 0:
            path = self._get_path_by_item_id(self, fid) 
            if path == None:
                return None
            return path + os.path.sep + name
        return name
        
    def _delete_version(self, vid):
        debug("DB: Closing version (id=%d)" % vid)
        query = 'UPDATE versions SET deleted = ? WHERE id = ? ;'
        self.execute(query, self.iteration, vid)

    def _get_current_version(self, item_id):
        query = 'SELECT * FROM versions WHERE item = ? AND deleted IS NULL';
        return self.execute(query, item_id).fetchone()

    def _get_empty_folders(self):
        query = 'SELECT * FROM items JOIN versions ON (WHERE size = 0 AND inode IS NULL AND deleted IS NULL)';
        data = self.execute(query).fetchall()
        for record in data:
            record['name'] = record['name'].encode('utf-8')
        return data

################################################################################

    def __add_path(self, path):
        debug("DB: Adding item %s" % path)
        folder_id = self._find_or_add_folder(os.path.dirname(file_path.rstrip(os.path.sep)))
        query = ' \
            INSERT INTO paths \
            (folder, path) VALUES (?, ?);'
        result = self.execute(query, folder_id, file_path.decode('utf-8'))
        return result.lastrecordid


    def __path_is_open(self, id):
        query = ' \
            SELECT * \
            FROM versions \
            WHERE path = ? \
            AND deleted_i IS NULL;'
        record = self.execute(query, id).fetchone()
        if record != None:
            return True
        return False

    def __find_or_add_folder(self, path):
        if path == '':
            return 0
        parent = 0
        subpath = ''
        path = path.split(os.path.sep)
        for folder in path:
            subpath = os.path.join(subpath, folder)
            fid = self._find_folder(parent, folder)
            if fid == None:
                fid = self._add_folder(parent, folder, subpath + os.path.sep)
            parent = fid
        return parent

    def __find_folder(self, parent, name):
        query = ' \
            SELECT id \
            FROM folders \
            WHERE parent = ? \
            AND name = ?;'
        record = self.execute(query, parent, name.decode('utf-8')).fetchone()
        if record != None:
            return record[0]
        return None

    def __get_parent_path(self, path_id):
        query = 'SELECT folders.path FROM folders JOIN paths ON (paths.folder = folders.id) WHERE paths.id = ?;'
        record = self.execute(query, path_id).fetchone()
        if record != None:
            return record[0]
        return None

    def __add_folder(self, parent, name, path):
        debug("DB: Adding folder %s under %d" % (name, parent))
        query = ' \
            INSERT INTO folders \
            (parent, name, path) VALUES (?, ?, ?);'
        result = self.execute(query, parent, name.decode('utf-8'), self._get_path_id(path))
        return result.lastrowid

    def __add_version(self, path_id, inode, time):
        debug("DB: Adding version (path=%d, inode=%s, created=%d)" % (path_id, inode, time))
        query = ' \
            INSERT INTO versions \
            (path, inode, created, created_i) VALUES (?, ?, ?, ?);'
        result = self.execute(query, path_id, inode, time, self.iteration)
        self._update_version(self._get_parent_path(path_id), time)
        return result.lastrowid

    def __close_version(self, path_id):
        debug("DB: Closing version (path=%d)" % path_id)
        query = ' \
            UPDATE versions \
            SET deleted_i = ? \
            WHERE path = ? \
            AND deleted_i IS NULL;'
        self.execute(query, self.iteration, path_id)

    def __update_version(self, path_id, time):
        if path_id == None:
            debug("DB: Not updating version reached the root.")
            return
        debug("DB: Updating version (path=%d, modified=%d)" % (path_id, time))
        query = 'SELECT created FROM versions WHERE path = ? AND deleted_i IS NULL;'
        created = self.execute(query, path_id).fetchone()[0]
        if time > created:
            query = 'UPDATE versions SET created = MAX(created, ?) WHERE path = ? AND deleted_i IS NULL;'
            self._update_version(self._get_parent_path(path_id), time)

    def __get_checksums(self, pattern):
        query = ' \
            SELECT checksum \
            FROM repository \
            WHERE checksum LIKE ? ;'
        return [record[0] for record in self.execute(query, pattern).fetchall()]

    def __add_checksum(self, checksum, inode, size):
        debug("DB: Adding checksum (inode=%d, checksum=%s, size=%d)" % (inode, checksum, size))
        query = ' \
            INSERT INTO repository \
            (id, checksum, size) VALUES (?, ?, ?);'
        self.execute(query, inode, checksum, size)

    def __get_unlinked_files(self, pattern):
        query = ' \
            SELECT versions.id, paths.path \
            FROM paths \
            INNER JOIN versions ON (versions.path = paths.id) \
            LEFT JOIN repository ON (repository.id = versions.inode) \
    		WHERE checksum IS NULL \
    		AND paths.path LIKE ? \
    		AND NOT SUBSTR(paths.path, -1, 1) = ? ;'
        return self.execute(query, pattern, os.path.sep)

    def __get_empty_folders(self, folder):
        query = ' \
            SELECT folder_paths.id, folder_paths.path \
            FROM folders \
            LEFT JOIN paths ON (paths.folder = folders.id) \
            LEFT JOIN versions ON (versions.path = paths.id) \
            JOIN paths as folder_paths ON (folder_paths.id = folders.path AND folder_paths.path LIKE ?) \
            JOIN versions as folder_versions ON (folder_versions.path = folder_paths.id) \
            WHERE versions.id IS NULL OR NOT versions.deleted_i IS NULL \
            AND folder_versions.deleted_i IS NULL \
            GROUP BY folders.id ;'
        return self.execute(query, folder + os.path.sep + '%' + os.path.sep)

    def __set_inode(self, version_id, inode):
        debug("DB: Set inode (version=%d, inode=%d)" % (version_id, inode))
        query = ' \
            UPDATE versions \
            SET inode = ? \
            WHERE id = ?;'
        self.execute(query, inode, version_id)


