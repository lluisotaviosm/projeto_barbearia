from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'nome_completo', 'telefone', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('nome_completo', 'telefone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('nome_completo', 'telefone')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
