from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import filesizeformat
from argyver.models import Data
from django.utils.translation import ugettext as _
from django.conf import settings
from django.utils import timezone
from hashlib import md5
import os


class Command(BaseCommand):
    args = '[dir]'
    help = 'Removes all files in a folder to the repository'

    BUFFER_SIZE = 4 * (2 ** 20)  # 4MB

    def handle(self, *args, **options):
        if not args:
            src_path = settings.AGV_SNAP_DIR
	else:
            src_path = args[0]

        started = timezone.now()

        inode_set = set()
        for (path, folder_list, file_list) in os.walk(settings.AGV_REPO_DIR):
            for file_name in file_list:
                inode_set.add(os.stat(os.path.join(path, file_name)).st_ino)
        self.stdout.write("%d inodes loaded" % len(inode_set))

        for (path, folder_list, file_list) in os.walk(src_path):
            for file_name in file_list:
                file_path = os.path.join(path, file_name)
                if not os.stat(file_path).st_ino in inode_set:
                    self._add_file_to_repo(file_path)

        self.stdout.write(_('Finished in %d seconds') % (timezone.now() - started).total_seconds())


    def _add_file_to_repo(self, file_path):
        print "Reading", file_path
        try:
            with open(file_path, 'rb') as fp:
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

        data = Data(hash=md5sum, size=os.path.getsize(file_path))

        data_path = data.abs_path()

        if os.path.exists(data_path):
            if data.size > 0:
                print "-- Linking", file_path
                os.remove(file_path)
                os.link(data_path, file_path)
            else:
                print "-- Skipping", file_path
        else:
            print "-- Creating", data_path
            data_dir = os.path.dirname(data_path)
            if not os.path.isdir(data_dir):
                os.makedirs(data_dir)
            os.link(file_path, data_path)

