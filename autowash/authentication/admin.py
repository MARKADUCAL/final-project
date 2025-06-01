from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Service, Booking

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'service', 'date_time', 'status', 'vehicle_make', 'vehicle_model')
    list_filter = ('status', 'date_time', 'service')
    search_fields = ('booking_id', 'user__username', 'vehicle_make', 'vehicle_model', 'license_plate')
    readonly_fields = ('booking_id', 'created_at', 'updated_at')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Service)
admin.site.register(Booking, BookingAdmin)
