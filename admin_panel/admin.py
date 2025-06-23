#admin_panel/admin.py
from django.contrib import admin
from .models import UpcomingLaunch
# Register your models here.

@admin.register(UpcomingLaunch)
class UpcomingLaunchAdmin(admin.ModelAdmin):
    list_display = ('car_name', 'launch_date', 'launch_time_start', 'launch_time_end', 'venue', 'location', 'created_at', 'image_thumbnail') # Added 'image_thumbnail'
    list_filter = ('launch_date', 'location')
    search_fields = ('car_name', 'car_minimal_details', 'car_description', 'venue', 'location')
    fieldsets = (
        ('Car Details', {
            'fields': ('car_name', 'car_minimal_details', 'car_description', 'image') # Added 'image'
        }),
        ('Launch Event Details', {
            'fields': ('launch_date', 'launch_time_start', 'launch_time_end', 'venue', 'location')
        }),
    )

    def image_thumbnail(self, obj):
        if obj.image:
            # Display a small thumbnail in the admin list view
            return f'<img src="{obj.image.url}" style="width: 50px; height: auto;" />'
        return "No Image"
    image_thumbnail.short_description = "Image"
    image_thumbnail.allow_tags = True # Allow rendering HTML