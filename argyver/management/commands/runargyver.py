from django.core.management.base import BaseCommand, CommandError
from argyver.models import Location, Node, Data, Version
from django.utils.translation import ugettext as _
from django.conf import settings
from datetime import datetime
from threading import Thread, Lock
from time import sleep
import subprocess
import signal
import os

"""
Some background information on rsync output:
YXcstpoguax  path/to/file
|||||||||||
`----------- the type of update being done::
 ||||||||||   <: file is being transferred to the remote host (sent).
 ||||||||||   >: file is being transferred to the local host (received).
 ||||||||||   c: local change/creation for the item, such as:
 ||||||||||      - the creation of a directory
 ||||||||||      - the changing of a symlink,
 ||||||||||      - etc.
 ||||||||||   h: the item is a hard link to another item (requires --hard-links).
 ||||||||||   .: the item is not being updated (though it might have attributes that are being modified).
 ||||||||||   *: means that the rest of the itemized-output area contains a message (e.g. "deleting").
 ||||||||||
 `---------- the file type:
  |||||||||   f for a file,
  |||||||||   d for a directory,
  |||||||||   L for a symlink,
  |||||||||   D for a device,
  |||||||||   S for a special file (e.g. named sockets and fifos).
  |||||||||
  `--------- c: different checksum (for regular files)
   ||||||||     changed value (for symlink, device, and special file)
   `-------- s: Size is different.
    `------- t: Modification time is different.
     `------ p: Permission are different.
      `----- o: Owner is different.
       `---- g: Group is different.
        `--- u: The u slot is reserved for future use.
         `-- a: The ACL information changed.
          `- x: The extended attribute information changed.
"""


class Command(BaseCommand):
    args = '<location location ...>'
    help = 'Runs the ArGyver for specified locations'

    def handle(self, *args, **options):
        location_list = []
        for slug in args:
            try:
                location_list.append(Location.objects.get(slug=slug))
            except Location.DoesNotExist:
                raise CommandError('Location "%s" does not exist' % slug)

        for location in location_list:
            self._archive(location)

    def _archive(self, location):
        global mutex

        started = datetime.now()
        self.stdout.write(_('Archiving "%(location)s" at %(timestamp)s') % {'location': location.name, 'timestamp' :started})
        self.stdout.write(_('Remote path: %s') % location.url)
        self.stdout.write(_('Local path: %s') % location.root_node.abs_path())

        mutex = Lock()
        thread = RsyncThread(location, mutex)
        thread.start()

        try:
            while thread.isAlive() or thread.buffer:
                if thread.buffer:
                    mutex.acquire()
                    line = thread.buffer.pop(0)
                    mutex.release()
                    self._process_output(line, location)
        except BaseException as exception:
            thread.process.kill()
            mutex.acquire()
            thread.buffer = []
            mutex.release()
            self.stderr.write("%s: %s" % (type(exception).__name__, str(exception)))

    def _process_output(self, line, location):
        action = line[0]
        node_type = line[1]
        path = os.path.join(location.root_node.path, line[12:])

        # check file type
        if node_type not in ['f', 'd']:
            self.stderr.write(_('Unkownn RSYNC file type received: %s') % line)

        # Deleting
        elif action == '*':
            if not line.startswith('*deleting'):
                self.stderr.write(_('Unkownn RSYNC status received: %s') % line)
                return
            self._delete_node(path)

        else:
            self._add_or_update_node(path)

    def _add_or_update_node(self, path):
        n = Node.get_or_create_from_path(path)

    def _delete_node(self, path):
        try:
            node = Node.get_from_path(path)
        except Node.DoesNotExist:
            self.stderr.write(_("%s was removed by RSYNC, but it doesn't exist in the database!") % path)
            return
        version = node.get_latest_version()

class RsyncThread(Thread):

    MAX_BUFFER = 1000 # lines of output

    def __init__(self, location, mutex):
        self.location = location
        self.mutex = mutex
        self.process = None
        self.buffer = []
        self.error = []
        super(RsyncThread, self).__init__()

    def run(self):
        command = self._get_rsync_cmd()
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        while self.process.poll() is None:
            output = self.process.stdout.readline().strip()
            if output:
                self.mutex.acquire()
                self.buffer.append(output.strip())
                self.mutex.release()
            if len(self.buffer) >= self.MAX_BUFFER:
                self.process.send_signal(signal.SIGSTOP)
                while len(self.buffer) > self.MAX_BUFFER / 2:
                    sleep(1)
                self.process.send_signal(signal.SIGCONT)

        remaining_output = [output.strip() for output in self.process.stdout.read().split('\n') if output]
        for output in remaining_output:
            self.mutex.acquire()
            self.buffer.append(output.strip())
            self.mutex.release()

        self.error = self.process.stderr.read()

    def _get_rsync_cmd(self):
        rsync = settings.AGV_RSYNC_BIN
        rsync += ' -aAHX --out-format=\'%i %n\' --outbuf=l --delete '
        if self.location.remote_port != 22:
            rsync += '-e \'ssh -p %d\'' % self.location.remote_port
        rsync += self.location.url + ' ' + self.location.root_node.abs_path()
        return rsync
