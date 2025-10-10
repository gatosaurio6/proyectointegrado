from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('anuncios/', views.anuncios,name= 'anuncios'),
    path('avisos/', views.avisos, name='avisos')
]