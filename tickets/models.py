from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import EmailValidator

  
# Sedes
class Sede(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150, blank=True)
    
    correo = models.EmailField(
        blank=True,
        null=True,
        validators=[EmailValidator(message="Ingrese un correo válido")]
    )

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
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.categoria} - {self.nombre}"


# Tickets
class Ticket(models.Model):

    ESTADOS = [
        ('abierto', 'Abierto'),
        ('en_proceso', 'En Progreso'),
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
from django.utils import timezone
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)   
# Create your models here.
