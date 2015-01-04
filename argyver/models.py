import os

from django.utils.translation import ugettext as _
from django.templatetags.static import static
from django.db import models
from django.conf import settings
from django.utils.text import slugify

ArGyverException = Exception


class Node(models.Model):
    parent = models.ForeignKey('self', blank=True, null=True)
    name = models.CharField(max_length=255, db_index=True)
    slug = models.CharField(max_length=255, db_index=True)

    unique_together = (('parent', 'name'),)

    @property
    def path(self):
        if self.parent:
            return os.path.join(self.parent.path, self.name)
        return self.name

    @property
    def url(self):
        if self.parent:
            url = self.parent.url
        else:
            url = '/'
        url += self.slug
        if self.name.endswith(os.path.sep):
            url += '/'
        return url

    def abs_path(self):
        return os.path.join(settings.AGV_SNAP_DIR, self.path)

    def parents(self):
        parents = []
        node = self.parent
        while node and node.parent:
            parents = [node] + parents
            node = node.parent
        return parents

    def siblings(self):
        if self.parent:
            return self.parent.node_set.all()
        return []

    def get_versions(self):
        version_set = Version.objects.filter(node=self).order_by('-created')
        return version_set

    def get_latest_version(self):
        version_set = self.get_versions()
        if not version_set.exists():
            raise Version.DoesNotExist
        return version_set[0]

    def get_current_version(self):
        version = self.get_latest_version()
        if version.deleted:
            raise Version.DoesNotExist
        return version

    def exists(self):
        try:
            self.get_latest_version()
        except Version.DoesNotExist:
            return False
        return True

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name.replace('.', '-'))
        super(Node, self).save(*args, **kwargs)

    def __unicode__(self):
        return unicode(self.path)

    def is_dir(self):
        return self.name.endswith(os.path.sep)

    def is_file(self):
        return not self.name.endswith(os.path.sep)

    def restore(self):
        if self.is_dir():
            os.mkdir(self.abs_path())
        elif self.is_file():
            data = self.get_current_version().data
            os.link(data.abs_path(), self.abs_path())

    def icon(self):
        if self.is_dir():
            ext = 'folder'
        else:
            ext = self.name.lower().split('.')[-1]
        icon = "img/ext/%s.png" % ext
        if not os.path.isfile(os.path.join(settings.BASE_DIR, 'argyver', 'static', icon)):
            icon = "img/ext/file.png"
        return static(icon)

    def thumbnail(self):
        if self.is_dir():
            return None
        try:
            version = self.get_latest_version()
        except Version.DoesNotExist:
            return None

        thumb = version.data.path + '.png'
        thumb = os.path.join(settings.AGV_THMB_DIR, thumb)
        thumb = os.path.relpath(thumb, settings.AGV_DATA_DIR)
        if not os.path.isfile(os.path.join(settings.AGV_DATA_DIR, thumb)):
            return False

        return static(thumb)

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

    @classmethod
    def get_from_url(cls, url):
        node_list = url.split('/')
        node = None
        for slug in node_list[:-1]:
            node = Node.objects.get(parent=node, slug=slug)
        slug = node_list[-1]
        if slug:
            node = Node.objects.get(parent=node, slug=slug)
        return node

    class Meta:
        verbose_name = _('file system node')
        verbose_name_plural = _('file system nodes')
        ordering = ['name']


class Data(models.Model):
    hash = models.CharField(max_length=32, unique=True, db_index=True)
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
        verbose_name_plural = _('files in repository')


class Version(models.Model):
    node = models.ForeignKey(Node, db_index=True)
    data = models.ForeignKey(Data, blank=True, null=True)
    timestamp = models.DateTimeField()
    created = models.DateTimeField(db_index=True)
    deleted = models.DateTimeField(blank=True, null=True, db_index=True)

    unique_together = (('node', 'data', 'timestamp'),)

    def __unicode__(self):
        if self.deleted:
            return "%s %s: (%s)" % (unicode(self.node), _('deleted'), self.deleted)
        else:
            return "%s %s: (%s)" % (unicode(self.node), _('created'), self.created)

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
        help_text=_('Only use this if you know what you are doing, it might break the ArGyver. Using -exclude and --include should be fine.'))
    root_node = models.ForeignKey(Node, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if self.id is None:
            if Node.objects.filter(name=self.slug + '/', parent=None).exists():
                raise ArGyverException(_("Someone tried to create a new location. The slug of a location defines the root folder of the corresponding archive and according to the database this root folder already exists."))
            self.root_node = Node(name=self.slug + '/')
            self.root_node.save()
            self.root_node_id = self.root_node.id
        self.remote_path = self.remote_path.replace('*', '').rstrip('/') + '/'
        super(Location, self).save(*args, **kwargs)

    @property
    def url(self):
        remote_path = self.remote_path.replace(r' ', r'\ ').replace(r'\\ ', r'\ ')
        return "%s@%s:%s" % (self.remote_user, self.remote_host, remote_path)

    def __unicode__(self):
        return unicode(self.name)

    @classmethod
    def get_first(cls):
        if Location.objects.exists():
            return Location.objects.order_by('name')[0]
        else:
            raise Location.DoesNotExist

    class Meta:
        ordering = ['name']
        verbose_name = _('remote location')
        verbose_name_plural = _('remote locations')
