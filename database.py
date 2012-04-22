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
        self.db.row_factory = sql.Row

    def close(self):
        debug("DB: Closing connection to database %s" % self.path)
        self.commit()
        self.db.close()
        

    def execute(self, query, *args):
        cursor = self.db.cursor()
        try:
            cursor.execute(query, args)
        except Exception as e:
            error(str(e))
            error(query)
        return cursor

    def commit(self, commit=True):
        if commit:
            debug("DB: Commit #%d." % self.iteration)
            self.db.commit()

    def finish(self):
        self._finish_iteration()

    def create(self):
        debug("DB: Creating empty database %s" % os.path.basename(self.path))
        self.db = sql.connect(self.path)
        self.execute(' \
            CREATE TABLE iterations ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                start INTEGER NOT NULL, \
                finished INTEGER NULL \
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
                time INTEGER NOT NULL, \
                size INTEGER NULL, \
                created INTEGER NOT NULL, \
                deleted INTEGER NULL, \
                previous_version INTEGER NULL \
            );')
        self.execute(' \
            CREATE TABLE repository ( \
                inode INTEGER PRIMARY KEY NOT NULL, \
                checksum TEXT NOT NULL \
            );')

    def create_indexes(self):
        self.execute('CREATE UNIQUE INDEX idx_iterations_id ON iterations (id);')

        self.execute('CREATE UNIQUE INDEX idx_items_id ON items (id);')
        self.execute('CREATE INDEX idx_items_parent ON items (parent);')
        self.execute('CREATE UNIQUE INDEX idx_items_name ON items (parent, name);')

        self.execute('CREATE UNIQUE INDEX idx_versions_id ON versions (id);')
        self.execute('CREATE INDEX idx_versions_item ON versions (item);')
        self.execute('CREATE UNIQUE INDEX idx_versions_current ON versions (item, deleted);')
        self.execute('CREATE UNIQUE INDEX idx_versions ON versions (item, created, deleted);')

        self.execute('CREATE UNIQUE INDEX idx_repository_inode ON repository (inode);')
        self.execute('CREATE UNIQUE INDEX idx_repository_checksum ON repository (checksum);')

    def delete_old_items(self, snapshot, temp, folder):

        if os.path.isdir(os.path.join(temp, folder)):
            self.delete_old_item(snapshot, temp, temp, folder)

        # For all (sub)folders in the temporary folder (storing all deleted/changed files):
        for (path, folders, files) in os.walk(os.path.join(temp, folder)):
            parent = self._get_item_id_by_path(os.path.relpath(path, temp))

            # For each subfolder and file in the folder:
            for item_name in folders + files:
                self.delete_old_item(snapshot, temp, path, item_name, parent)

        # Remove deleted empty folders
        for (fid, vid) in self._get_empty_folder_ids():
            rel_path = self._get_path_by_item_id(fid)
            snap_path = os.path.join(snapshot, rel_path)
            if not os.path.exists(snap_path):
                debug("Closing empty folder %s" % rel_path)
                self._delete_version(vid)

        # Save all changes to the database
        self.commit()
    
    def delete_old_item(self, snapshot, temp, path, item_name, parent=0):
        # Construct the path to the folder or file in the snapshot and in the temporary folder
        temp_path = os.path.join(path, item_name)
        snap_path = os.path.join(snapshot, os.path.relpath(temp_path, temp))
                
        # If the source path is a symbolic link, ignore it
        if os.path.islink(temp_path):
            debug("Tried to delete %s in the DB, but it is a symbolic link." % temp_path)
            return

        # If the source path does not exist, 'throw' an error
        if not os.path.exists(temp_path):
            error("Tried to delete %s in the DB, but it doesn't exist." % temp_path)
            return

        # Construct the relative path
        rel_path = os.path.relpath(snap_path, snapshot)
                
        # Get the item's id from the database
        fid = self._get_item_id_by_name(item_name, parent)

        # If it is not in the database, throw a error, otherwise close it
        if fid == None:
            error("Path id of %s could not be found in the database" % rel_path)
            return

        version = self._get_current_version(fid)
                                               
        # If there is no open version, throw a error, otherwise close it
        if version == None:
            error("There is no version of %s in the database" % rel_path)
            return

        self._delete_version(version['id'])

    def add_new_items(self, snapshot, folder):

        self.add_new_item(snapshot, folder)

        # For all folders and files in the snaphot:
        for (path, folders, files) in os.walk(os.path.join(snapshot, folder)):
            parent = self._get_item_id_by_path(os.path.relpath(path, snapshot))

            # For each subfolder and file in the folder:
            for item_name in folders + files:
                self.add_new_item(path, item_name, parent)

        # Save all changes to the database
        self.commit()

    def add_new_item(self, path, item_name, parent=0):
        # The absolute path is the path of the folder + the name of the subfolder or file
        abs_path = os.path.join(path, item_name)
                
        # If the source path is a symbolic link, ignore it
        if os.path.islink(abs_path):
            debug("Tried to add \"%s\" to the DB, but it is a symbolic link." % abs_path)
            return

        # If the source path does not exist, 'throw' an error
        if not os.path.exists(abs_path):
            error("Tried to add path \"%s\" to the DB, but it doesn't exist on the disk." % abs_path)
            return

        # Check if the path is allready in the database or add it
        fid = self._find_or_add_item(item_name, parent)

        # If it didn't exist or it was removed earlier, add a new version
        if self._get_current_version(fid) == None:
            stat = os.stat(abs_path)
            if os.path.isdir(abs_path):
                self._add_version(fid, stat.st_mtime)
            else:
                self._add_version(fid, stat.st_mtime, stat.st_size, stat.st_ino)

    def propagate_changes(self, parent=None):
        if parent == None:
            parent = {'id': 0, 'time': 0}
        time = parent['time']
        created = 0
        size = 0
        for item in self._get_items(parent['id']):
            if item['inode'] == None:
                (t, c, s) = self.propagate_changes(item)
            else:
                t = item['time']
                c = item['created']
                s = item['size']
            time = max(time, t)
            created = max(created, c)
            size += s

        if parent['id'] > 0:
            if parent['created'] < created:
                self._delete_version(parent['vid'])
                self._add_version(parent['id'], time, size)
            else:
                self._update_version(parent['vid'], time, size)

        return (time, created, size)

    def add_new_repository_entries(self, repository):
        # Walk through all folders in the repository
        for (path, folders, fs_checksums) in os.walk(repository):
            # For each folder walk through all files (checksums)
            if len(fs_checksums) > 0:

                # We do this in batches, so get the first two characters of the checksums in the current folder (= folder name)
                batch = os.path.basename(path)

                # Get all known checksums in this batch from the databse
                db_checksums = self._get_checksum_subset(batch+'%')

                # Get the set difference to find out wich checksum files are on the disk but not in the database
                new_checksums = set(fs_checksums) - set(db_checksums)
                
                # Add all new checksums acompanied with their inode
                for checksum in new_checksums:
                    stat = os.stat(os.path.join(path, checksum))
                    self._add_checksum(checksum, stat.st_ino)

        # Save all changes to the database
        self.commit()

    def update_inodes(self, snapshot):

        # For each unlinked version, link it
        for record in self._get_unlinked_files():
            vid = record['vid']
            rel_path = self._get_path_by_item_id(record['fid'])
            
            # Construct the absolute path
            abs_path = os.path.join(snapshot, rel_path)
                
            # If the source path is a symbolic link, ignore it
            if os.path.islink(abs_path):
                debug("Skipping inode update for %s, it is a symbolic link." % rel_path)
                continue

            #If the path doesn't exist, throw an error
            if not os.path.exists(abs_path):
                error("Path %s could not be found" % rel_path)
                continue

            # Get some folder/file statistics
            stat = os.stat(abs_path)

            # Set the inode
            self._set_inode(vid, stat.st_ino)

        # Save all changes to the database
        self.commit()

    def update_history(self):
        warning("DB: update_history() is not implemented. This could be used to show if a file is moved, copied, deleted, etc in the GUI.")

# Iterations

    def _add_iteration(self):
        debug("DB: Adding iteration")
        query = 'INSERT INTO iterations (start) VALUES (?);'
        result = self.execute(query, mktime(datetime.now().timetuple()))
        return result.lastrowid

    def _finish_iteration(self):
        debug("DB: Finishing iteration")
        query = 'UPDATE iterations SET finished = ? WHERE id = ?;'
        result = self.execute(query, mktime(datetime.now().timetuple()), self.iteration)
        return result.lastrowid

# Items

    def _find_or_add_item(self, name, parent=0):
        fid = self._get_item_id_by_name(name, parent)
        if fid == None:
            fid = self._add_item(name, parent);
        return fid

    def _add_item(self, name, parent=0):
        debug("DB: Adding item '%s' under %d" % (name, parent))
        query = 'INSERT INTO items (parent, name) VALUES (?, ?);'
        return self.execute(query, parent, name.decode('utf-8')).lastrowid

    def _get_item_id_by_path(self, path, parent=0):
        if not isinstance(path, list):
            path = path.split(os.path.sep)
        if len(path) == 0 or path == ['.']:
            return parent
        fid = self._get_item_id_by_name(path.pop(0), parent)
        if fid != None:
            return self._get_item_id_by_path(path, fid)
        return None

    def _get_item_id_by_name(self, name, parent=0):
        query = 'SELECT id FROM items WHERE parent = ? AND name = ?;'
        record = self.execute(query, parent, name.decode('utf-8')).fetchone()
        if record != None:
            return record['id']
        return None

    def _get_path_by_item_id(self, fid):
        if fid == 0:
            return ''
        query = 'SELECT name, parent FROM items WHERE id = ? ;'
        record = self.execute(query, fid).fetchone()
        if record == None:
            error("Item %d not found in the database." % fid)
            return None
        path = self._get_path_by_item_id(record['parent']) 
        if path == None:
            return None
        return os.path.join(path, record['name'].encode('utf-8'))

    # The folder might contain files of size 0
    def _get_empty_folder_ids(self):
        query = ' \
            SELECT items.id as fid, versions.id as vid \
            FROM items \
            JOIN versions ON (versions.item = items.id) \
            WHERE size = 0 \
            AND inode IS NULL \
            AND deleted IS NULL;';
        return self.execute(query)

    def _get_items(self, parent):
        query = ' \
            SELECT items.id as id, versions.id as vid, inode, size, time, created \
            FROM items \
            JOIN versions ON (versions.item = items.id AND versions.deleted IS NULL) \
            WHERE items.parent = ? ;';
        result = self.execute(query, parent)
        if result == None:
            return []
        return result

# Versions

    def _add_version(self, fid, time=0, size=None, inode=None):
        debug("DB: Adding version (item=%d)" % fid)
        query = 'INSERT INTO versions (item, inode, time, size, created) VALUES (?, ?, ?, ?, ?);'
        result = self.execute(query, fid, inode, time, size, self.iteration)
        vid = result.lastrowid
        return vid

    def _get_version(self, vid):
        query = 'SELECT * FROM versions WHERE id = ?;'
        return self.execute(query, vid).fetchone()

    def _get_current_version(self, fid):
        query = 'SELECT * FROM versions WHERE item = ? AND deleted IS NULL;'
        return self.execute(query, fid).fetchone()

    def _get_parent_version(self, vid):
        query = ' \
            SELECT p.* \
            FROM versions \
            JOIN items ON (items.id = versions.item) \
            JOIN versions AS p ON (p.item = items.parent AND p.deleted IS NULL) \
            WHERE versions.id = ?;'
        return self.execute(query, vid).fetchone()

    def _delete_version(self, vid):
        debug("DB: Closing version (id=%d)" % vid)
        query = 'UPDATE versions SET deleted = ? WHERE id = ? ;'
        self.execute(query, self.iteration, vid)
        version = self._get_version(vid)

    def _update_version(self, vid, time, size):
        query = 'UPDATE versions SET size = ?, time = ? WHERE id = ? ;'
        self.execute(query, size, time, vid)

    def _set_inode(self, vid, inode):
        debug("DB: Set inode (version=%d, inode=%d)" % (vid, inode))
        query = 'UPDATE versions SET inode = ? WHERE id = ?;'
        self.execute(query, inode, vid)

# Repository

    def _add_checksum(self, checksum, inode):
        debug("DB: Adding checksum (inode=%d, checksum=%s)" % (inode, checksum))
        query = 'INSERT INTO repository (inode, checksum) VALUES (?, ?);'
        self.execute(query, inode, checksum)

    def _get_checksum_subset(self, pattern):
        query = 'SELECT checksum FROM repository WHERE checksum LIKE ? ;'
        return [record['checksum'] for record in self.execute(query, pattern).fetchall()]

    def _get_inodes_in_repository(self):
        query = 'SELECT inode FROM repository;'
        return self.execute(query)

    def _get_unlinked_files(self):
        query = ' \
            SELECT items.id as fid, versions.id as vid \
            FROM items \
            INNER JOIN versions ON (versions.item = items.id) \
            LEFT JOIN repository ON (repository.inode = versions.inode) \
            WHERE NOT versions.inode IS NULL \
    		AND repository.inode IS NULL;'
        return self.execute(query)

