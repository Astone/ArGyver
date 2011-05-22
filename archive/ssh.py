import paramiko
from verbose import *

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
        try:
            self.sftp.listdir_attr(path)
        except Exception as e:
            if e.errno == 2:
                return False
            else:
                fatal(e)
        else:
            return True 
    