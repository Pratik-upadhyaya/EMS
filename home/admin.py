from django.contrib import admin
from .models import Event, Bookings


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "seats"]


@admin.register(Bookings)
class BookingsAdmin(admin.ModelAdmin):
    list_display = ["event", "participant", "booked_at"]