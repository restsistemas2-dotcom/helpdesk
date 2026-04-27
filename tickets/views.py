from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Ticket
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .models import Subcategoria


def es_admin(user):
    return user.is_staff
    
@login_required
def lista_tickets(request):
    perfil = request.user.perfil
    tickets = Ticket.objects.filter(sede=perfil.sede).order_by('-fecha_creacion')

    return render(request, 'tickets/lista.html', {'tickets': tickets})
    
from .models import Ticket, Sede, Categoria, Subcategoria

@login_required
def crear_ticket(request):
    
    if request.method == 'POST':
        
        categoria_id = request.POST.get('categoria')
        
        impacto = (request.POST.get('impacto') or '').lower()
        urgencia = (request.POST.get('urgencia') or '').lower()

        # Prioridad tipo ITIL
        if impacto == 'alto' and urgencia == 'alta':
            prioridad = 'P1'
        elif impacto == 'alto' and urgencia == 'media':
            prioridad = 'P2'
        elif impacto == 'medio' and urgencia == 'alta':
            prioridad = 'P2'
        elif impacto == 'medio' and urgencia == 'media':
            prioridad = 'P3'
        else:
            prioridad = 'P4'
        
        perfil = request.user.perfil
        
        Ticket.objects.create(
            usuario=request.user,
            sede=perfil.sede,
            categoria_id=int(categoria_id),
            subcategoria_id=int(request.POST.get('subcategoria')),
            descripcion=request.POST.get('descripcion'),
            impacto=impacto,
            urgencia=urgencia,
            prioridad=prioridad,
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

    return render(request, 'tickets/crear.html', {
        'categorias': categorias,
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
