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
admin.site.register(Complaint)
admin.site.register(ComplaintRemark)
