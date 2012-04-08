import os
from datetime import datetime

DEBUG   = 1
NOTICE  = 2
WARNING = 4
ERROR   = 8
FATAL   = 16

SCREEN_LEVEL = FATAL | ERROR | WARNING | NOTICE
LOG_LEVEL    = FATAL | ERROR | WARNING | NOTICE | DEBUG

VERBOSE_TEXT = ""
VERBOSE_LOG_FILE = None
VERBOSE_TIME = datetime.now()

def set_log_file(log_file, v):
    global VERBOSE_LOG_FILE, LOG_LEVEL
    if log_file == None:
        return

    VERBOSE_LOG_FILE = open(log_file, 'w')
    (LOG_LEVEL, v) = get_verbosity(v)
    debug("Log level set to: %s" % v)

def set_verbosity(v):
    global SCREEN_LEVEL
    (SCREEN_LEVEL, v) = get_verbosity(v)
    debug("Verbosity level set to: %s" % v)

def get_verbosity(v = None):

    v_int = [
        0,
        FATAL,
        FATAL | ERROR,
        FATAL | ERROR | WARNING,
        FATAL | ERROR | WARNING | NOTICE,
        FATAL | ERROR | WARNING | NOTICE | DEBUG]

    v_str = ['quiet', 'fatal errors', 'errors', 'warnings', 'notices', 'debug']

    return (v_int[v], v_str[v])

def debug(msg, show=True):
    verbose(DEBUG, msg, 'cyan', show)

def notice(msg, show=True):
    verbose(NOTICE, msg, 'white', show)

def warning(msg, show=True):
    verbose(WARNING, msg, 'yellow', show)

def error(msg, show=True):
    verbose(ERROR, msg, 'red', show)

def fatal(msg = 'exit'):
    verbose(FATAL, msg, 'red', True, True)
    exit()

def verbose(type, msg, color, show=True, bright=False):
    global VERBOSE_TEXT

    types = {
        DEBUG: 'Debug',
        NOTICE: 'Notice',
        WARNING: 'Warning',
        ERROR: 'Error',
        FATAL: 'FATAL ERROR'}
    
    VERBOSE_TEXT += colorize(msg, color, bright)
    if show:
        if SCREEN_LEVEL & type:
            print colorize(types[type]+':', color, bright), VERBOSE_TEXT
        VERBOSE_TEXT = ""
    else:
        VERBOSE_TEXT += " ... "
    
    if VERBOSE_LOG_FILE != None and LOG_LEVEL & type:
        duration = datetime.now() - VERBOSE_TIME
        seconds = duration.days * 24 * 3600 + duration.secconds + duration.microseconds / 10**6 
        log = "%0.3f %s | %s: %s" % (seconds, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), types[type], msg) 
        if not show:
            log += " ..."
        VERBOSE_LOG_FILE.write(log + "\n")
        VERBOSE_LOG_FILE.flush()

def colorize(text, color = 'white', bright=False):
    c = {
        'black'     : 30,
        'red'       : 31,
        'green'     : 32,
        'yellow'    : 33,
        'blue'      : 34,
        'magenta'   : 35,
        'cyan'      : 36,
        'white'     : 37}

    if not color in c:
        color = 'white'
        
    return "\033[%d;%dm%s\033[0m" % (bright, c[color], text)
