from django.contrib import admin
from .models import Event, Bookings, ExpiredEvent

class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "seats"]


admin.site.register(Event, EventAdmin)
admin.site.register(Bookings)

from django.utils import timezone
class ExpiredEventAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(dnt__lt=timezone.now())
    
admin.site.register(ExpiredEvent, ExpiredEventAdmin)