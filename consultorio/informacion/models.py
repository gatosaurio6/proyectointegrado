from django.db import models
from django.contrib.auth.models import Group, User
from django.core.validators import FileExtensionValidator


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
    
#Modelo de Areas    
class Area(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    jefe = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='jefatura_area',
        limit_choices_to={'groups__name': 'Jefatura'}
    )

    def __str__(self):
        return self.nombre

#Modelo de perfil de usuario 
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

#Modelo para la solicitud de dias libres
class SolicitudDiaLibre(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_creadas')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, editable=False, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    gestionado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='solicitudes_gestionadas'
    )
    fecha_gestion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Solicitud de {self.solicitante.username} ({self.estado})"
    

#modelo para subir documento
class Documento(models.Model):
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(
        upload_to='documentos/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx'])]
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
