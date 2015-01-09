from django.core.management.base import BaseCommand, CommandError
from argyver.models import Archive, ArGyverException
from django.utils.translation import ugettext as _
from django.utils import timezone
import shutil
import os


class Command(BaseCommand):
    args = '<archive archive ...>'
    help = 'Syncs the files on disk with the files in the database (db is leading)'

    def handle(self, *args, **options):
        archive_list = []
        for slug in args:
            try:
                archive_list.append(Archive.objects.get(slug=slug))
            except Archive.DoesNotExist:
                raise CommandError('Archive "%s" does not exist' % slug)

        started = timezone.now()

        for archive in archive_list:
            self.stdout.write(_('Cleaning up "%(archive)s" at %(timestamp)s') % {'archive': archive.name, 'timestamp': started})
            self._cleanup(archive.root_node)

        self.stdout.write(_('Note that only the links are removed; the actual data is still stored in the repository.'))
        self.stdout.write(_('Run ./manage.py cleanupargyver to remove the data as well.'))
        self.stdout.write(_('Finished in %d seconds') % (timezone.now() - started).total_seconds())

    def _cleanup(self, db_node):

        db_node.node_set.filter(version=None).delete()

        db_sub_nodes = [node for node in db_node.node_set.all() if node.get_latest_version().deleted is None]
        db_folders = set([node.name[:-1] for node in db_sub_nodes if node.is_dir()])
        db_files = set([node.name for node in db_sub_nodes if node.is_file()])

        fs_node = db_node.abs_path()
        fs_sub_nodes = [node for node in os.listdir(fs_node) if node != '.' and node != '..']
        fs_folders = set([node for node in fs_sub_nodes if os.path.isdir(os.path.join(fs_node, node))])
        fs_files = set([node for node in fs_sub_nodes if os.path.isfile(os.path.join(fs_node, node))])

        to_remove = (fs_files - db_files) | (fs_folders - db_folders)
        self._remove_fs(fs_node, to_remove)

        to_restore = (db_files - fs_files) | (db_folders - fs_folders)
        to_restore = [node for node in db_sub_nodes if node.name.strip('/') in to_restore]
        self._restore_fs(to_restore)

        db_sub_nodes = [node for node in db_sub_nodes if node.is_dir()]
        for node in db_sub_nodes:
            self._cleanup(node)

    def _remove_fs(self, path, node_list):
        for node in node_list:
            node_path = os.path.join(path, node)
            self.stdout.write(_('Removing %s') % node_path)
            if os.path.islink(node_path):
                os.remove(node_path)
            elif os.path.isdir(node_path):
                shutil.rmtree(node_path)
            elif os.path.isfile(node_path):
                os.remove(node_path)

    def _restore_fs(self, node_list):
        for node in node_list:
            self.stdout.write(_('Restoring %s') % node.abs_path())
            try:
                node.restore()
            except ArGyverException as e:
                self.stderr.write(str(e))
