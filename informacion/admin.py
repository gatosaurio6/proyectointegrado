from django.contrib import admin
from .models import Evento, Area, PerfilUsuario, SolicitudDiaLibre, Documento, SolicitudVacaciones, LicenciaMedica
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['total_solicitudes_dia_libre'] = SolicitudDiaLibre.objects.count()
        extra_context['total_solicitudes_vacaciones'] = SolicitudVacaciones.objects.count()
        extra_context['total_licencias_medicas'] = LicenciaMedica.objects.count()
        return super().index(request, extra_context=extra_context)

custom_admin_site = CustomAdminSite(name='custom_admin')

# Register your models here.

custom_admin_site.site_header = "Administración CESFAM"
custom_admin_site.site_title = "Portal de Administración"
custom_admin_site.index_title = "Bienvenido al Panel de Gestión"


class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin')
    filter_horizontal = ('roles_permitidos',)


#------------

class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'archivo', 'fecha_subida')
    search_fields = ('titulo', 'descripcion')
    list_filter = ('fecha_subida',)

class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('solicitante', 'area', 'fecha_inicio', 'fecha_fin', 'estado')
    list_filter = ('estado', 'area')
    search_fields = ('solicitante__username', 'motivo')

class LicenciaAdmin(admin.ModelAdmin):
    list_display = ('solicitante', 'area', 'fecha_inicio', 'fecha_fin', 'estado')
    list_filter = ('estado', 'area')
    search_fields = ('solicitante__username', 'motivo')

class UserAdmin(BaseUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        if obj is None:
            return True
        if request.user.groups.filter(name = 'Direccion').exists():
            return True
        if request.user.groups.filter(name__in = ['Subdireccion Administrativa', 'Subdireccion Clinica']).exists():
            if obj.groups.filter(name = 'Direccion').exists():
                return False
            return True
        if request.user.groups.filter(name = 'Jefatura').exists():
            if obj.groups.filter(name__in = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica', 'Jefatura']).exists():
                return False
            return True
        return False


custom_admin_site.register(Documento, DocumentoAdmin)
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Area)
custom_admin_site.register(PerfilUsuario)
custom_admin_site.register(SolicitudDiaLibre, SolicitudAdmin)
custom_admin_site.register(SolicitudVacaciones, SolicitudAdmin)
custom_admin_site.register(LicenciaMedica, LicenciaAdmin)
custom_admin_site.register(Evento, EventoAdmin)