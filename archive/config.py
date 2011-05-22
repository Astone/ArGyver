from verbose import *
from ssh import SshClient
from ConfigParser import SafeConfigParser
from stat import *
import pickle
import os

class Config():
    
    config_file = None
    parser = None

    defaults = {
        'hasher'   : 'client',
        'snapshot' : 'snapshot/',
        'archive'  : 'archive/',
        'index'    : 'index.pkl',
        'hostname' : 'localhost',
        'port'     : '22',
        'username' : None,
        'password' : None,
    }
    
    vars = {}

    def __init__(self, config_file):
        self.set_file(config_file)
        self.load()
    
    def set_file(self, config_file):
        notice("Loading config file \"%s\"" % config_file, False)
        if os.path.exists(config_file):
            self.config_file = config_file
            notice("OK")
        else:
            fatal("FAILED")

    def load(self):
        notice("Parsing config file \"%s\"" % self.config_file, False)
        try:
            self.parser = SafeConfigParser(defaults=self.defaults, allow_no_value=True)
            self.parser.read(self.config_file)
        except Exception as e:
            error("FAILED")
            fatal(str(e))
        else:
            notice("OK")
        self.config_check()
        
    def config_check(self):
        notice('Configuration check')
        self.get_hasher()
        self.get_server_root()
        self.get_server_snapshot()
        self.get_server_archive()
        self.get_server_index_file()
        self.get_client_ssh()
        self.get_client_root()
        self.get_client_src_list()
        notice('Configuration check completed!')
            

    def get_hasher(self):
        if not 'hasher' in self.vars:
            hasher = self.get('options', 'hasher')
            if not hasher in ['client', 'server']:
                fatal('options.hasher should be "client" or "server".')
            self.vars['hasher'] = hasher
        return self.vars['hasher']

    def get_server_root(self, auto_fix = True):
        if not 'server_root' in self.vars:
            root = os.path.abspath(self.get('server', 'root'))
            if not os.path.exists(root):
                debug("The server's root dir \"%s\" does not exist." % root)
                if auto_fix:
                    try:
                        os.makedirs(root, 0755)
                    except Exception as e:
                        fatal(str(e))
                    else:
                        notice("Root dir created on server: %s" % root)
                else:
                    fatal()
            self.vars['server_root'] = root
        return self.vars['server_root']

    def get_server_snapshot(self, auto_fix = True):
        if not 'server_snapshot' in self.vars:
            root = self.get_server_root(auto_fix)
            snapshot = os.path.join(root, self.get('server', 'snapshot'))
            if not os.path.exists(snapshot):
                debug("The snapshot dir \"%s\" does not exist." % snapshot)
                if auto_fix:
                    try:
                        os.makedirs(snapshot, 0755)
                    except Exception as e:
                        fatal(str(e))
                    else:
                        notice("Snapshot dir created on server: %s" % snapshot)
                else:
                    fatal()
            self.vars['server_snapshot'] = snapshot
        return self.vars['server_snapshot']

    def get_server_archive(self, auto_fix = True):
        if not 'server_archive' in self.vars:
            root = self.get_server_root(auto_fix)
            archive = os.path.join(root, self.get('server', 'archive'))
            if not os.path.exists(archive):
                debug("The archive dir \"%s\" does not exist." % archive)
                if auto_fix:
                    try:
                        os.makedirs(archive, 0755)
                    except Exception as e:
                        fatal(str(e))
                    else:
                        notice("Archive dir created on server: %s" % archive)
                else:
                    fatal()
            self.vars['server_archive'] = archive
        return self.vars['server_archive']

    def get_server_index(self, auto_fix = True):
        if not 'server_index' in self.vars:
            index = self.get_server_index_file(auto_fix)
            notice("Loading index file \"%s\"" % index)
            try:
                index = pickle.load(open(index, 'w'))
            except Exception as e:
                fatal(str(e))
            else:
                notice("OK")
            self.vars['server_index'] = index
        return self.vars['server_index']

    def get_server_index_file(self, auto_fix = True):
        if not 'server_index_file' in self.vars:
            root = self.get_server_root(auto_fix)
            index = os.path.join(root, self.get('server', 'index'))
            if not os.path.exists(index):
                debug("The index file \"%s\" does not exist." % index)
                if auto_fix:
                    try:
                        pickle.dump({}, open(index, 'w'))
                    except Exception as e:
                        fatal(str(e))
                    else:
                        notice("Index file created on server: %s" % index)
                else:
                    fatal()
            self.vars['server_index_file'] = index
        return self.vars['server_index_file']
    
    def get_client_ssh(self, auto_fix=True):
        if not 'client_ssh' in self.vars:
            hostname = self.get('client', 'hostname')
            username = self.get('client', 'username')
            password = self.get('client', 'password')
            port = self.getint('client', 'port')
            self.vars['client_ssh'] = SshClient(hostname, username, password, port, auto_fix)
        return self.vars['client_ssh']

    def get_client_root(self):
        if not 'client_root' in self.vars:
            root = self.get('client', 'root')
            ssh = self.get_client_ssh()
            if not ssh.is_folder(root):
                fatal("The client root \"%s\" does not exist." % root)
            self.vars['client_root'] = root
        return self.vars['client_root']

    def get_client_src_list(self):
        ssh = self.get_client_ssh()
        root = self.get_client_root()
        if not 'client_src_list' in self.vars:
            src = {}
            for s in self.parser.options('client'):
                if s[:4] == 'src-':
                    path = os.path.join(root, self.get('client', s))
                    if not ssh.is_folder(path):
                        error("The client source folder \"%s\" does not exist." % path)
                    else:
                        src[s[4:]] = path
            if len(src) == 0:
                fatal("There are no client source folders defined. Use src-data, src-pictures etc.")
            self.vars['client_src_list'] = src
        return self.vars['client_src_list']
        
    def get(self, section, option):
        debug("Get config option %s.%s" % (section, option), False)
        try:
            value = self.parser.get(section, option)
        except Exception as e:
            error("FAILED")
            fatal(str(e))
        else:
            if value == '':
                value = None
            debug(value)
            return value

    def getint(self, section, option):
        debug("Get config option %s.%s as integer" % (section, option), False)
        try:
            value = self.parser.getint(section, option)
        except Exception as e:
            error("FAILED")
            fatal(str(e))
        else:
            debug(value)
            return value

    def __str__(self):
        return str(self.config_file)
