#!/usr/bin/env python

import os
from verbose import *
from datetime import datetime
from time import mktime
import sqlite3 as sql

class Database(object):

    itteration = None
    path = None
    db = None

    def __init__(self, db_path, auto_create=True):
        self.path = os.path.abspath(db_path)
        if not os.path.isfile(self.path) and auto_create:
            self.create(True)
        else:
            self.connect()
        self.itteration = self._get_itteration() + 1
        debug("DB: Iteration #%d" % self.itteration)
        self.close()

    def connect(self):
        debug("DB: Connecting to database %s" % self.path)
        self.db = sql.connect(self.path)

    def close(self):
        debug("DB: Closing connection to database %s" % self.path)
        self.commit()
        self.db.close()

    def create(self, commit=True):
        debug("DB: Creating empty database %s" % os.path.basename(self.path))
        self.db = sql.connect(self.path)
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
                created REAL NOT NULL, \
                deleted REAL NULL, \
                created_i INTEGER NOT NULL, \
                deleted_i INTEGER NULL \
            );')
        self.execute(' \
            CREATE TABLE repository ( \
                id INTEGER PRIMARY KEY NOT NULL, \
                hash TEXT NOT NULL \
            );')

    def execute(self, query, *args):
        cursor = self.db.cursor()
        try:
            cursor.execute(query, args)
        except Exception as e:
            error(str(e))
        return cursor

    def commit(self, commit=True):
        if commit:
            debug("DB: Commit #%d." % self.itteration)
            self.db.commit()

    def add_new_paths(self, root, folder):
        for (path, folders, files) in os.walk(os.path.join(root, folder)):
            for name in folders+files:
                abs_path = os.path.join(path, name)
                if not os.path.exists(abs_path):
                    continue
                stat = os.stat(abs_path)
                if stat.st_nlink > 1 and self.itteration > 1:
                    continue
                rel_path = os.path.relpath(abs_path, root)
                pid = self._get_path_id(rel_path)
                if pid == None:
                    pid = self._add_path(rel_path)
                    if os.path.isdir(abs_path):
                        self._get_or_add_folder(rel_path)
                if os.path.isdir(abs_path) and not self._path_is_open(pid):
                    self._add_version(pid, stat.st_mtime)
                if os.path.isfile(abs_path):
                    self._add_version(pid, stat.st_mtime)
            self.commit()
 
    def delete_old_paths(self, snapshot, temp, folder):
        for (path, folders, files) in os.walk(os.path.join(temp, folder)):
            for file_name in folders+files:
                temp_path = os.path.join(path, file_name)
                snap_path = os.path.join(snapshot, os.path.relpath(temp_path, temp))
                if not os.path.exists(temp_path):
                    continue
                if not os.path.isdir(snap_path):
                    continue
                inode = os.stat(temp_path).st_i
                if os.path.exists(snap_path):
                    mtime = os.stat(snap_path).st_mtime
                else:
                    mtime = mktime(datetime.now().timetuple())
                pid = self._get_path_id(os.path.relpath(snap_path, snapshot))
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

    def link_files_to_repository(self, root, folder):
        for (path_id, rel_path) in self._get_orphan_paths(folder+'/%'):
            abs_path = os.path.join(root, rel_path.encode('utf-8'))
            if not os.path.exists(abs_path):
                warning("Path %s could not be found" % abs_path)
                continue
            inode = os.stat(abs_path).st_ino
            self._set_inode(path_id, inode)
        self.commit()

    def update_history(self):
        warning("DB: update_history() is not implemented. This could be used to show if a file is moved, copied, deleted, etc in the GUI.")

    def _get_itteration(self):
        query = ' \
            SELECT 0, MAX(created_i), MAX(deleted_i) \
            FROM versions;'
        row = self.execute(query).fetchone()
        return max(row)

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
        folder_id = self._get_or_add_folder(os.path.dirname(file_path))
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

    def _add_version(self, path_id, mtime):
        debug("DB: Adding version (path=%d, created=%f)" % (path_id, mtime))
        query = ' \
            INSERT INTO versions \
            (path, created, created_i) VALUES (?, ?, ?);'
        result = self.execute(query, path_id, mtime, self.itteration)
        return result.lastrowid

    def _close_version(self, path_id, inode, mtime):
        debug([path_id, inode, mtime])
        debug("DB: Closing version (path=%d, inode=%d, deleted=%f)" % (path_id, inode, mtime))
        query = ' \
            UPDATE versions \
            SET deleted = ?, deleted_i = ? \
            WHERE path = ? \
            AND inode = ? \
            AND deleted IS NULL;'
        self.execute(query, mtime, self.itteration, path_id, inode)

    def _get_hashes(self, pattern):
        query = ' \
            SELECT hash \
            FROM repository \
            WHERE hash LIKE ?;'
        return [row[0] for row in self.execute(query, pattern).fetchall()]

    def _add_hash(self, file_hash, inode):
        debug("DB: Adding hash (inode=%d, hash=%s)" % (inode, file_hash))
        query = ' \
            INSERT INTO repository \
            (id, hash) VALUES (?, ?);'
        self.execute(query, inode, file_hash)

    def _get_orphan_paths(self, pattern):
        query = ' \
            SELECT versions.path, paths.path \
            FROM paths \
            JOIN versions ON (versions.path = paths.id) \
            WHERE paths.path LIKE ? \
            AND inode IS NULL;'
        return self.execute(query, pattern).fetchall()

    def _set_inode(self, path_id, inode):
        debug("DB: Set inode (path=%d, inode=%d)" % (path_id, inode))
        query = ' \
            UPDATE versions \
            SET inode = ? \
            WHERE path = ? \
            AND inode IS NULL;'
        self.execute(query, inode, path_id)


