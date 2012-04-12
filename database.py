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
                hash TEXT NOT NULL \
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
        self.execute('CREATE UNIQUE INDEX idx_repository_hash ON repository (hash);')

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

    def add_new_paths(self, root, folder):
        for (path, folders, files) in os.walk(os.path.join(root, folder)):
            for name in folders + files:
                abs_path = os.path.join(path, name)
                if not os.path.exists(abs_path):
                    continue
                stat = os.stat(abs_path)
                if stat.st_nlink > 1 and not os.path.isdir(abs_path) and self.iteration > 1:
                    continue
                rel_path = os.path.relpath(abs_path, root)
                if os.path.isdir(abs_path):
                    rel_path += os.path.sep
                pid = self._get_path_id(rel_path)
                if pid == None:
                    pid = self._add_path(rel_path)
                    if os.path.isdir(abs_path):
                        self._get_or_add_folder(rel_path.rstrip(os.path.sep))
                if os.path.isdir(abs_path) and not self._path_is_open(pid):
                    self._add_version(pid, stat.st_ino, stat.st_mtime)
                if os.path.isfile(abs_path):
                    self._add_version(pid, stat.st_ino, stat.st_mtime)
        self.commit()
 
    def delete_old_paths(self, snapshot, temp, folder):
        for (path, folders, files) in os.walk(os.path.join(temp, folder)):
            for file_name in folders + files:
                temp_path = os.path.join(path, file_name)
                snap_path = os.path.join(snapshot, os.path.relpath(temp_path, temp))
                if not os.path.exists(temp_path):
                    continue
                if os.path.isdir(snap_path):
                    continue
                inode = os.stat(temp_path).st_ino
                if os.path.exists(snap_path):
                    mtime = os.stat(snap_path).st_mtime
                else:
                    mtime = 0
                rel_path = os.path.relpath(snap_path, snapshot)
                if os.path.isdir(temp_path):
                    rel_path += os.path.sep
                pid = self._get_path_id(rel_path)
                if not pid == None:
                    self._close_version(pid, inode, mtime)
                else:
                    warning("Path id of %s could not be found in the database" % os.path.relpath(snap_path, snapshot))
        self.commit()
    
    def add_new_repository_entries(self, repository):
        for (path, folders, fs_hashes) in os.walk(repository):
            if len(fs_hashes) > 0:
                batch = os.path.basename(path)
                db_hashes = self._get_hashes(batch+'%')
                hashes = set(fs_hashes) - set(db_hashes)
                for h in hashes:
                    self._add_hash(h, os.stat(os.path.join(path, h)).st_ino)
        self.commit()

    def update_inodes(self, root, folder):
        for (version_id, rel_path) in self._get_unlinked_files(folder+'/%'):
            abs_path = os.path.join(root, rel_path.encode('utf-8'))
            if not os.path.exists(abs_path):
                warning("Path %s could not be found" % abs_path)
                continue
            inode = os.stat(abs_path).st_ino
            self._set_inode(version_id, inode)
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

    def _get_hashes(self, pattern):
        query = ' \
            SELECT hash \
            FROM repository \
            WHERE hash LIKE ? ;'
        return [row[0] for row in self.execute(query, pattern).fetchall()]

    def _add_hash(self, file_hash, inode):
        debug("DB: Adding hash (inode=%d, hash=%s)" % (inode, file_hash))
        query = ' \
            INSERT INTO repository \
            (id, hash) VALUES (?, ?);'
        self.execute(query, inode, file_hash)

    def _get_unlinked_files(self, pattern):
        query = ' \
            SELECT versions.id, paths.path \
            FROM paths \
            INNER JOIN versions ON (versions.path = paths.id) \
            LEFT JOIN repository ON (repository.id = versions.inode) \
    		WHERE hash IS NULL \
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


