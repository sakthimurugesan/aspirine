from django.contrib import admin
from .models import State, Taluka, District, Lane, Junction, OffSwitch, Coordinates, M,OffTable


class OffSwitchInline(admin.TabularInline):
    model = OffSwitch
    extra = 1

class CoordinatesAdmin(admin.ModelAdmin):
    inlines = [
        OffSwitchInline,
    ]

admin.site.register(Coordinates, CoordinatesAdmin)

admin.site.register(State)
admin.site.register(District)
admin.site.register(Taluka)
admin.site.register(Lane)
admin.site.register(Junction)
admin.site.register(M)
admin.site.register(OffTable)