from django.contrib import admin
from .models import Evento



# Register your models here.

class EventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin')
    filter_horizontal = ('roles_permitidos',)

admin.site.register(Evento, EventoAdmin)