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

from .models import Ticket

def es_admin(user):
    return user.is_staff

@user_passes_test(es_admin)
def dashboard(request):
    perfil = getattr(request.user, 'perfil', None)

    if not perfil:
        return redirect('login')

    tickets = Ticket.objects.filter(sede=perfil.sede)

    total_tickets = tickets.count()
    abiertos = tickets.filter(estado='abierto').count()
    cerrados = tickets.filter(estado='cerrado').count()
    en_proceso = tickets.filter(estado='en_proceso').count()
    
    tickets_cerrados = tickets.filter(
        estado='cerrado',
        fecha_cierre__isnull=False
    )

    tickets_con_tiempo = tickets_cerrados.annotate(
        tiempo_resolucion=ExpressionWrapper(
            F('fecha_cierre') - F('fecha_creacion'),
            output_field=DurationField()
        )
    )

    cumple_sla = tickets_con_tiempo.filter(
        tiempo_resolucion__lte=timedelta(hours=24)
    ).count()

    no_cumple = tickets_con_tiempo.filter(
        tiempo_resolucion__gt=timedelta(hours=24)
    ).count()

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

        impacto = 'alto'
        urgencia = 'alta'
        
        perfil = request.user.perfil

        # 📎 archivo
        archivo = request.FILES.get('archivo')

        Ticket.objects.create(
            usuario=request.user,
            sede=perfil.sede,
            categoria=categoria,
            subcategoria_id=int(request.POST.get('subcategoria')),
            descripcion=request.POST.get('descripcion'),
            impacto=impacto,
            urgencia=urgencia,
            prioridad=prioridad,
            archivo=archivo
        )
        
        sede = perfil.sede

        send_mail(
            'Nuevo Ticket Creado',
            f'Se ha creado un ticket:\n\n'
            f'Usuario: {request.user.username}\n'
            f'🏢 Sede: {sede.nombre}\n'
            f'Descripción: {request.POST.get("descripcion")}\n'
            f'Prioridad: {prioridad}',
            'emontenegro@100montaditosca.com',
            ['emontenegro@100montaditosca.com', sede.correo],
            fail_silently=False,
        )

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
