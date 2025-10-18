from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from .models import Evento
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Q




#esto asegura que solo usuarios logeados puedan ver la pagina de inicio
@login_required 
def inicio(request):
    return render(request, 'inicio.html')

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'login.html')

def inicio(request):
    return render(request, 'inicio.html')

def anuncios(request):
    return render(request, 'anuncios.html')

def avisos(request):
    return render(request, 'avisos.html')


#API para manejar eventos del calendario.

@csrf_exempt
def calendario_eventos(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse([], safe=False)

        roles_del_usuario = request.user.groups.all()


        eventos_visibles = Evento.objects.filter(
            Q(roles_permitidos__isnull=True) | Q(roles_permitidos__in=roles_del_usuario)
        ).distinct()

        data = []
        for evento in eventos_visibles:
            data.append({
                'id': evento.id,
                'title': evento.titulo,
                'start': evento.fecha_inicio.isoformat(),
                'end': evento.fecha_fin.isoformat() if evento.fecha_fin else None,
                'description': evento.descripcion
            })
        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        if not request.user.is_staff:
            return JsonResponse({'error': 'No tienes permiso para crear eventos'}, status=403)
        
        data = json.loads(request.body)
        evento = Evento.objects.create(
            titulo=data['title'],
            fecha_inicio=data['start'],
            fecha_fin=data.get('end', None)
        )

        return JsonResponse({'id': evento.id, 'title': evento.titulo, 'start': evento.fecha_inicio, 'end': evento.fecha_fin}, status=201)
    
    return JsonResponse({'error': 'Método no soportado'}, status=405)

@csrf_exempt
def manipular_evento(request, evento_id):
    # --- CONTROL DE PERMISOS ---
    if not request.user.is_staff:
        return JsonResponse({'error': 'No tienes permiso para modificar eventos'}, status=403)

    try:
        evento = Evento.objects.get(pk=evento_id)
    except Evento.DoesNotExist:
        return JsonResponse({'error': 'Evento no encontrado'}, status=404)

    if request.method == 'PUT':
        data = json.loads(request.body)
        evento.titulo = data.get('title', evento.titulo)
        evento.fecha_inicio = data.get('start', evento.fecha_inicio)
        evento.fecha_fin = data.get('end', evento.fecha_fin)
        evento.save()
        return JsonResponse({'status': 'Evento actualizado'})
    
    if request.method == 'DELETE':
        evento.delete()
        return JsonResponse({'status': 'Evento eliminado'}, status=204)

    return JsonResponse({'error': 'Método no soportado'}, status=405)