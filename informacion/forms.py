from django import forms
from .models import Documento, SolicitudDiaLibre, SolicitudVacaciones, LicenciaMedica, PerfilUsuario, Anuncio, Evento, ReporteProblema
from django.contrib.auth.models import User



# Formulario para Documentos
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'descripcion', 'archivo']

# Formulario para Solicitudes de Dias Libres
class DateInput(forms.DateInput):
    """Clase auxiliar para que el campo de fecha use el tipo 'date' de HTML5."""
    input_type = 'date'

class SolicitudDiaLibreForm(forms.ModelForm):
    class Meta:
        model = SolicitudDiaLibre
        fields = ['fecha_inicio', 'fecha_fin', 'motivo']
        widgets = {
            'fecha_inicio': DateInput(),
            'fecha_fin': DateInput(),
            'motivo': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe un breve motivo...'}),
        }
        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Término',
            'motivo': 'Motivo de la solicitud',
        }

# Formulario para Solicitudes de Vacaciones
class SolicitudVacacionesForm(forms.ModelForm):
    class Meta:
        model = SolicitudVacaciones
        fields = ['fecha_inicio', 'fecha_fin', 'motivo']
        widgets = {
            'fecha_inicio': DateInput(),
            'fecha_fin': DateInput(),
            'motivo': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe un breve motivo para tus vacaciones...'}),
        }
        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Término',
            'motivo': 'Motivo de la solicitud',
        }

# Formulario para Licencias Medicas
class LicenciaMedicaForm(forms.ModelForm):
    class Meta:
        model = LicenciaMedica
        fields = ['fecha_inicio', 'fecha_fin', 'motivo', 'certificado']
        widgets = {
            'fecha_inicio': DateInput(),
            'fecha_fin': DateInput(),
            'motivo': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe el motivo de tu licencia...'}),
        }
        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Término',
            'motivo': 'Motivo de la licencia',
            'certificado': 'Certificado Médico',
        }

#para el crud
#registrar y actualizar usuario *CRUD*

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class UserCreateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, label='Nombre')
    last_name = forms.CharField(max_length=30, label='Apellido')
    password = forms.CharField(widget=forms.PasswordInput, label='Contraseña Inicial') 

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['area']
    
#crear y asignar area
from django.contrib.auth.models import Group
from .models import Area

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre', 'jefe']
        labels = {
            'nombre': 'Nombre del Área',
            'jefe': 'Jefe Encargado (Debe ser del grupo Jefatura)'
        }

class AsignarRolForm(forms.Form):
    usuario = forms.ModelChoiceField(queryset=User.objects.all(), label="Seleccionar Usuario")
    rol = forms.ModelChoiceField(queryset=Group.objects.all(), label="Seleccionar Nuevo Rol")

#crear anuncios
class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        fields = ['titulo', 'contenido', 'importante']
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 4}),
        }

#crear eventos calendario
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'roles_permitidos']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'roles_permitidos': forms.CheckboxSelectMultiple() 
        }
        labels = {
            'fecha_inicio': 'Inicio (DD/MM/AAAA HH:MM)',
            'fecha_fin': 'Fin (Opcional)'
        }

#formulario para reportar algun problema en el edificio
class ReporteProblemaForm(forms.ModelForm):
    class Meta:
        model = ReporteProblema
        fields = ['titulo', 'lugar', 'prioridad', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describa brevemente qué sucede...'}),
            'lugar': forms.TextInput(attrs={'placeholder': 'Ej: Oficina 302, Baño de visitas...'}),
        }