
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.shortcuts import redirect
from . import views


urlpatterns = [
    
    #puse esta ruta para que al entrar a la pag principal te dirija al login
    path('', views.inicio_generico, name='inicio'),

    #las rutas que se usan para navegar durante la sesion al intranet
    path('login/', views.login, name='login'),
    path('inicio/direccion/', views.inicio_direccion, name='inicio_direccion'),
    path('inicio/subdireccion/', views.inicio_subdireccion, name = 'inicio_subdireccion'),
    path('inicio/jefatura/', views.inicio_jefatura, name = 'inicio_jefatura'),
    path('inicio/funcionario/', views.inicio_funcionario, name = 'inicio_funcionario'),
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
    path('solicitar-licencia/', views.crear_licencia_medica, name='solicitar_licencia'),

    # --- URLs para Solicitudes de Vacaciones ---
    path('solicitudes/vacaciones/crear/', views.crear_solicitud_vacaciones, name='crear_solicitud_vacaciones'),
    path('solicitudes/vacaciones/revisar/', views.revisar_solicitudes_vacaciones, name='revisar_solicitudes_vacaciones'),
    path('solicitudes/vacaciones/gestionar/<int:solicitud_id>/<str:accion>/', views.gestionar_solicitud_vacaciones, name='gestionar_solicitud_vacaciones'),

    # --- URLs para Licencias Médicas ---
    path('licencias/crear/', views.crear_licencia_medica, name='crear_licencia_medica'),
    path('licencias/revisar/', views.revisar_licencias_medicas, name='revisar_licencias_medicas'),
    path('licencias/gestionar/<int:licencia_id>/<str:accion>/', views.gestionar_licencia_medica, name='gestionar_licencia_medica'),

    #rutas para gestionar el CRUD
    # CRUD Funcionarios 
    path('gestion/funcionarios/', views.lista_funcionarios, name='lista_funcionarios'),
    path('gestion/funcionarios/crear/', views.editar_funcionario, name='crear_funcionario'),
    path('gestion/funcionarios/editar/<int:user_id>/', views.editar_funcionario, name='editar_funcionario'),
    path('gestion/funcionarios/eliminar/<int:user_id>/', views.eliminar_funcionario, name='eliminar_funcionario'),
    #  CRUD ÁREAS
    path('gestion/areas/', views.lista_areas, name='lista_areas'),
    path('gestion/areas/crear/', views.editar_area, name='crear_area'),
    path('gestion/areas/editar/<int:area_id>/', views.editar_area, name='editar_area'),
    path('gestion/areas/eliminar/<int:area_id>/', views.eliminar_area, name='eliminar_area'),
    # ROLES
    path('gestion/asignar-rol/', views.asignar_rol, name='asignar_rol'),
    # GESTIÓN DE EVENTOS 
    path('gestion/eventos/', views.lista_eventos_gestion, name='lista_eventos_gestion'),
    path('gestion/eventos/crear/', views.editar_evento_gestion, name='crear_evento'),
    path('gestion/eventos/editar/<int:evento_id>/', views.editar_evento_gestion, name='editar_evento'),
    path('gestion/eventos/eliminar/<int:evento_id>/', views.eliminar_evento_gestion, name='eliminar_evento'),

    #GESTIÓN DE ANUNCIOS
    path('gestion/anuncios/', views.lista_anuncios_gestion, name='lista_anuncios_gestion'),
    path('gestion/anuncios/crear/', views.editar_anuncio_gestion, name='crear_anuncio'),
    path('gestion/anuncios/editar/<int:anuncio_id>/', views.editar_anuncio_gestion, name='editar_anuncio'),
    path('gestion/anuncios/eliminar/<int:anuncio_id>/', views.eliminar_anuncio_gestion, name='eliminar_anuncio'),
    # GESTION DARSHBOARD
    path('gestion/dashboard/', views.dashboard_direccion, name='dashboard_direccion'),
#fin del crud

#rutas para reportes
path('avisos/gestionar/<int:reporte_id>/<str:accion>/', views.gestionar_reporte, name='gestionar_reporte'),









]


