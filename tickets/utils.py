from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


def enviar_correo_ticket(ticket, destinatarios, tipo):

    try:

        # ✅ VALIDAR + LIMPIAR CORREOS
        destinatarios_validos = []

        for correo in destinatarios:

            if correo:

                correo = correo.strip()

                try:
                    validate_email(correo)
                    destinatarios_validos.append(correo)

                except ValidationError:
                    print(f"❌ Correo inválido ignorado: {correo}")

        # ✅ ELIMINAR DUPLICADOS
        destinatarios_validos = list(set(destinatarios_validos))

        if not destinatarios_validos:
            print("❌ No hay destinatarios válidos")
            return

        # ✅ MENSAJES
        if tipo == 'creado':

            subject = f'🎫 Ticket #{ticket.id} CREADO'

            message = f'''
Hola,

Se ha creado un nuevo ticket.

━━━━━━━━━━━━━━━━━━
🎫 Ticket: #{ticket.id}
🏢 Sede: {ticket.sede}
📂 Categoría: {ticket.categoria}
📝 Descripción:
{ticket.descripcion}
━━━━━━━━━━━━━━━━━━

Departamento IT
'''

        elif tipo == 'cerrado':

            subject = f'✅ Ticket #{ticket.id} CERRADO'

            message = f'''
Hola,

Tu ticket ha sido cerrado.

━━━━━━━━━━━━━━━━━━
🎫 Ticket: #{ticket.id}
🏢 Sede: {ticket.sede}
📅 Fecha cierre: {ticket.fecha_cierre.strftime("%d/%m/%Y %I:%M %p")}
━━━━━━━━━━━━━━━━━━


🛠️ Solución:
{ticket.solucion or "Ticket atendido correctamente."}

Gracias.
Departamento IT
'''

        else:
            return

        print("FROM:", settings.DEFAULT_FROM_EMAIL)
        print("DESTINATARIOS:", destinatarios_validos)

        # ✅ ENVÍO
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            destinatarios_validos,
            fail_silently=False,
        )

        print(f"✅ Correo enviado a: {destinatarios_validos}")

    except Exception as e:
        print("❌ ERROR CORREO:", e)