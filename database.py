#!/usr/bin/env python

import os
from verbose import *
import sqlite3 as sql

class Database(object):

    path = None
    db = None

    def __init__(self, db_path):
        self.path = os.path.abspath(db_path)

    def connect(self, auto_create=True):
        debug("Connecting to database %s" % self.path)
        if not os.path.isfile(self.path) and auto_create:
            self.create()
        else:
            self.db = sql.connect(self.path)

    def close(self):
        debug("Closing connection to database %s" % self.path)
        self.commit()
        self.db.close()

    def create(self, commit=True):
        debug("Creating empty database %s" % os.path.basename(self.path))
        self.db = sql.connect(self.path)
        self.execute(' \
            CREATE TABLE paths ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                path TEXT NOT NULL \
            );')
        self.execute(' \
            CREATE TABLE versions ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                path INTEGER NOT NULL, \
                inode INTEGER NOT NULL, \
                previous_version INTEGER NULL, \
                created INTEGER NOT NULL, \
                deleted INTEGER NULL \
            );')
        self.execute(' \
            CREATE TABLE files ( \
                id INTEGER PRIMARY KEY NOT NULL, \
                hash TEXT NOT NULL \
            );')

    def execute(self, query, *args):
        cursor = self.db.cursor()
        cursor.execute(query, args)
        return cursor

    def commit(self, commit=True):
        if commit:
            self.db.commit()

    def add_new_files(self, root, folder):
        for (path, folders, files) in os.walk(os.path.join(root, folder)):
            for file_name in files:
                file_path = os.path.join(path, file_name)
                if not os.path.isfile(file_path):
                    continue
                file_stat = os.stat(file_path)
                if file_stat.st_nlink > 1:
                    continue
                file_path = os.path.relpath(file_path, root)
                pid = self._get_path_id(file_path)
                if pid == None:
                    pid = self._add_path(file_path)
                self._add_version(pid, file_stat)
 
    def delete_old_files(self, snapshot, temp, folder):
        for (path, folders, files) in os.walk(os.path.join(temp, folder)):
            for file_name in files:
                temp_path = os.path.join(path, file_name)
                snap_path = os.path.join(snapshot, os.path.relpath(temp_path, temp))
                if not os.path.isfile(temp_path):
                    continue
                inode = os.stat(temp_path).st_ino
                if os.path.isfile(snap_path):
                    mtime = os.stat(snap_path).st_mtime
                else:
                    mtime = 0 # TODO: NOW()
                pid = self._get_path_id(os.path.relpath(snap_path, snapshot))
                self._close_version(pid, inode, mtime)
    
    def add_new_repository_entries(self, repository):
        warning("DB: add_new_repository_entries %s" % repository)

    def link_files_to_repository(self, root, folder):
        warning("DB: link_files_to_repository %s" % folder)

    def _get_path_id(self, file_path):
        query = ' \
            SELECT id \
            FROM paths \
            WHERE path = ?;'
        row = self.execute(query, file_path).fetchone()
        if row != None:
            return row[0]
        return None

    def _add_path(self, file_path):
        notice("DB: Adding path %s" % file_path)
        query = ' \
            INSERT INTO paths \
            (path) VALUES (?);'
        result = self.execute(query, file_path)
        return result.lastrowid

    def _add_version(self, path_id, stat):
        notice("DB: Adding version (path=%d, inode=%d, created=%d)" % (path_id, stat.st_ino, stat.st_mtime))
        query = ' \
            INSERT INTO versions \
            (path, inode, created) VALUES (?, ?, ?);'
        result = self.execute(query, path_id, stat.st_ino, stat.st_mtime)
        return result.lastrowid

    def _close_version(self, path_id, inode, mtime):
        notice("DB: Closing version (path=%d, inode=%d, deleted=%d)" % (path_id, inode, mtime))
        query = ' \
            UPDATE versions \
            SET deleted = ? \
            WHERE path = ? \
            AND inode = ? \
            AND deleted IS NULL;'
        result = self.execute(query, mtime, path_id, inode)
  
