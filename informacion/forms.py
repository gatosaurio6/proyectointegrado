from django import forms
from .models import Documento, SolicitudDiaLibre, SolicitudVacaciones, LicenciaMedica, PerfilUsuario, Anuncio, Evento, ReporteProblema
from django.contrib.auth.models import User



# Formulario para Documentos
class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['titulo', 'descripcion', 'archivo', 'importante']

# Formulario para Solicitudes de Dias Libres
class DateInput(forms.DateInput):
    """Clase auxiliar para que el campo de fecha use el tipo 'date' de HTML5."""
    input_type = 'date'

class SolicitudDiaLibreForm(forms.ModelForm):
    class Meta:
        model = SolicitudDiaLibre
        fields = ['fecha_inicio', 'fecha_fin', 'motivo', 'archivo_adjunto']
        widgets = {
            'fecha_inicio': DateInput(),
            'fecha_fin': DateInput(),
            'motivo': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'archivo_adjunto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Término',
            'motivo': 'Motivo',
            'archivo_adjunto': 'Adjuntar Justificativo (Si corresponde)',
        }
class SolicitudVacacionesForm(forms.ModelForm):
    class Meta:
        model = SolicitudVacaciones
        fields = ['fecha_inicio', 'fecha_fin', 'motivo', 'archivo_adjunto']
        widgets = {
            'fecha_inicio': DateInput(),
            'fecha_fin': DateInput(),
            'motivo': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'archivo_adjunto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_fin': 'Fecha de Término',
            'motivo': 'Motivo',
            'archivo_adjunto': 'Adjuntar Justificativo (Si corresponde)',
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
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, label='Nombre', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, label='Apellido', widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserCreateForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, label='Nombre', widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, label='Apellido', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Contraseña Inicial')
    

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PerfilUpdateForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['rut', 'area']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678-9'}),
            'area': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'rut': 'RUT (Con guion, sin puntos)'
        }
    
#crear y asignar area
from django.contrib.auth.models import Group
from .models import Area

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre', 'jefe']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'jefe': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre del Área',
            'jefe': 'Jefe Encargado (Debe ser del grupo Jefatura)'
        }

class AsignarRolForm(forms.Form):
    usuario = forms.ModelChoiceField(queryset=User.objects.all(), label="Seleccionar Usuario", widget=forms.Select(attrs={'class': 'form-control'}))
    rol = forms.ModelChoiceField(queryset=Group.objects.all(), label="Seleccionar Nuevo Rol", widget=forms.Select(attrs={'class': 'form-control'}))

#crear anuncios
class AnuncioForm(forms.ModelForm):
    class Meta:
        model = Anuncio
        fields = ['titulo', 'contenido', 'importante']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'importante': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

#crear eventos calendario
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'roles_permitidos']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'roles_permitidos': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}) 
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
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Breve descripción del problema'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Oficina 302, Baño de visitas...'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describa brevemente qué sucede...'}),
        }