from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.conf import settings
from models import Location, Node


class ArgyverView(View):
    def get(self, request, path):
        try:
            html = self.render_main(path)
        except Node.DoesNotExist:
            raise Http404()
        if html is None:
            return HttpResponseRedirect(reverse('admin:argyver_location_add'))
        return HttpResponse(html)

    def render_main(self, path):
        if path:
            root_node = Node.get_from_url(path.split('/')[0])
            location = Location.objects.get(root_node=root_node)
            node = Node.get_from_url(path)
        else:
            try:
                location = Location.get_first()
            except Location.DoesNotExist:
                return None
            else:
                node = location.root_node

        context = {
            'settings': settings,
            'locations': self.render_locations(location),
            'folders': self.render_folders(location, node),
            'files': self.render_files(node),
            'versions': self.render_versions(node),
        }
        return render_to_string('main.html', context)

    def render_locations(self, location):
        context = {
            'settings': settings,
            'location_list': Location.objects.all(),
            'current': location,
        }
        return render_to_string('locations.html', context)

    def render_folders(self, location, node):
        context = {
            'settings': settings,
            'location': location,
            'current': node,
        }
        return render_to_string('folders.html', context)

    def render_files(self, node):
        context = {
            'settings': settings,
            'node': node,
        }
        return render_to_string('files.html', context)

    def render_versions(self, node):
        context = {
            'settings': settings,
            'node': node,
        }
        return render_to_string('versions.html', context)
