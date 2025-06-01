from django.contrib import admin
from .models import AdminProfile, AdminLog

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'phone_number', 'date_joined')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('position', 'date_joined')

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'timestamp', 'ip_address')
    search_fields = ('admin__username', 'action', 'details')
    list_filter = ('timestamp', 'action')
    readonly_fields = ('admin', 'action', 'timestamp', 'ip_address', 'details')
