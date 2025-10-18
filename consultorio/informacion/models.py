from django.db import models
from django.contrib.auth.models import Group


#Modelos para los usuarios del sistema
class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    ROL_CHOICES = [
        ('Empleado', 'Empleado'),
        ('Subdirector', 'Subdirector'),
        ('Director', 'Director'),
    ]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='Empleado')

    def __str__(self):
        return f"{self.nombre} - {self.rol}"
    


#Modelos para los eventos del calendario
class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(blank=True, null=True)
    roles_permitidos = models.ManyToManyField(Group, blank=True)

    def __str__(self):
        return self.titulo
    
