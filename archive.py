#!/usr/bin/python
from modules import *

cnf = config.Config()

idx = index.Index(cnf)
idx.update()

s = sync.Sync(cnf, idx)
s.update()