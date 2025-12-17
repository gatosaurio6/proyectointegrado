from django.contrib import admin
from .models import Evento, Area, PerfilUsuario, SolicitudDiaLibre, Documento, SolicitudVacaciones, LicenciaMedica
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

# This file no longer customizes AdminSite behavior directly as the admin URL is being removed.
# You can uncomment and re-enable custom_admin_site if you decide to re-introduce the admin later.

# from django.urls import reverse
# from django.http import HttpResponseRedirect
# from django.utils.translation import gettext as _
# from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.admin.sites import AdminSite 

# class CustomAdminSite(admin.AdminSite):
#     def get_urls(self):
#         # Import path locally to avoid potential circular imports if admin.py is imported early.
#         from django.urls import path
#         urls = super().get_urls()
#         # Prepend our custom login URL pattern to ensure it's matched before the default admin login.
#         my_urls = [
#             path('login/', self.custom_admin_login, name='login'),
#         ]
#         return my_urls + urls

#     def custom_admin_login(self, request, extra_context=None):
#         # Call the original admin login view. This handles authentication and sets request.user.
#         response = super().login(request, extra_context)
        
#         # After super().login executes, request.user will be the authenticated user
#         # if the login was successful.
#         if request.user.is_authenticated and request.user.is_staff and not request.user.is_superuser:
#             # If the user is an authenticated staff member but NOT a superuser,
#             # redirect them to the 'inicio' page. This overrides the default
#             # redirect to '/admin/' that super().login might have set.
#             return HttpResponseRedirect(reverse('inicio'))
        
#         # Otherwise (if login failed, or user is not staff, or user is superuser),
#         # return the original response from super().login.
#         return response

#     def index(self, request, extra_context=None):
#         # This method is called if the user lands on the admin index page (e.g., by typing the URL directly).
#         # If they are an authenticated staff member but NOT a superuser, redirect them away to 'inicio'.
#         if request.user.is_authenticated and request.user.is_staff and not request.user.is_superuser:
#             return HttpResponseRedirect(reverse('inicio'))
        
#         # For superusers, or if the user has been redirected, this part won't be reached.
#         # This section adds context for the original admin index page, which superusers will still see.
#         extra_context = extra_context or {}
#         extra_context['total_solicitudes_dia_libre'] = SolicitudDiaLibre.objects.count()
#         extra_context['total_solicitudes_vacaciones'] = SolicitudVacaciones.objects.count()
#         extra_context['total_licencias_medicas'] = LicenciaMedica.objects.count()
#         return super().index(request, extra_context=extra_context)

# custom_admin_site = CustomAdminSite(name='custom_admin')

# Register your models here.
# For now, we will register models with the default admin site, which is not exposed.
# If you re-introduce a custom admin site, you'll need to register with that site instead.

# custom_admin_site.site_header = "Administración CESFAM"
# custom_admin_site.site_title = "Portal de Administración"
# custom_admin_site.index_title = "Bienvenido al Panel de Gestión"


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

# Unregister the default UserAdmin and then register our custom UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


admin.site.register(Documento, DocumentoAdmin)
admin.site.register(Area)
admin.site.register(PerfilUsuario)
admin.site.register(SolicitudDiaLibre, SolicitudAdmin)
admin.site.register(SolicitudVacaciones, SolicitudAdmin)
admin.site.register(LicenciaMedica, LicenciaAdmin)
admin.site.register(Evento, EventoAdmin)