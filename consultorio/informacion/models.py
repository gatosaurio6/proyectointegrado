from django.db import models



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
    
