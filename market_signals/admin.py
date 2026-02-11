from django.contrib import admin
from .models import WeatherSignal, LocalEvent

@admin.register(WeatherSignal)
class WeatherSignalAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'temperature', 'precipitation')
    list_filter = ('timestamp',)

@admin.register(LocalEvent)
class LocalEventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'date', 'impact_score')
    list_filter = ('date',)
    search_fields = ('event_name',)