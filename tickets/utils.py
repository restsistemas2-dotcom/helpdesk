from django.core.mail import send_mail
from django.conf import settings

def enviar_correo_ticket(ticket, destinatarios, tipo):
    try:
        if tipo == 'creado':
            subject = f'🎫 Ticket #{ticket.id} CREADO'
            message = f'''
Hola,

Se ha creado un nuevo ticket.

ID: {ticket.id}
Sede: {ticket.sede}
Descripción:
{ticket.descripcion}
'''
        elif tipo == 'cerrado':
            subject = f'✅ Ticket #{ticket.id} CERRADO'
            message = f'''
Hola,

Tu ticket ha sido cerrado.

ID: {ticket.id}
Sede: {ticket.sede}
Fecha cierre: {ticket.fecha_cierre}

Solución:
{ticket.solucion or "Ticket atendido correctamente."}
'''
        else:
            return
        
        print("FROM:", settings.DEFAULT_FROM_EMAIL)
        print("DESTINATARIOS:", destinatarios)
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            destinatarios,
            fail_silently=False,
        )

        print(f"✅ Correo enviado a: {destinatarios}")

    except Exception as e:
        print("❌ ERROR CORREO:", e)