from django.contrib import admin

from NAFAN.models import *

class UserAdmin(admin.ModelAdmin):
    pass

admin.site.register(User, UserAdmin)