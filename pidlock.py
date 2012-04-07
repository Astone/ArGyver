#!/usr/bin/python
import os
import json
import hashlib

class PidLock(object):
    lockfilepath = '/tmp'
    lockfilename = None

    def __init__(self, *args, **kwargs):
        md5 = hashlib.md5()
        md5.update(json.dumps(kwargs))
        self.lockfilename = md5.hexdigest() + '.lock'

    def lockfile(self):
        return os.path.join(self.lockfilepath, self.lockfilename)
        
    def lock(self):
        if self.locked():
            return False
        else:
            lock = open(self.lockfile(), 'w')
            lock.write(str(os.getpid()))
            lock.close()
            return True

    def unlock(self):
        if os.path.isfile(self.lockfile()):
            os.unlink(self.lockfile())
            return True
        else:
            return False

    def locked(self):
        pid = self.pid()
        if pid == 0: # Not locked!
            return False
        else: # There is a lock file
            try: # Is the process still running?
                os.kill(pid, 0)
            except OSError: # No: Unlock.
                self.unlock()
                return False
            else: # Yes: It is locked!
                return True

    def pid(self):
        pid = 0
        if os.path.isfile(self.lockfile()):
            lock = open(self.lockfile(), 'r')
            pid = int(lock.read())
            lock.close()
        return pid


if __name__ == '__main__':
    import time

    p = PidLock(foo=1, bar=2, test='abc')

    if p.locked():
        print "Locked!"

    else:
        print "Locking..."
        p.lock()
        for i in range(10):
            print "Doing something... %d%%" % ((i+1) * 10)
            time.sleep(1)
        p.unlock()

