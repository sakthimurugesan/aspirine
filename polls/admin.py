from django.contrib import admin
from .models import State, Taluka, District, Lane, Junction, OffSwitch, Coordinates, M,OffTable,JunctionLaneState,CurrentJunctionState


class OffSwitchInline(admin.TabularInline):
    model = OffSwitch
    extra = 1

class CoordinatesAdmin(admin.ModelAdmin):
    inlines = [
        OffSwitchInline,
    ]

class LaneAdmin(admin.ModelAdmin):
    prepopulated_fields=[]

admin.site.register(Coordinates, CoordinatesAdmin)

admin.site.register(State)
admin.site.register(District)
admin.site.register(Taluka)
admin.site.register(Lane)
admin.site.register(Junction)
admin.site.register(M)
admin.site.register(OffTable)
admin.site.register(JunctionLaneState)
admin.site.register(CurrentJunctionState)
