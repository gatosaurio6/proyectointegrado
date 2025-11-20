from django.db import models
from django.contrib.auth.models import Group, User
from django.core.validators import FileExtensionValidator, MinLengthValidator, RegexValidator

def val_nombres():
    return RegexValidator(
        regex=r"^[a-zA-ZñÑáÁéÉíÍóÓúÚ\s\-']+$",
        message = "El nombre solo puede contener letras, espacios, guiones y apóstrofes"
    )

def val_telefono():
    return RegexValidator(
        regex=r'^\+?56\d{8}$', 
        message='El teléfono debe tener formato 569xxxxxxxx o +569xxxxxxxx'
    )

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
    nombre = models.CharField(max_length=100, unique=True,validators = [val_nombres()])
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
    rut = models.CharField(max_length = 10, validators= [MinLengthValidator(10), RegexValidator(r'^\d{10}$', 'El RUT debe tener 10 números incluyendo guión')])
    telefono = models.CharField(max_length = 12, validators= [MinLengthValidator(8), val_telefono])
    cargo = models.CharField(max_length = 100, validators= [MinLengthValidator(5)], blank = False, null = False)
    dias_libres = models.IntegerField(default = 0)
    dias_vacaciones = models.IntegerField(default = 0)
    dias_licencia = models.IntegerField(default = 0)

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
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

#Modelo para la solicitud de vacaciones
class SolicitudVacaciones(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_vacaciones')
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
        related_name='vacaciones_gestionadas'
    )
    fecha_gestion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Solicitud de vacaciones de {self.solicitante.username} ({self.estado})"

#Modelo para la licencia medica
class LicenciaMedica(models.Model):
    ESTADOS = [
        ('en revision', 'En revisión'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='licencias_medicas')
    area = models.ForeignKey(Area, on_delete=models.CASCADE, editable=False, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()
    certificado = models.FileField(upload_to='licencias/', validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'png', 'web'])])
    estado = models.CharField(max_length=15, choices=ESTADOS, default='en revision')
    gestionado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='licencias_gestionadas'
    )
    fecha_gestion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Licencia médica de {self.solicitante.username} ({self.estado})"


#Modelo de anuncios

class Anuncio(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    importante = models.BooleanField(default=False, verbose_name="¿Es Importante?")
    
    def __str__(self):
        return self.titulo
    
#modelo de reportar problemas

class ReporteProblema(models.Model):
    PRIORIDADES = [
        ('baja', 'Baja (Se puede esperar)'),
        ('media', 'Media (Necesita atención)'),
        ('alta', 'Alta (Urgente / Peligroso)'),
    ]
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
    ]

    titulo = models.CharField(max_length=200, verbose_name="¿Cuál es el problema?")
    descripcion = models.TextField(verbose_name="Detalles del problema")
    lugar = models.CharField(max_length=100, verbose_name="Lugar exacto (Ej: Baño Piso 1)")
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES, default='media')
    
    solicitante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reportes')
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    
    estado = models.CharField(max_length=15, choices=ESTADOS, default='pendiente')
    
    def __str__(self):
        return f"{self.titulo} ({self.estado})"