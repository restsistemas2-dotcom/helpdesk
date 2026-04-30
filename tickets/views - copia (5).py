from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Ticket
from django.db.models import Count
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .models import Subcategoria
from .models import Categoria
from .models import Perfil
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, DurationField
from datetime import timedelta
from .models import Ticket, Categoria, Subcategoria
import threading
from django.conf import settings


import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def api_tickets(request):
    tickets = Ticket.objects.all().values(
        'id',
        'estado',
        'prioridad',
        'fecha_creacion',
        'fecha_cierre',
        'sede__nombre',
        'categoria__nombre'
    )
    return JsonResponse(list(tickets), safe=False)
    
def es_admin(user):
    return user.is_staff

@user_passes_test(es_admin)
def dashboard(request):
    perfil = getattr(request.user, 'perfil', None)
    
    # 🔐 CONTROL DE ACCESO
    if request.user.is_staff:
        tickets = Ticket.objects.all()  # ADMIN ve todo
    else:
        if not perfil:
            return redirect('login')
        tickets = Ticket.objects.filter(sede=perfil.sede)  # Usuario solo su sede
    
    # 📊 KPIs
    total_tickets = tickets.count()
    abiertos = tickets.filter(estado='abierto').count()
    en_proceso = tickets.filter(estado='en_proceso').count()
    cerrados = tickets.filter(estado='cerrado').count()
    
    
    from django.utils import timezone
    from datetime import timedelta
    
    # ⏱️ SLA (24 horas)
    cumple_sla = 0
    no_cumple = 0

    for t in tickets.filter(estado='cerrado'):
        if t.fecha_cierre and t.fecha_creacion:
            tiempo = t.fecha_cierre - t.fecha_creacion

            if tiempo <= timedelta(hours=24):
                cumple_sla += 1
            else:
                no_cumple += 1

    return render(request, 'tickets/dashboard.html', {
        'total_tickets': total_tickets,
        'abiertos': abiertos,
        'en_proceso': en_proceso,
        'cerrados': cerrados,
        'cumple_sla': cumple_sla,
        'no_cumple': no_cumple,
    })
        
@login_required
def lista_tickets(request):
    perfil, created = Perfil.objects.get_or_create(user=request.user)
    
    tickets = Ticket.objects.filter(sede=perfil.sede).order_by('-fecha_creacion')

    return render(request, 'tickets/lista.html', {'tickets': tickets})
    
from .models import Ticket, Sede, Categoria, Subcategoria

@login_required
def crear_ticket(request):

    if request.method == 'POST':

        categoria = Categoria.objects.get(id=request.POST.get('categoria'))

        # 🎯 prioridad automática
        if categoria.nombre.lower() == 'hardware':
            prioridad = 'P2'
        elif categoria.nombre.lower() == 'red':
            prioridad = 'P1'
        elif categoria.nombre.lower() == 'usuario':
            prioridad = 'P3'
        else:
            prioridad = 'P4'

        perfil = request.user.perfil
        sede = perfil.sede  # ✅ DEFINIDO ANTES

        # ✅ GUARDAR EN VARIABLE
        ticket = Ticket.objects.create(
            usuario=request.user,
            sede=sede,
            categoria=categoria,
            subcategoria_id=int(request.POST.get('subcategoria')),
            descripcion=request.POST.get('descripcion'),
            impacto=impacto,
            urgencia=urgencia,
            prioridad=prioridad,
            archivo=archivo
        )

        def enviar_correo():
            try:
                message = Mail(
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to_emails=[
                        'emontenegro@100montaditosca.com',
                        sede.correo
                    ],
                    subject=f'Nuevo Ticket #{ticket.id}',
                    plain_text_content=(
                        f'Se ha creado un ticket:\n\n'
                        f'Usuario: {request.user.username}\n'
                        f'Sede: {sede.nombre}\n'
                        f'Descripción: {ticket.descripcion}\n'
                        f'Prioridad: {prioridad}'
                    )
                )

                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                print("CORREO ENVIADO:", response.status_code)

            except Exception as e:
                print("ERROR SENDGRID:", e)
                
        threading.Thread(target=enviar_correo).start()        

        return redirect('lista_tickets')

# ✅ IMPORTANTE: respuesta GET
    categorias = Categoria.objects.all()
    subcategorias = Subcategoria.objects.all()

    return render(request, 'tickets/crear.html', {
        'categorias': categorias,
        'subcategorias': subcategorias
    })
    
@login_required
def cerrar_ticket(request, id):
    ticket = Ticket.objects.get(id=id)

    if ticket.estado == 'cerrado':
        return redirect('lista_tickets')
        
    # Cambiar estado
    ticket.estado = 'cerrado'
    ticket.fecha_cierre = timezone.now()
    ticket.save()

    def enviar_correo_cierre():
        try:
            message = Mail(
                from_email=settings.DEFAULT_FROM_EMAIL,
                to_emails=[
                    'emontenegro@100montaditosca.com',
                    ticket.sede.correo
                ],
                subject=f'✅ Ticket #{ticket.id} CERRADO',
                plain_text_content=(
                    f'📌 Ticket #{ticket.id} cerrado exitosamente\n\n'
                    f'👤 Usuario: {ticket.usuario.username}\n'
                    f'🏢 Sede: {ticket.sede.nombre}\n'
                    f'🛠️ Descripción: {ticket.descripcion}\n'
                    f'📅 Fecha cierre: {ticket.fecha_cierre}\n\n'
                    f'🧾 Solución: Ticket atendido correctamente\n\n'
                    f'🙏 Gracias por utilizar la mesa de ayuda'
                )
            )

            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print("CORREO CIERRE:", response.status_code)

        except Exception as e:
            print("ERROR CIERRE:", e)
    
    # Enviar en segundo plano
    threading.Thread(target=enviar_correo_cierre).start()
    
    return redirect('lista_tickets')

    categorias = Categoria.objects.all()
    subcategorias = Subcategoria.objects.all()

    return render(request, 'tickets/crear.html', {
        'categorias': categorias,
        'subcategorias': subcategorias
    })
    
    # ESTO ES LO NUEVO
    sedes = Sede.objects.all()
    categorias = Categoria.objects.all()
    subcategorias = Subcategoria.objects.all()

    return render(request, 'tickets/crear.html', {
        'sedes': sedes,
        'categorias': categorias,
        'subcategorias': subcategorias
    })

def crear_admin(request):
    User.objects.filter(username='admin').delete()
    User.objects.create_superuser('admin', 'admin@test.com', 'Admin12345')
    return HttpResponse("Admin creado")
    
def cargar_subcategorias(request):
    categoria_id = request.GET.get('categoria_id')
    subcategorias = Subcategoria.objects.filter(categoria_id=categoria_id)

    data = list(subcategorias.values('id', 'nombre'))
    return JsonResponse(data, safe=False)
    
# Create your views here.
