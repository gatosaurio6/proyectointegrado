from django.contrib import admin
from .models import Evento, Area, PerfilUsuario, SolicitudDiaLibre, Documento
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User


# Register your models here.

admin.site.site_header = "Administración CESFAM"
admin.site.site_title = "Portal de Administración"
admin.site.index_title = "Bienvenido al Panel de Gestión"


class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin')
    filter_horizontal = ('roles_permitidos',)


#------------

class DocumentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'archivo', 'fecha_subida')
    search_fields = ('titulo', 'descripcion')
    list_filter = ('fecha_subida',)

class UserAdmin(BaseUserAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            if request.user.groups.filter(name='Direccion').exists():
                qs = qs.exclude(groups__name='Subdireccion')
            elif request.user.groups.filter(name='Subdireccion').exists():
                qs = qs.exclude(groups__name='Direccion')
        return qs


admin.site.register(Documento, DocumentoAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Area)
admin.site.register(PerfilUsuario)
admin.site.register(SolicitudDiaLibre)
admin.site.register(Evento, EventoAdmin)