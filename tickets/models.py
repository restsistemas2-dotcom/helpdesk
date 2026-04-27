from django.db import models
from django.contrib.auth.models import User
   
# Sedes
class Sede(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150, blank=True)
    correo = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# Perfil
class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username

# Categorías
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


# Subcategorías
class Subcategoria(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.categoria} - {self.nombre}"


# Tickets
class Ticket(models.Model):

    ESTADOS = [
        ('abierto', 'Abierto'),
        ('progreso', 'En Progreso'),
        ('cerrado', 'Cerrado'),
    ]

    IMPACTO = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
    ]

    URGENCIA = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    sede = models.ForeignKey(Sede, on_delete=models.CASCADE)

    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.SET_NULL, null=True)

    descripcion = models.TextField()

    prioridad = models.CharField(max_length=2, default="P3")
    
    estado = models.CharField(max_length=20, choices=ESTADOS, default='abierto')

    impacto = models.CharField(max_length=10, choices=IMPACTO, null=True, blank=True)
    urgencia = models.CharField(max_length=10, choices=URGENCIA, null=True, blank=True)

    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tickets_asignados')

    archivo = models.FileField(upload_to='tickets/', null=True, blank=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    
    solucion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.estado}"

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import User
       
@receiver(post_save, sender=Ticket)
def enviar_correo_cierre(sender, instance, created, **kwargs):
    
    # solo cuando se actualiza
    if not created and instance.estado == 'cerrado':
        
        # si no tiene fecha, la agregamos SIN usar save()
        if not instance.fecha_cierre:
            Ticket.objects.filter(id=instance.id).update(
                fecha_cierre=timezone.now()
            )
            instance.fecha_cierre = timezone.now()
                  
            destinatarios = []

            if instance.usuario.email:
                destinatarios.append(instance.usuario.email)

            if instance.sede.correo:
                destinatarios.append(instance.sede.correo)
          
            if destinatarios:
                send_mail(
                    f'Ticket #{instance.id} Cerrado',
                    f'Hola,\n\n'
                    f'Tu ticket ha sido cerrado exitosamente.\n\n'
                    f'🆔 ID: {instance.id}\n'
                    f'🏢 Sede: {instance.sede.nombre}\n'
                    f'📅 Fecha de cierre: {instance.fecha_cierre.strftime("%d/%m/%Y %H:%M")}\n\n'
                    f'🛠️ Solución:\n{instance.solucion or "No especificada"}\n\n'
                    f'Gracias por utilizar la mesa de ayuda.',
                    'emontenegro@100montaditosca.com',
                    destinatarios,
                    fail_silently=False,
                )
# Create your models here.
