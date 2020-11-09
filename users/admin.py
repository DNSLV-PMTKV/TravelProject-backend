from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext
from . import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['id', 'email', 'first_name',
                    'last_name', 'is_staff', 'is_active']
    fieldsets = [
        (None, {
            'fields': ('email', 'password')
        }),
        (gettext('Personal Info'), {
            'fields': ('first_name', 'last_name', 'profile_pic')
        }),
        (gettext('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        (gettext('Important dates'), {
            'fields': ('last_login', )
        }),
    ]
    add_fieldsets = [
        (None, {
            'classes': ('wide', ),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2')
        }),
    ]


class UnconfirmedUserAdmin(admin.ModelAdmin):
    list_display = ['token', 'user', ]
    search_fields = ['user__email', 'token']


admin.site.register(models.User, UserAdmin)
admin.site.register(models.UnconfirmedUser, UnconfirmedUserAdmin)
