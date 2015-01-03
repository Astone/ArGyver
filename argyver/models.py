import os

from django.utils.translation import ugettext as _
from django.db import models
from django.conf import settings


ArGyverException = Exception


class Node(models.Model):
    parent = models.ForeignKey('Node', blank=True, null=True)
    name = models.CharField(max_length=255, db_index=True)

    @property
    def path(self):
        if self.parent:
            return os.path.join(self.parent.path, self.name)
        return self.name

    def abs_path(self):
        return os.path.join(settings.AGV_SNAP_DIR, self.path)

    def get_versions(self):
        version_set = Version.objects.filter(node=self, deleted=None).order_by('-created')
        return version_set

    def get_latest_version(self):
        version_set = self.get_versions()
        if not version_set.exists():
            raise Version.DoesNotExist
        return version_set[0]

    def __unicode__(self):
        return unicode(self.path)

    @classmethod
    def get_or_create(cls, parent, name):
        try:
            node = Node.objects.get(parent=parent, name=name)
        except Node.DoesNotExist:
            node = Node(parent=parent, name=name)
            node.save()
        return node

    @classmethod
    def get_or_create_from_path(cls, path):
        node_list = path.split(os.path.sep)
        node = None
        for name in node_list[:-1]:
            node = Node.get_or_create(parent=node, name=name + os.path.sep)
        name = node_list[-1]
        if name:
            node = Node.get_or_create(parent=node, name=name)
        return node

    @classmethod
    def get_from_path(cls, path):
        node_list = path.split(os.path.sep)
        node = None
        for name in node_list[:-1]:
            node = Node.objects.get(parent=node, name=name + os.path.sep)
        name = node_list[-1]
        if name:
            node = Node.objects.get(parent=node, name=name)
        return node

    class Meta:
        verbose_name = _('file system node')
        verbose_name_plural = _('file system nodes')


class Data(models.Model):
    hash = models.CharField(max_length=32, unique=True, db_index=True)
    timestamp = models.DateTimeField()
    size = models.IntegerField()

    @property
    def path(self):
        return os.path.join(self.hash[:2], self.hash)

    def abs_path(self):
        return os.path.join(settings.AGV_REPO_DIR, self.path)

    def __unicode__(self):
        return unicode(self.path)

    class Meta:
        verbose_name = _('file in repository')
        verbose_name_plural = _('file in repository')


class Version(models.Model):
    node = models.ForeignKey(Node, db_index=True)
    data = models.ForeignKey(Data, blank=True, null=True)
    created = models.DateTimeField(db_index=True)
    deleted = models.DateTimeField(blank=True, null=True, db_index=True)

    class Meta:
        verbose_name = _('version')
        verbose_name_plural = _('versions')


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=32, unique=True)
    remote_host = models.CharField(
        max_length=255,
        help_text=_('For example: %s') % '173.194.65.121')
    remote_port = models.SmallIntegerField(
        default=22,
        help_text=_('Default is: %s') % '22')
    remote_user = models.CharField(
        max_length=64,
        help_text=_('For example: %s') % 'angus')
    remote_path = models.CharField(
        max_length=255,
        help_text=_('For example: %s') % 'Documents/' + ' (' + _('which is equal to') + ' /home/angus/Documents/)')
    rsync_arguments = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_('AGV_WARNING_RSYNC_ARGUMENTS'))
    root_node = models.ForeignKey(Node, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if self.id is None:
            if Node.objects.filter(name=self.slug + '/', parent=None).exists():
                raise ArGyverException(_('AGV_EXCEPTION_LOCATION_ROOT_FOLDER_EXISTS'))
            self.root_node = Node(name=self.slug + '/')
            self.root_node.save()
        self.remote_path = self.remote_path.replace('*', '').rstrip('/') + '/'
        super(Location, self).save(*args, **kwargs)


    @property
    def url(self):
        return "%s@%s:%s" % (self.remote_user, self.remote_host, self.remote_path)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        ordering = ['name']
        verbose_name = _('remote location')
        verbose_name_plural = _('remote locations')
