from django.contrib import admin
from .models import CustomUser
# Register your models here.


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name')
    search_fields = ('id', 'email', 'username', 'first_name', 'last_name')


admin.site.register(CustomUser, CustomUserAdmin)
