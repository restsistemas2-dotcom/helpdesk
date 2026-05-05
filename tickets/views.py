from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import JsonResponse
from .models import Ticket
from django.db.models import Count
from django.core.mail import send_mail
from django.contrib.auth.decorators import user_passes_test
from .models import Subcategoria
from .models import Categoria
from .models import Perfil
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import F, ExpressionWrapper, DurationField
from .models import Ticket, Categoria, Subcategoria
import threading
from django.conf import settings
from django.shortcuts import get_object_or_404

def enviar_correo_ticket(ticket, destinatarios, tipo='creado'):
    try:
        if tipo == 'creado':
            subject = f'🎫 Ticket #{ticket.id} creado'
            mensaje = f'''
Hola,

Tu ticket ha sido creado correctamente.

🆔 ID: {ticket.id}
🏢 Sede: {ticket.sede}
📌 Estado: {ticket.estado}

Gracias por utilizar la mesa de ayuda.
'''
        else:
            subject = f'✅ Ticket #{ticket.id} CERRADO'
            mensaje = f'''
Hola,

Tu ticket ha sido cerrado.

🆔 ID: {ticket.id}
🏢 Sede: {ticket.sede}
📅 Fecha cierre: {ticket.fecha_cierre}

🛠️ Solución:
{instance.solucion or "Ticket atendido correctamente."}

Gracias por utilizar la mesa de ayuda.
'''

        send_mail(
            subject,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            destinatarios,
            fail_silently=False,
        )

        print("✅ Correo enviado")

    except Exception as e:
        print("❌ ERROR CORREO:", e)

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

    cerrados_qs = tickets.filter(estado='cerrado')
    
    for t in cerrados_qs:
        if t.fecha_cierre and t.fecha_creacion:
            tiempo = t.fecha_cierre - t.fecha_creacion

            if tiempo <= timedelta(hours=24):
                cumple_sla += 1
            else:
                no_cumple += 1

    # 📊 AGRUPACIÓN POR PRIORIDAD (esto te faltaba)
    por_prioridad = tickets.values('prioridad').annotate(total=Count('id'))

    # 🧪 DEBUG (esto sí va fuera del render)
    print("TOTAL:", total_tickets)
    print("CERRADOS:", cerrados)
    print("SLA OK:", cumple_sla)
    print("SLA FAIL:", no_cumple)

    return render(request, 'tickets/dashboard.html', {
        'total': total_tickets,
        'total_tickets': total_tickets,
        'abiertos': abiertos,
        'en_proceso': en_proceso,
        'cerrados': cerrados,
        'cumple_sla': cumple_sla,
        'no_cumple': no_cumple,
        'por_prioridad': por_prioridad
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
        archivo = request.FILES.get('archivo')
        
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
        
        # 👇 DESTINATARIOS
        destinatarios = [
            ticket.sede.correo,
            'emontenegro@100montaditosca.com'
        ]
        destinatarios = [d for d in destinatarios if d]
        
        # 👇 THREAD CORRECTO
        import threading
        threading.Thread(
            target=enviar_correo_ticket,
            args=(ticket, destinatarios, 'creado')
        ).start()

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
    ticket = get_object_or_404(Ticket, id=id)
    
     # 🔐 SOLO ADMIN
    if not request.user.is_staff:
        return redirect('lista_tickets')
        
    if ticket.estado == 'cerrado':
        return redirect('lista_tickets')
        
    # Cambiar estado
    ticket.estado = 'cerrado'
    ticket.fecha_cierre.strftime("%d/%m/%Y %H:%M")
    ticket.save()

    # 📧 DESTINATARIOS SEGUROS
    destinatarios = []

    if ticket.sede.correo:
        destinatarios.append(ticket.sede.correo)

    destinatarios.append('emontenegro@100montaditosca.com')

    import threading
    threading.Thread(
        target=enviar_correo_ticket,
        args=(ticket, destinatarios, 'cerrado')
    ).start()

    return redirect('lista_tickets')
  
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
