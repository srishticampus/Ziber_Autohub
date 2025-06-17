#admin_panel/admin.py
from django.contrib import admin
from .models import UpcomingLaunch
# Register your models here.

@admin.register(UpcomingLaunch)
class UpcomingLaunchAdmin(admin.ModelAdmin):
    list_display = ('car_name', 'launch_date', 'launch_time_start', 'launch_time_end', 'venue', 'location', 'created_at')
    list_filter = ('launch_date', 'location')
    search_fields = ('car_name', 'car_minimal_details', 'car_description', 'venue', 'location')
    fieldsets = (
        ('Car Details', {
            'fields': ('car_name', 'car_minimal_details', 'car_description')
        }),
        ('Launch Event Details', {
            'fields': ('launch_date', 'launch_time_start', 'launch_time_end', 'venue', 'location')
        }),
    )