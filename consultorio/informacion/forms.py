from django import forms
from .models import Documento, SolicitudDiaLibre

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