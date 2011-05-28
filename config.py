from verbose import *
from argparse import ArgumentParser
from ConfigParser import SafeConfigParser
from subprocess import check_output, CalledProcessError

class Config(object):
    
    argparser = None
    config_file = None
    confparser = None

    defaults = {
        'archive_snapshot'  : False,
        'rsync_options'     : '-rlpEtgoHDyv',
        'root'              : '.',
        'snapshot'          : 'snapshot/',
        'archive'           : 'archive/',
        'tmp'               : '.tmp/',
    }

    args = {}    
    vars = {}

    def __init__(self):
        self.parse_arguments()
        set_log_file(self.args.log_file, self.args.log_level)
        set_verbosity(self.args.verbosity)
        self.load_config_file(self.args.config_file)
        
    def parse_arguments(self):
        self.argparser = ArgumentParser(description='Create a snapshot and archive of your files.')

        self.argparser.add_argument(
            '-c', dest='config_file', required=True,
            help='Specify a valid config file')

        self.argparser.add_argument(
            '-l', dest='log_file',
            help='Log all actions to a log file')

        self.argparser.add_argument(
            '-ll', dest='log_level', type=int, choices=range(0, 6), default=5,
            help='The verbosity level for the log file. 0=quiet, 1=fatal errors, 2=errors, 3=warnings, 4=notices, 5=debug')

        self.argparser.add_argument(
            '-v', dest='verbosity', type=int, choices=range(0, 6), default=4,
            help='The verbosity level. 0=quiet, 1=fatal errors, 2=errors, 3=warnings, 4=notices, 5=debug')

        self.args = self.argparser.parse_args()
        
    def load_config_file(self, config_file):
        config_file = str(config_file)
        notice("Loading config file \"%s\"" % config_file, False)
        if os.path.exists(config_file):
            self.config_file = config_file
            notice("OK")
        else:
            fatal("FAILED")

        notice("Parsing config file \"%s\"" % self.config_file, False)
        try:
            self.confparser = SafeConfigParser(defaults=self.defaults, allow_no_value=True)
            self.confparser.read(self.config_file)
        except Exception as e:
            error("FAILED")
            fatal(str(e))
        else:
            notice("OK")
        self.config_check()
        
    def config_check(self):
        notice('Starting configuration check.')
        self.get_archive_snapshot()
        self.get_rsync_options()
        self.get_server_root()
        self.get_server_snapshot()
        self.get_server_archive()
        self.get_server_tmp()
        self.get_sources()
        notice('Configuration check completed.')

    def get_archive_snapshot(self):
        if not 'archive_snapshot' in self.vars:
            archive_snapshot = self.get_option('options', 'archive_snapshot')
            if not archive_snapshot in ['true', 'false']:
                fatal('options.archive_snapshot should be "true" or "false".')
            self.vars['archive_snapshot'] = {'true': True, 'false': False}[archive_snapshot]
        return self.vars['archive_snapshot']

    def get_rsync_options(self):
        if not 'rsync_options' in self.vars:
            rsync_options = self.get_option('options', 'rsync_options')
            self.vars['rsync_options'] = rsync_options
        return self.vars['rsync_options']

    def get_server_root(self, auto_fix = True):
        if not 'server_root' in self.vars:
            root = os.path.abspath(self.get_option('server', 'root'))
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
            self.vars['server_snapshot'] = self.get_server_folder(self.get_option('server', 'snapshot'))
        return self.vars['server_snapshot']

    def get_server_archive(self, auto_fix = True):
        if not 'server_archive' in self.vars:
            self.vars['server_archive'] = self.get_server_folder(self.get_option('server', 'archive'))
        return self.vars['server_archive']

    def get_server_tmp(self, auto_fix = True):
        if not 'server_tmp' in self.vars:
            self.vars['server_tmp'] = self.get_server_folder(self.get_option('server', 'tmp'))
        return self.vars['server_tmp']
    
    def get_sources(self):
        if not 'sources' in self.vars:
            self.vars['sources'] = {}
            for s in self.confparser.options('sources'):
                if s[:4] == 'src-':
                    path = self.get_option('sources', s)
                    if not self.is_client_folder(path):
                        error("The client source folder \"%s\" does not exist or is not readable." % path)
                    else:
                        folder = s[4:]
                        self.get_server_folder(folder, self.get_server_snapshot())
                        self.vars['sources'][folder] = path
            if len(self.vars['sources']) == 0:
                fatal("There are no client source folders defined. Use src-data, src-pictures etc.")
        return self.vars['sources']
        
    def get_option(self, section, option, type=str):
        debug("Get config option %s.%s as %s" % (section, option, str(type)), False)
        try:
            if type == str:
                value = self.confparser.get(section, option)
            if type == int:
                value = self.confparser.getint(section, option)
            if type == float:
                value = self.confparser.getfloat(section, option)
            if type == bool:
                value = self.confparser.getboolean(section, option)
        except Exception as e:
            error("FAILED")
            fatal(str(e))
        else:
            if value == '':
                value = None
            if option == 'password' and not value == None:
                debug('***')
            else:
                debug(value)
            return value

    def get_server_folder(self, folder, root = None, auto_fix = True):
        if root == None:
            root = self.get_server_root(auto_fix)
        path = os.path.join(root, folder)
        if not os.path.exists(path):
            debug("The folder \"%s\" does not exist." % folder)
            if auto_fix:
                try:
                    os.makedirs(path, 0755)
                except Exception as e:
                    fatal(str(e))
                else:
                    notice("Folder \"%s\" created on server." % folder)
            else:
                fatal()
        return path


    def is_client_folder(self, path):
        try:
            check_output(['rsync', path])
        except CalledProcessError as e:
            if e.returncode == 23:
                return False
            else:
                fatal(str(e))
        else:
            return True

    def __str__(self):
        return str(self.config_file)