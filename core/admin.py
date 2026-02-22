from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department, ServiceCharter, Complaint, ComplaintRemark

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'department', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'department')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(Department)
admin.site.register(ServiceCharter)
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'title', 'citizen', 'department', 'status', 'created_at', 'ip_address')
    list_filter = ('status', 'department', 'created_at')
    search_fields = ('tracking_id', 'title', 'description', 'citizen__username', 'ip_address')
    readonly_fields = ('tracking_id', 'ip_address', 'browser_info', 'created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('tracking_id', 'title', 'description', 'status')
        }),
        ('User & Assignment', {
            'fields': ('citizen', 'department', 'assigned_to')
        }),
        ('Evidence & Location', {
            'fields': ('location', 'image')
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'browser_info', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ComplaintRemark)
class ComplaintRemarkAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'user', 'created_at')
    search_fields = ('complaint__tracking_id', 'remark', 'user__username')
