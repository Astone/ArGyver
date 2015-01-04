from django.views.generic.base import View
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from django.conf import settings
from models import Location


class ArgyverView(View):
    def get(self, request, path):
        html = self.render_main(path)
        return HttpResponse(html)

    def render_main(self, path):
        context = {
            'settings': settings,
            'locations': self.render_locations(path),
        }
        return render_to_string('main.html', context)

    def render_locations(self, path):
        context = {
            'settings': settings,
            'location_list': Location.objects.all(),
        }
        try:
            context['current'] = Location.get_first()
        except Location.DoesNotExist:
            pass
        return render_to_string('locations.html', context)

