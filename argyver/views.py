from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.conf import settings
from models import Archive, Node, Version
from django.utils import timezone
from datetime import datetime
import re

class ArgyverView(View):
    def get(self, request, path):
        try:
            html = self.render_main(path)
        except Node.DoesNotExist:
            raise Http404()
        if html is None:
            return HttpResponseRedirect(reverse('admin:argyver_archive_add'))
        html = re.sub(r'\n\s+', '\n', html)
        return HttpResponse(html)

    def render_main(self, path):
        if path:
            root_node = Node.get_from_url(path.split('/')[0])
            archive = Archive.objects.get(root_node=root_node)
            node = Node.get_from_url(path)
        else:
            try:
                archive = Archive.get_first()
            except Archive.DoesNotExist:
                return None
            else:
                node = archive.root_node

        context = {
            'settings': settings,
            'archives': self.render_archives(archive),
            'folders': self.render_folders(archive, node),
            'files': self.render_files(archive, node),
            'versions': self.render_versions(node),
        }
        return render_to_string('main.html', context)

    def render_archives(self, archive):
        context = {
            'settings': settings,
            'archive_list': Archive.objects.all(),
            'current': archive,
        }
        return render_to_string('archives.html', context)

    def render_folders(self, archive, node):
        context = {
            'settings': settings,
            'archive': archive,
            'current': node,
        }
        return render_to_string('folders.html', context)

    def render_files(self, archive, node):
        context = {
            'settings': settings,
            'archive': archive,
            'folder': [node, node.parent][node.is_file()],
            'current': node,
        }
        return render_to_string('files.html', context)

    def render_versions(self, node):
        context = {
            'settings': settings,
            'node': node,
        }
        return render_to_string('versions.html', context)


class DownloadView(View):
    def get(self, request, path, version):
        try:
            node = Node.get_from_url(path)
        except Node.DoesNotExist:
            raise Http404()

        try:
            created = datetime.strptime(version, '%Y%m%d-%H%M%S')
            created = timezone.get_current_timezone().localize(created)
            version = node.version_set.get(created=created)
        except Version.DoesNotExist:
            raise Http404()

        response = HttpResponse()
        del response['Content-Type']
        response['Content-Disposition'] = 'attachment; filename=%s' % node.name.encode('utf-8')
        response['Content-Length'] = version.data.size
        if settings.DEBUG:
            with open(version.data.abs_path(), 'rb') as fp:
                response.content = fp.read()
        else:
            response['X-Sendfile'] = version.data.abs_path().encode('utf-8')
        return response
