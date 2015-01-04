from django.core.management.base import BaseCommand, CommandError
from argyver.models import Location, Node
from django.utils.translation import ugettext as _
from django.utils import timezone
import shutil
import os


class Command(BaseCommand):
    args = '<location location ...>'
    help = 'Removes all the data (on disk and in the database) for specified locations'

    def handle(self, *args, **options):
        location_list = []
        for slug in args:
            try:
                location_list.append(Location.objects.get(slug=slug))
            except Location.DoesNotExist:
                raise CommandError('Location "%s" does not exist' % slug)

        started = timezone.now()

        for location in location_list:
            self.stdout.write(_('Resetting "%(location)s" at %(timestamp)s') % {'location': location.name, 'timestamp': started})
            self._reset_db(location)
            self._reset_fs(location)

        self.stdout.write(_('Note that only the links are removed; the actual data is still stored in the repository'))
        self.stdout.write(_('Run ./manage.py cleanupargyver to remove the data as well.'))
        self.stdout.write(_('Finished in %d seconds') % (timezone.now() - started).total_seconds())

    def _reset_db(self, location):
        self.stdout.write(_('Removing database objects below: %s') % location.root_node.name)
        Node.objects.filter(parent=location.root_node).delete()

    def _reset_fs(self, location):
        path = location.root_node.abs_path()
        self.stdout.write(_('Removing directory: %s') % path)
        if os.path.exists(path):
            shutil.rmtree(path)
