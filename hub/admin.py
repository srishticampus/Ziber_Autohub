# hub/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Car, ServiceBooking, JobVacancy, JobApplication, Cart, CartItem, Order, OrderItem, PreBooking, Accessory,LaunchRegistration, Complaint, Feedback, TestDriveBooking # Import Accessory model

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_contact_number')
    list_select_related = ('profile', )

    def get_contact_number(self, instance):
        return instance.profile.contact_number
    get_contact_number.short_description = 'Contact Number'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'model', 'year', 'price', 'stock', 'is_new') # Added 'is_new'
    list_filter = ('brand', 'year', 'is_new', 'fuel_type') # Added 'is_new', 'fuel_type'
    search_fields = ('name', 'brand', 'model', 'description') # Added 'description'
    ordering = ('-year', 'brand')
    fieldsets = (
        (None, {
            'fields': ('seller', 'name', 'brand', 'model', 'year', 'fuel_type', 'is_new')
        }),
        ('Details', {
            'fields': ('price', 'stock', 'description', 'image', 'kms_driven', 'owner') # Added kms_driven, owner
        }),
    )

@admin.register(JobVacancy)
class JobVacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'posted_at', 'is_active')
    list_filter = ('is_active', 'location')
    search_fields = ('title', 'description')
    ordering = ('-posted_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'location')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Accessory) # NEW: Register the Accessory model
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'created_at')
    list_filter = ('category', 'created_at', 'stock')
    search_fields = ('name', 'description', 'category')
    ordering = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'category')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Visuals', {
            'fields': ('image',)
        }),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ServiceBooking)
admin.site.register(JobApplication)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(PreBooking)
admin.site.register(LaunchRegistration)
admin.site.register(Feedback)
admin.site.register(Complaint)
admin.site.register(TestDriveBooking)