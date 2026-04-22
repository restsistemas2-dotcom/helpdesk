from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Ticket
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail


@login_required
def lista_tickets(request):
    tickets = Ticket.objects.all().order_by('-fecha_creacion')
    return render(request, 'tickets/lista.html', {'tickets': tickets})

from .models import Ticket, Sede, Categoria, Subcategoria

@login_required
def crear_ticket(request):
    
    if request.method == 'POST':
        
        categoria_id = request.POST.get('categoria')
        
        # TOMAR DATOS DEL FORMULARIO
        impacto = request.POST.get('impacto')
        urgencia = request.POST.get('urgencia')

        impacto = impacto.lower()
        urgencia = urgencia.lower()
    
        # (OPCIONAL) lógica por categoría
        if categoria_id == '1':
            pass  # o alguna regla especial
            
        print("Impacto recibido:", impacto)
        print("Urgencia recibida:", urgencia)
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

        Ticket.objects.create(
            usuario=request.user,
            sede_id=int(request.POST.get('sede')),
            categoria_id=int(categoria_id),
            subcategoria_id=int(request.POST.get('subcategoria')),
            descripcion=request.POST.get('descripcion'),
            impacto=impacto,
            urgencia=urgencia,
            prioridad=prioridad.upper(),
        )
        
        # 2. Obtener la sede
        sede = Sede.objects.get(id=request.POST.get('sede'))

        # 3. Enviar correo
        send_mail(
            'Nuevo Ticket Creado',
            f'Se ha creado un ticket:\n\n'
            f'Usuario: {request.user.username}\n'
            f'Sede: {sede.nombre}\n'
            f'Descripción: {request.POST.get("descripcion")}\n'
            f'Prioridad: {prioridad}',
            'emontenegro@100montaditosca.com',
            ['emontenegro@100montaditosca.com', sede.correo],
            fail_silently=False,
        )
        return redirect('lista_tickets')
    

   
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
    return HttpResponse("OK FUNCIONANDO")

# Create your views here.
