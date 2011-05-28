import paramiko
from verbose import *
from binascii import a2b_hex

class SshClient(paramiko.SSHClient): 
    
    sftp = None
    
    def __init__(self, hostname = 'localhost', username=None, password=None, port=22, auto_fix=True):
        
        paramiko.SSHClient.__init__(self)

        if auto_fix:
            self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
        self.load_system_host_keys()

        notice("Connecting to \"%s\"" % hostname, False)
        try:
            self.connect(hostname, port, username, password)
        except Exception as e:
            fatal(str(e))
        else:
            notice('OK')
    
        notice("Opening SFTP connection", False)
        try:
            self.sftp = self.open_sftp()
        except Exception as e:
            fatal(str(e))
        else:
            notice('OK')
       
    def is_folder(self, path):
        debug("Is \"%s\" a readable folder on the client?" % path)
        if self.listdir(path) == None:
            debug("no")
            return False
        else:
            debug("yes")
            return True 
    
    def listdir(self, path):
        debug("List folder \"%s\" on the client" % path)
        try:
            items = self.sftp.listdir_attr(path)
        except Exception as e:
            if e.errno == 2:
                warning("Folder \"%s\" does not exist on the client" % path)
                return None
            elif e.errno == 13:
                warning("Folder \"%s\" (on the client) is not readable" % path)
                return None
            else:
                fatal(e)
        folder = {}
        for item in items:
            time = item.st_mtime
            if item.longname[0] == 'd':
                time = None
            folder[item.filename] = time

        return folder
        
    def tree(self, path):
        debug("Build tree for \"%s\" on the client" % path)
        tree = {}
        items = self.listdir(path)
        for (name, time) in items.iteritems():
            if time == None:
                tree[name] = self.tree(os.path.join(path, name))
            else:
                tree[name] = time
        return tree
        
    def md5(self, path):
        debug("Get md5 hash of \"%s\" on the client." % path)
        (stdin, stdout, stderr) = self.exec_command("md5sum %s" % path)
        err = stderr.read()
        if not err == "":
            fatal (err) 
        else:
            return a2b_hex(stdout.read().split()[0])

    def download(self, remote_path, local_path):
        debug("Downloading \"%s\" from the client to \"%s\"." % (remote_path, local_path))
        try:
            self.sftp.get(remote_path, local_path)
        except Exception as e:
            fatal(str(e))