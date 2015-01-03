import os

from django.utils.translation import ugettext as _
from django.db import models
from django.conf import settings


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
        help_text=_('Only use this if you know what you are doing, it might break the ArGyver.') + ' ' +
        _('Using -exclude and --include should be fine.'))

    def url(self):
        remote_path = self.remote_path.rstrip('/') + '/'
        return "%s@%s:%s" % (self.remote_user, self.remote_host, remote_path)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        ordering = ['name']
        verbose_name = _('remote location')
        verbose_name_plural = _('remote locations')


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

    def __unicode__(self):
        return unicode(self.path)

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
