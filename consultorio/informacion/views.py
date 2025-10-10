from django.shortcuts import render

# Create your views here.

def login (request):
    return render (request, 'login.html', {})

def inicio (request):
    return render (request, 'inicio.html', {})

def anuncios (request):
    return render (request, 'anuncios.html', {})

def avisos (request):
    return render (request, 'avisos.html', {})