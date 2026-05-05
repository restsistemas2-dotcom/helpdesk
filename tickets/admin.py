from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Perfil, Sede, Categoria, Subcategoria, Ticket
from django.core.exceptions import ValidationError
from django.urls import path
from django.shortcuts import redirect
from .models import Ticket
import threading
from django.conf import settings
from django.core.mail import send_mail

def borrar_tickets(modeladmin, request, queryset):
        Ticket.objects.all().delete()

borrar_tickets.short_description = "🗑 Borrar TODOS los tickets"
    
# Guardar el método original
original_get_urls = admin.site.get_urls

def custom_get_urls():
    urls = original_get_urls()
    custom_urls = [
        path('dashboard/', lambda request: redirect('/dashboard/'))
    ]
    return custom_urls + urls

admin.site.get_urls = custom_get_urls

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'sede', 'estado', 'prioridad', 'tecnico')
    list_filter = ('estado', 'prioridad', 'tecnico')
    search_fields = ('descripcion',)
    
    actions = [borrar_tickets]  # 👈 AGREGAR ESTO

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
        cerrado_ahora = False

        # 🔍 Detectar si se está cerrando en este momento
        if obj.pk:
            original = Ticket.objects.get(pk=obj.pk)
            if original.estado != 'cerrado' and obj.estado == 'cerrado':
                cerrado_ahora = True

        # 💾 Guardar primero
        super().save_model(request, obj, form, change)

        # 📧 Enviar correo SOLO si se acaba de cerrar
        if cerrado_ahora:
            try:
                destinatarios = []

                if obj.sede.correo:
                    destinatarios.append(obj.sede.correo)

                destinatarios.append('emontenegro@100montaditosca.com')

                def enviar():
                    send_mail(
                        subject=f'✅ Ticket #{obj.id} CERRADO',
                        message=f'''
Hola,

Tu ticket ha sido cerrado.

🆔 ID: {obj.id}
🏢 Sede: {obj.sede}
📅 Fecha cierre: {obj.fecha_cierre}

🛠️ Solución:
{obj.solucion or "Ticket atendido correctamente."}

Gracias por utilizar la mesa de ayuda.
''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=destinatarios,
                        fail_silently=False,
                    )
                    print("✅ Correo enviado desde ADMIN")

                threading.Thread(target=enviar).start()

            except Exception as e:
                print("❌ ERROR ADMIN:", e)


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