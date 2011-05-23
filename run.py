#!/usr/bin/python
from archive import *

cnf = config.Config()

idx = index.Index(cnf)
idx.rebuild()
#idx.update()

#print idx.index