from django.contrib import admin
from models import Location


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'url', 'remote_port', 'rsync_arguments')
    actions = ()

    def get_readonly_fields(self, request, obj=None):
        fields = super(LocationAdmin, self).get_readonly_fields(request, obj)
        if obj:
            fields += ('slug',)
        return fields

admin.site.register(Location, LocationAdmin)
