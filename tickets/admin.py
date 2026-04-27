from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Perfil, Sede, Categoria, Subcategoria, Ticket
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
        'solucion',
        'archivo',
    )

    def save_model(self, request, obj, form, change):
        if obj.estado == 'cerrado' and not obj.solucion:
            raise ValidationError("Debes ingresar una solución para cerrar el ticket.")
        super().save_model(request, obj, form, change)


# Inline Perfil
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False


class CustomUserAdmin(UserAdmin):
    inlines = (PerfilInline,)


# 🔥 IMPORTANTE
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# 🔥 ESTO ES LO QUE TE FALTA (clave)
admin.site.register(Sede)
admin.site.register(Categoria)
admin.site.register(Subcategoria)

def dashboard_redirect(request):
    return redirect('/dashboard/')

admin.site.get_urls = lambda: [
    path('dashboard/', dashboard_redirect)
] + admin.site.get_urls()