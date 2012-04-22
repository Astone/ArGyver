ArGyver 3.1
===========

ArGyver is backup utility based on rsync, it stores each version
of your files individually in a file based archive. It can
maintain archives for local and remote file systems for any
number of machines.

The web interface is a bit premature. It uses old fashion frames
and page reloads. You're welcome to implement a proper web
interface using AJAX etc :)

    usage: backup.py [-h] -c CONFIG_FILE [-l LOG_FILE]
           [-ll {0,1,2,3,4,5}] [-v {0,1,2,3,4,5}]

    arguments:
    -h, --help         show help message
    -c CONFIG_FILE     Specify a valid config file
    -l LOG_FILE        Log all actions to a log file
    -ll {0,1,2,3,4,5}  The verbosity level for the log file.
                       0=quiet, 1=fatal errors, 2=errors,
                       3=warnings, 4=notices, 5=debug
    -v {0,1,2,3,4,5}   The verbosity level.
                       0=quiet, 1=fatal errors, 2=errors,
                       3=warnings, 4=notices, 5=debug

Installation
------------

1.  Place ArGyver somewhere on the server side.

2.  Edit the config file config/argyver.conf.
    See 'Configuration' below.

3.  Make sure you have (ssh) access to all remote source locations.
    You might need to do some public/private key magic:

    http://lmgtfy.com/?q=ssh+key

4.  Find out if Argyver likes your config skills.
    Select the maximum verbosity level to see what you did wrong :)

        $ ./argyver.py -c argyver.conf -v5

5.  ArGyver should be scheduled as a cron job.
    To edit your systems cron jobs use: crontab -e

6.  Let's assume ArGyver is in Angus' home folder and you want
    to run ArGyverevery hour on the hour.
    Then add something like this to your crontab:

        0 * * * * /home/angus/ArGyver/argyver.py -c /home/angus/ArGyver/argyver.conf -l /home/angus/ArGyver/argyver.log -v 2

    I'd advise you to use absolute paths because it's not
    always clear from which root folder the crontab executes
    its commands.

Web Interface
-------------
You can use the web interface to browse and download all
versions of your files. To enable the webinterface you
need a webserver and php 5.

1.  Set the `repository` and `database` in config/argyver.conf.
    If you changed the location of your config file, you should
    alter the CONFIG_PATH variable in www/config.php.

2.  If your webserver can be reached from the World Wide Web,
    add a .htaccess and .htpasswd file in the www folder to
    prevent unauthorized people from browsing your files.

    http://lmgtfy.com/?q=.htaccess+.htpasswd

3. Create a symbolic link to the www folder in your webroot:

        $ ln -s /home/angus/ArGyver/www /var/www/argyver

4. Open your favourite browser and go to:

    http://localhost/argyver


Configuration
-------------

### options.rsync_options

You can specify your own rsync options. But I would recommend
you to leave this the default, which is `-rlpEtgoHDuyv`

this means `r`ecurse into directories, copy sym`l`inks as
symlinks, preserve `p`ermissions, `E`xecutability, modification
`t`imes, `g`roup, `o`wner, `H`ard links, `D`evice files and
special files, `u`pdate only. The `y` is for the 'fuzzy' mode,
which means that rsync finds a similar file for basis if no
destination file exists. The last one is `v`erbosity.

### server.root 
The root folder on the server, where the backups are created.
Default: `[the current working directory]`

### server.snapshot
The folder where the snapshot is created, relative to the server
root. Or an absolute path if you wish.
Default: `snapshot/`

### server.archive
The folder where the archive is created, relative to the server
root. Or an absolute path if you wish.
Default: `archive/`

### server.repository
The folder where all data is stored, relative to the server root.
Or an absolute path if you wish. This is used by the file linker
to save disk space. 
Default: `[disabled]`

### server.database
A database file where all version information data, relative to
the server root. Or an absolute path if you wish. This is used
by web interface.
Default: `[disabled]`

### server.tmp
A temporary folder used by rsync to store all files that are
changed. These files will be placed in the archive folder
after rsync has terminated. Again a relative path to the server
root. Or an absolute path if you wish.
Default: `.tmp/`

### sources
A list of source locations.

For example:

    src-photos: username@hostname:Pictures/MyPhotos/

The files in the client folder "Pictures/MyPhotos" (relative to
the clients home dir, start with a slash to use absolute paths)
will be stored in the snapshot and archive folder "photos".

Of course you can also use the script locally without ssh, e.g.:

    src-www: /var/www/

A trailing slash on the source avoids creating an additional
directory level at the destination. You can think of a trailing
slash on a source as meaning "copy the contents of this
directory" as opposed to "copy the directory by name".

Some more examples:

    src-documents: username@hostname:Documents/
    src-www: username@mydomain.com:/var/www/
    src-pics/private: username@ip-address:Pictures/
    src-pics/download: username@ip-address:Downloads/Images/
    src-pics: /home/angus/Pictures/helicopters

