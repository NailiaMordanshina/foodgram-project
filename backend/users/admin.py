from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class UsersAdmin(admin.ModelAdmin):
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email',)


admin.site.register(User, UserAdmin)
