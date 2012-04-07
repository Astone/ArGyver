#!/usr/bin/env python

import os
from verbose import *

class Database(object):

    file_name = None
    db = None
    
    def __init__(self, file_name=".data.sqlite"):
        self.file_name = os.path.abspath(file_name)

    def connect(self):
        warning("DB: connect")

    def close(self):
        warning("DB: close")

    def add_new_files(self, folder):
        warning("DB: add_new_files %s" % folder)

    def delete_old_files(self, folder):
        warning("DB: delete_old_files %s" % folder)
    
    def add_new_repository_entries(self, repository):
        warning("DB: add_new_repository_entries %s" % folder)

    def delete_old_files(self, folder):
        warning("DB: delete_old_files %s" % folder)

