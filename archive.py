#!/usr/bin/python
from modules import *

cnf = config.Config()

idx = index.Index(cnf)
#idx.rebuild()
idx.update()

#print idx.index
