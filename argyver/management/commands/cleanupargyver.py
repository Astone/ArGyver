from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import filesizeformat
from argyver.models import Data
from django.utils.translation import ugettext as _
from django.conf import settings
from django.utils import timezone
import os


class Command(BaseCommand):
    help = 'Removes all unused data (on disk and in the database)'

    def handle(self, *args, **options):
        started = timezone.now()
        self._cleanup_db()
        self._cleanup_fs()
        self.stdout.write(_('Finished in %d seconds') % (timezone.now() - started).total_seconds())

    def _cleanup_db(self):
        self.stdout.write(_('Removing dangling database objects'))
        data = Data.objects.filter(version=None)
        count = data.count()
        data.delete()
        self.stdout.write(_('%d objects removed') % count)

    def _cleanup_fs(self):
        self.stdout.write(_('Removing files from repository'))
        count = 0
        total_size = 0
        for (path, folder_list, file_list) in os.walk(settings.AGV_REPO_DIR):
            for file_name in file_list:
                if not Data.objects.filter(hash=file_name).exists():
                    file_path = os.path.abspath(os.path.join(path, file_name))
                    count += 1
                    total_size += os.path.getsize(file_path)
                    os.remove(file_path)
        self.stdout.write(_('%d objects removed') % count)
        self.stdout.write(_('%s freed') % filesizeformat(total_size))
