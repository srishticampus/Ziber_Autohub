from django.contrib import admin

# Register your models here.
from .models import UserProfile,Car,ServiceBooking

admin.site.register(UserProfile)
admin.site.register(Car)

@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'car_model', 'service_date', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'car_model')


from django.contrib import admin
from .models import JobVacancy, JobApplication

# For Job Vacancy
@admin.register(JobVacancy)
class JobVacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'posted_at')
    search_fields = ('title', 'location')
    list_filter = ('posted_at',)

# For Job Applications
@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'applied_at', 'status')
    list_filter = ('status', 'applied_at')
    search_fields = ('job__title', 'applicant__username')
