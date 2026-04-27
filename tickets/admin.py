from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Perfil
from .models import Sede, Categoria, Subcategoria, Ticket
from django.core.exceptions import ValidationError
from django.urls import path
from django.shortcuts import redirect
    
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'sede', 'estado', 'prioridad', 'tecnico')
    
    list_filter = ('estado', 'prioridad', 'tecnico')
    
    search_fields = ('descripcion',)

    fields = (
        'usuario',
        'sede',
        'categoria',
        'subcategoria',
        'descripcion',
        'impacto',
        'urgencia',
        'prioridad',
        'estado',
        'tecnico',
        'solucion',  # AGREGAR ESTO
        'archivo',
    )
    def save_model(self, request, obj, form, change):
        if obj.estado == 'cerrado' and not obj.solucion:
            raise ValidationError("Debes ingresar una solución para cerrar el ticket.")
    
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.estado == 'cerrado':
            return ()
        return ('solucion',)

class CustomAdminSite(admin.AdminSite):
    site_header = "HelpDesk Admin"
    site_title = "HelpDesk"
    index_title = "Panel de administración"

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path('dashboard/', self.admin_view(self.ver_dashboard))
        ]

        return custom_urls + urls

    def ver_dashboard(self, request):
        return redirect('/dashboard/') 
 
# Inline para Perfil dentro de User
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'

# Extender UserAdmin
class CustomUserAdmin(UserAdmin):
    inlines = (PerfilInline,)
    
admin_site = CustomAdminSite(name='custom_admin')
    
admin_site.register(Ticket)
admin_site.register(Sede)
admin_site.register(Categoria)
admin_site.register(Subcategoria)
admin_site.register(User, CustomUserAdmin)

# Register your models here.
