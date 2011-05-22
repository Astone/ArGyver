import os
from datetime import datetime

DEBUG   = 1
NOTICE  = 2
WARNING = 4
ERROR   = 8
FATAL   = 16

SCREEN_LEVEL = DEBUG | NOTICE | WARNING | ERROR | FATAL
LOG_LEVEL    = DEBUG | NOTICE | WARNING | ERROR | FATAL

VERBOSE_TEXT = ""
VERBOSE_LOG_FILE = open("/tmp/archive.log", 'w')
VERBOSE_TIME = datetime.now()
 
def debug(msg, show=True):
    verbose(DEBUG, msg, 'magenta', show)

def notice(msg, show=True):
    verbose(NOTICE, msg, 'blue', show)

def warning(msg, show=True):
    verbose(WARNING, msg, 'yellow', show)

def error(msg, show=True):
    verbose(ERROR, msg, 'red', show)

def fatal(msg = 'exit'):
    verbose(FATAL, msg, 'red', True)
    exit()

def verbose(type, msg, color, show = True):
    global VERBOSE_TEXT

    types = {
        DEBUG: 'Debug',
        NOTICE: 'Notice',
        WARNING: 'Warning',
        ERROR: 'Error',
        FATAL: 'FATAL ERROR'}
    
    VERBOSE_TEXT += colorize(msg, color)
    if show:
        if SCREEN_LEVEL & type:
            print colorize(types[type]+':', color), VERBOSE_TEXT
        VERBOSE_TEXT = ""
    else:
        VERBOSE_TEXT += " ... "
    
    if LOG_LEVEL & type:
        duration = datetime.now() - VERBOSE_TIME 
        log = "%0.3f %s | %s: %s" % (duration.total_seconds(), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), types[type], msg) 
        if not show:
            log += " ..."
        VERBOSE_LOG_FILE.write(log + "\n")

def colorize(text, color = 'white', bright=True):
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