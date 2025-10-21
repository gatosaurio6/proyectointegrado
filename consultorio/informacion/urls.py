
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.shortcuts import redirect
from . import views


urlpatterns = [
    
    #puse esta ruta para que al entrar a la pag principal te dirija al login
    path('', lambda request: redirect('login')),

    #las rutas que se usan para navegar durante la sesion al intranet
    path('login/', views.login, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('anuncios/', views.anuncios, name='anuncios'),
    path('avisos/', views.avisos, name='avisos'),

    #Las rutas que tenemos para el calendario
    path('api/eventos/', views.calendario_eventos, name='calendario_eventos'),
    path('api/eventos/<int:evento_id>/', views.manipular_evento, name='manipular_evento'),

    path('documentos/', views.lista_documentos, name='lista_documentos'),
    path('documentos/subir/', views.subir_documento, name='subir_documento'),

    # --- NUEVAS URLs PARA SOLICITUDES ---
    path('solicitudes/crear/', views.crear_solicitud, name='crear_solicitud'),
    path('solicitudes/revisar/', views.revisar_solicitudes, name='revisar_solicitudes'),
    path('solicitudes/gestionar/<int:solicitud_id>/<str:accion>/', views.gestionar_solicitud, name='gestionar_solicitud'),
]
