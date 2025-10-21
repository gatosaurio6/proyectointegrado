from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from .models import Evento, Documento, Area, PerfilUsuario, SolicitudDiaLibre
from .forms import DocumentoForm, SolicitudDiaLibreForm
import json

#Vistas del Sitio

@login_required
def inicio(request):
    return render(request, 'inicio.html')

def login(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        contrasena = request.POST.get('password')
        user = authenticate(request, username=usuario, password=contrasena)

        if user is not None:
            auth_login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos.'})
    return render(request, 'login.html')

@login_required
def anuncios(request):
    return render(request, 'anuncios.html')

@login_required
def avisos(request):
    sesiones_activas = Session.objects.filter(expire_date__gte=timezone.now())
    lista_user_id = []
    for sesion in sesiones_activas:
        data = sesion.get_decoded()
        user_id = data.get('_auth_user_id', None)
        if user_id and user_id not in lista_user_id:
            lista_user_id.append(user_id)

    usuarios_conectados = User.objects.filter(id__in=lista_user_id)

    context = {
        'usuarios_conectados': usuarios_conectados
    }
    return render(request, "avisos.html", context)


# Vista del calendario

@csrf_exempt
@login_required
def calendario_eventos(request):
    if request.method == 'GET':
        roles_del_usuario = request.user.groups.all()
        eventos_visibles = Evento.objects.filter(
            Q(roles_permitidos=None) | Q(roles_permitidos__in=roles_del_usuario)
        ).distinct()

        data = []
        for evento in eventos_visibles:
            data.append({
                'id': evento.id,
                'title': evento.titulo,
                'start': evento.fecha_inicio.isoformat(),
                'end': evento.fecha_fin.isoformat() if evento.fecha_fin else None,
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
@login_required
def manipular_evento(request, evento_id):
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


# --- Vistas de Gestión de Documentos ---

@login_required
def lista_documentos(request):
    documentos = Documento.objects.all().order_by('-fecha_subida')
    return render(request, 'lista_documentos.html', {'documentos': documentos})

@login_required
def subir_documento(request):
    if not request.user.is_staff:
        return redirect('lista_documentos')

    if request.method == 'POST':
        form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_documentos')
    else:
        form = DocumentoForm()
    
    return render(request, 'subir_documento.html', {'form': form})


# --- Vistas de Solicitud de Días Libres ---

@login_required
def crear_solicitud(request):
    if request.method == 'POST':
        form = SolicitudDiaLibreForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.solicitante = request.user
            
            try:
                perfil = request.user.perfil
                solicitud.area = perfil.area
            except PerfilUsuario.DoesNotExist:
                pass 
                
            solicitud.save()
            return redirect('inicio')
    else:
        form = SolicitudDiaLibreForm()
    
    return render(request, 'crear_solicitud.html', {'form': form})

@login_required
def revisar_solicitudes(request):
    if not request.user.groups.filter(name='Jefatura').exists():
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    area_del_jefe = None
    try:
        area_del_jefe = Area.objects.get(jefe=request.user)
    except Area.DoesNotExist:
        pass 

    if area_del_jefe:
        solicitudes_pendientes = SolicitudDiaLibre.objects.filter(
            area=area_del_jefe,
            estado='pendiente'
        ).order_by('fecha_inicio')
    else:
        solicitudes_pendientes = []

    context = {
        'solicitudes': solicitudes_pendientes,
        'area_del_jefe': area_del_jefe
    }
    return render(request, 'revisar_solicitudes.html', context)

@login_required
def gestionar_solicitud(request, solicitud_id, accion):
    if not request.user.groups.filter(name='Jefatura').exists():
        return HttpResponseForbidden("No tienes permiso.")

    solicitud = get_object_or_404(SolicitudDiaLibre, id=solicitud_id)

    try:
        area_del_jefe = Area.objects.get(jefe=request.user)
        if solicitud.area != area_del_jefe:
            return HttpResponseForbidden("Esta solicitud no pertenece a tu área.")
    except Area.DoesNotExist:
        return HttpResponseForbidden("No eres jefe de ningún área.")

    if accion == 'aprobar':
        solicitud.estado = 'aprobado'
        solicitud.gestionado_por = request.user
    elif accion == 'rechazar':
        solicitud.estado = 'rechazado'
        solicitud.gestionado_por = request.user
    
    solicitud.save()
    return redirect('revisar_solicitudes')