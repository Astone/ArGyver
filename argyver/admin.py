from django.contrib import admin
from models import Location, Node, Data, Version

admin.site.disable_action('delete_selected')


class VersionInline(admin.TabularInline):
    model = Version
    extra = 0

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'url', 'remote_port', 'rsync_arguments')
    actions = ()
    def get_readonly_fields(self, request, obj=None):
        fields = super(LocationAdmin, self).get_readonly_fields(request, obj)
        if obj:
            fields += ('slug',)
        return fields


class NodeAdmin(admin.ModelAdmin):
    inlines = [VersionInline]


class DataAdmin(admin.ModelAdmin):
    inlines = [VersionInline]

admin.site.register(Location, LocationAdmin)
admin.site.register(Node, NodeAdmin)
admin.site.register(Data, DataAdmin)
admin.site.register(Version)
