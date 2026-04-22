from django.shortcuts import render, redirect
from .models import Ticket
from django.contrib.auth.decorators import login_required

@login_required
def lista_tickets(request):
    tickets = Ticket.objects.all().order_by('-fecha_creacion')
    return render(request, 'tickets/lista.html', {'tickets': tickets})

from .models import Ticket, Sede, Categoria, Subcategoria

@login_required
def crear_ticket(request):
    
    if request.method == 'POST':
        
        categoria_id = request.POST.get('categoria')

        # Lógica automática (puedes mejorarla después)
        if categoria_id == '1':  # Hardware
            impacto = 'bajo'
            urgencia = 'media'
        else:
            impacto = 'alto'
            urgencia = 'alta'
        
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
            prioridad=prioridad,
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

# Create your views here.
