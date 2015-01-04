from django.core.management.base import BaseCommand, CommandError
from argyver.models import Archive, Node
from django.utils.translation import ugettext as _
from django.utils import timezone
import shutil
import os


class Command(BaseCommand):
    args = '<archive archive ...>'
    help = 'Removes all the data (on disk and in the database) for specified archives'

    def handle(self, *args, **options):
        archive_list = []
        for slug in args:
            try:
                archive_list.append(Archive.objects.get(slug=slug))
            except Archive.DoesNotExist:
                raise CommandError('Archive "%s" does not exist' % slug)

        started = timezone.now()

        for archive in archive_list:
            self.stdout.write(_('Resetting "%(archive)s" at %(timestamp)s') % {'archive': archive.name, 'timestamp': started})
            self._reset_db(archive)
            self._reset_fs(archive)

        self.stdout.write(_('Note that only the links are removed; the actual data is still stored in the repository'))
        self.stdout.write(_('Run ./manage.py cleanupargyver to remove the data as well.'))
        self.stdout.write(_('Finished in %d seconds') % (timezone.now() - started).total_seconds())

    def _reset_db(self, archive):
        self.stdout.write(_('Removing database objects below: %s') % archive.root_node.name)
        Node.objects.filter(parent=archive.root_node).delete()

    def _reset_fs(self, archive):
        path = archive.root_node.abs_path()
        self.stdout.write(_('Removing directory: %s') % path)
        if os.path.exists(path):
            shutil.rmtree(path)
