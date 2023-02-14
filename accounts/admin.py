from django.contrib import admin

from accounts.models import User, UserProfile
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    list_display = ('email','username','first_name', 'last_name', 'role', 'is_active')
    ordering = ('-date_joined',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# Register your models here.
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)