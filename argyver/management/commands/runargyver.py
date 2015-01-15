from django.core.management.base import BaseCommand, CommandError
from argyver.models import Iteration, Archive, Node, Data, Version, ArGyverException
from django.utils.translation import ugettext as _
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from threading import Thread, Lock
from time import sleep
from hashlib import md5
import subprocess
import signal
import os
import re


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
    args = '<archive archive ...>'
    help = 'Runs the ArGyver for specified archives'

    BUFFER_SIZE = 4 * (2 ** 20)  # 4MB
    valid_line = re.compile(r'^[<>ch.*][fdLDS][.+c][.+s][.+t][.+p][.+o][.+g][.+u][.+a][.+x] ')

    def handle(self, *args, **options):
        archive_list = []
        for slug in args:
            try:
                archive_list.append(Archive.objects.get(slug=slug))
            except Archive.DoesNotExist:
                raise CommandError('Archive "%s" does not exist' % slug)

        started = timezone.now()

        self.iteration = Iteration(started=timezone.now(), errors="")
        self.iteration.save()
        for archive in archive_list:
            self._archive(archive)

        self.iteration.finished = timezone.now()
        if not self.iteration.errors:
            self.iteration.errors = None
        self.iteration.save()

        self.stdout.write(_('Finished in %d seconds') % (timezone.now() - started).total_seconds())

    def _archive(self, archive):
        global mutex
        self.stdout.write(_('Archiving "%(archive)s" at %(timestamp)s') % {'archive': archive.name, 'timestamp': timezone.now()})
        self.stdout.write(_('Remote path: %s') % archive.url)
        self.stdout.write(_('Local path: %s') % archive.root_node.abs_path())

        local_dir = os.path.dirname(archive.root_node.abs_path())
        if not os.path.isdir(local_dir):
            os.makedirs(local_dir)

        mutex = Lock()
        thread = RsyncThread(archive, mutex)
        thread.start()

        while thread.isAlive() or thread.buffer:
            if len(thread.buffer) > 1 or not thread.isAlive():
                mutex.acquire()
                line = thread.buffer.pop(0)
                mutex.release()
                try:
                    self._process_output(line, archive)
                except KeyboardInterrupt:
                    thread.process.kill()
                    msg = _("Keyboard Interrupt, finishing %d items in buffer...") % max(len(thread.buffer) - 1, 0)
                    self.stderr.write(msg)
                    self.iteration.errors += msg + "\n"
                    while len(thread.buffer) > 1:
                        self._process_output(thread.buffer.pop(0), archive)
                    break
                except BaseException as exception:
                    msg = "%Error in: %s" % (_("Error in: %s") % line) + "\n%s: %s" % (type(exception).__name__, str(exception))
                    self.stderr.write(msg)
                    self.iteration.errors += msg + "\n"
            else:
                sleep(1)

        if thread.error:
            self.stderr.write(thread.error)
            self.iteration.errors += thread.error + "\n"

    def _process_output(self, line, archive):
        if not line.startswith('*') and not self.valid_line.match(line):
            raise ArGyverException('Invalid line')

        line = line.decode('utf-8')
        action = line[0]
        node_type = line[1]
        path = os.path.join(archive.root_node.path, line[12:]).replace('/./', '/')

        # check file type
        if node_type not in ['f', 'd']:
            self.stderr.write(_('Unkownn RSYNC file type received: %s') % line)

        # Deleting
        elif action == '*':
            if not line.startswith('*deleting'):
                self.stderr.write(_('Unkownn RSYNC status received: %s') % line)
                return
            self._delete_node(path)
        elif action == 'h':
            # TODO handle hardlinks, might involve storing inodes in data table
            self._add_or_update_node(path)
        else:
            self._add_or_update_node(path)

    def _add_or_update_node(self, path):
        self.stdout.write(_("Add: %s") % path)
        node = Node.get_or_create_from_path(path)

        if not os.path.exists(node.abs_path()):
            self.stderr.write(_('Tried to add %s to the database, but it does not exist on disk!') % node.path)
            return

        if node.is_file():
            timestamp = os.path.getmtime(node.abs_path())
            timestamp = timezone.datetime.fromtimestamp(timestamp)
            timestamp = timezone.make_aware(timestamp, timezone.get_default_timezone())
        else:
            timestamp = None

        if node.is_file():
            data = self._add_file_to_repo(node)
        else:
            data = None

        try:
            old_version = node.get_current_version()
        except Version.DoesNotExist:
            old_version = None

        if old_version and old_version.data == data:
            old_version.timestamp = timestamp
            old_version.save()
        else:
            new_version = Version(node=node, data=data, timestamp=timestamp, created=timezone.now())
            if old_version:
                old_version.deleted = new_version.created
                old_version.save()
            new_version.save()

    def _delete_node(self, path):
        self.stdout.write(_("Delete: %s") % path)
        try:
            node = Node.get_from_path(path)
        except Node.DoesNotExist:
            self.stderr.write(_("%s was removed by RSYNC, but it does not exist in the database!") % path)
            return
        if node.is_dir():
            for file_node in node.node_set.filter(~Q(name__endswith=os.path.sep)):
                if file_node.exists():
                    version = file_node.get_current_version()
                    version.deleted = timezone.now()
                    version.save()
        version = node.get_current_version()
        version.deleted = timezone.now()
        version.save()

    def _add_file_to_repo(self, node):
        node_path = node.abs_path()
        if not os.path.exists(node_path):
            self.stderr.write(_("Tried to add %s to the repository, but the file doesn't exist!") % node_path)
            return

        try:
            with open(node_path, 'rb') as fp:
                md5sum = md5()
                while True:
                    content = fp.read(self.BUFFER_SIZE)
                    if not content:
                        break
                    md5sum.update(content)
            md5sum = md5sum.hexdigest()
        except BaseException as exception:
            self.stderr.write("%s: %s" % (type(exception).__name__, str(exception)))
            return

        try:
            data = Data.objects.get(hash=md5sum)
        except Data.DoesNotExist:
            data = Data(hash=md5sum, size=os.path.getsize(node_path))
            data.save()

        data_path = data.abs_path()

        if os.path.exists(data_path):
            if data.size > 0:
                os.remove(node_path)
                os.link(data.abs_path(), node_path)
        else:
            data_dir = os.path.dirname(data.abs_path())
            if not os.path.isdir(data_dir):
                os.makedirs(data_dir)
            os.link(node_path, data_path)

        return data


class RsyncThread(Thread):

    MAX_BUFFER = 1000  # lines of output

    def __init__(self, archive, mutex):
        self.archive = archive
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
#        rsync += ' -aH --out-format=\'%i %n\' --outbuf=L --delete --delete-excluded '
        rsync += ' -aH --out-format=\'%i %n\' --delete --delete-excluded '
        if self.archive.remote_port != 22:
            rsync += '-e \'ssh -p %d\'' % self.archive.remote_port
        if self.archive.rsync_arguments:
            rsync += self.archive.rsync_arguments
        rsync += " \"%s\" \"%s\"" % (self.archive.url, self.archive.root_node.abs_path())
        return rsync
