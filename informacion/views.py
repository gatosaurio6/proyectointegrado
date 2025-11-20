from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User, Group
from .models import Evento, Documento, Area, PerfilUsuario, SolicitudDiaLibre, SolicitudVacaciones, LicenciaMedica, Anuncio,ReporteProblema
from .forms import DocumentoForm, SolicitudDiaLibreForm, SolicitudVacacionesForm, LicenciaMedicaForm,UserUpdateForm, PerfilUpdateForm, AreaForm, AsignarRolForm, AnuncioForm, EventoForm,UserCreateForm, ReporteProblemaForm

#Vistas del Sitio

@login_required
def inicio_generico(request):
    dias_totales = 15 
    dias_usados = SolicitudDiaLibre.objects.filter(solicitante=request.user, estado='aprobado').count()
    dias_disponibles = dias_totales - dias_usados

    context = {
        'dias_disponibles': dias_disponibles,
    }
    return render(request, 'inicio.html', context)

@login_required
def inicio_direccion(request):
    if not request.user.groups.filter(name='Direccion').exists():
        return HttpResponseForbidden("No tienes permisos de Dirección")
    return inicio_generico(request)

@login_required
def inicio_subdireccion(request):
    if not request.user.groups.filter(name__in=['Subdireccion Administrativa', 'Subdireccion Clinica']).exists():
        return HttpResponseForbidden("No tienes permisos de Subdirección")
    return inicio_generico(request)

@login_required
def inicio_jefatura(request):
    if not request.user.groups.filter(name='Jefatura').exists():
        return HttpResponseForbidden("No tienes permisos de Jefatura")
    return inicio_generico(request)

@login_required
def inicio_funcionario(request):
    # El funcionario entra directo
    return inicio_generico(request)

def login(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        contrasena = request.POST.get('password')
        user = authenticate(request, username=usuario, password=contrasena)

        if user is not None:
            auth_login(request, user)

            if user.groups.filter(name= 'Direccion').exists():
                return redirect('inicio_direccion')
            elif user.groups.filter(name__in = ['Subdireccion Administrativa', 'Subdireccion Clinica']).exists():
                return redirect('inicio_subdireccion')
            elif user.groups.filter(name = 'Jefatura').exists():
                return redirect('inicio_jefatura')
            elif user.groups.filter(name = 'Funcionario').exists():
                return redirect ('inicio_funcionario')
            else:
                messages.error(request, 'no se ha asignado un rol al usuario.')
                return render(request, 'login.html')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render (request, 'login.html', {'error': 'Usuario o contraseña incorrectos.'})
    
    return render(request, 'login.html')

@login_required
def anuncios(request):
    noticias = Anuncio.objects.all().order_by('-fecha_publicacion')
    return render(request, 'anuncios.html', {'noticias': noticias})

@login_required
def avisos(request):
    if request.method == 'POST':
        form = ReporteProblemaForm(request.POST)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.solicitante = request.user
            reporte.save()
            messages.success(request, '¡Tu reporte ha sido enviado correctamente!')
            return redirect('avisos') 
    else:
        form = ReporteProblemaForm()
    if request.user.groups.filter(name__in=['Direccion', 'Subdireccion Administrativa']).exists():
        mis_reportes = ReporteProblema.objects.all().order_by('-fecha_reporte')
        es_admin = True
    else:
        mis_reportes = ReporteProblema.objects.filter(solicitante=request.user).order_by('-fecha_reporte')
        es_admin = False
    context = {
        'form': form,
        'mis_reportes': mis_reportes,
        'es_admin': es_admin
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
        if not request.user.groups.filter(name__in= ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']).exists():
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
    if not request.user.groups.filter(name__in = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']).exists():
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
    if not request.user.groups.filter(name__in= ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']).exists():
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
            if request.user.groups.filter(name = 'Direccion').exists():
                return redirect ('inicio_direccion')
            elif request.user.groups.filter(name__in = ['Subdireccion Administrativa', 'Subdireccion Clinica']).exists():
                return redirect ('inicio_subdireccion')
            elif request.user.groups.filter(name = 'Jefatura').exists():
                return redirect ('inicio_jefatura')
            elif request.user.groups.filter(name= 'Funcionario').exists():
                return redirect ('inicio_funcionario')
            else:
                return redirect ('login')
    else:
        form = SolicitudDiaLibreForm()
    
    return render(request, 'crear_solicitud.html', {'form': form})

@login_required
def revisar_solicitudes(request):
    # Verificar permisos
    if not request.user.groups.filter(name__in=['Jefatura', 'Direccion']).exists():
        return HttpResponseForbidden("No tienes permiso.")

    solicitudes_pendientes = []
    area_del_jefe = None

    # Lógica: Obtener el área donde este usuario es el JEFE
    try:
        area_del_jefe = Area.objects.get(jefe=request.user)
        
        # FILTRO CLAVE: Traer solo solicitudes de esa área y que estén pendientes
        solicitudes_pendientes = SolicitudDiaLibre.objects.filter(
            area=area_del_jefe,
            estado='pendiente'
        ).order_by('fecha_inicio')
        
    except Area.DoesNotExist:
        # Si el usuario es Jefatura pero no se le ha asignado un Área en el admin
        pass 

    context = {
        'solicitudes': solicitudes_pendientes,
        'area_del_jefe': area_del_jefe
    }
    return render(request, 'revisar_solicitudes.html', context)

@login_required
def gestionar_solicitud(request, solicitud_id, accion):
    if not request.user.groups.filter(name__in=['Jefatura', 'Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']).exists():
        return HttpResponseForbidden("No tienes permiso.")

    solicitud = get_object_or_404(SolicitudDiaLibre, id=solicitud_id)

    if request.user.groups.filter (name = 'Jefatura').exists():
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
    else:
        return HttpResponseForbidden("aacion no válida.")
    
    solicitud.save()
    return redirect('revisar_solicitudes')

# --- Vistas de Solicitud de Vacaciones ---

@login_required
def crear_solicitud_vacaciones(request):
    if request.method == 'POST':
        form = SolicitudVacacionesForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.solicitante = request.user
            
            try:
                perfil = request.user.perfil
                solicitud.area = perfil.area
            except PerfilUsuario.DoesNotExist:
                pass 
                
            solicitud.save()
            if request.user.groups.filter(name = 'Direccion').exists():
                return redirect ('inicio_direccion')
            elif request.user.groups.filter(name__in = ['Subdireccion Administrativa', 'Subdireccion Clinica']).exists():
                return redirect ('inicio_subdireccion')
            elif request.user.groups.filter(name = 'Jefatura').exists():
                return redirect ('inicio_jefatura')
            elif request.user.groups.filter(name= 'Funcionario').exists():
                return redirect ('inicio_funcionario')
            else:
                return redirect ('login')
    else:
        form = SolicitudVacacionesForm()
    
    return render(request, 'crear_solicitud_vacaciones.html', {'form': form})

@login_required
def revisar_solicitudes_vacaciones(request):
    if not request.user.groups.filter(name__in=['Jefatura', 'Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']).exists():
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    area_del_jefe = None
    try:
        area_del_jefe = Area.objects.get(jefe=request.user)
    except Area.DoesNotExist:
        pass 

    if area_del_jefe:
        solicitudes_pendientes = SolicitudVacaciones.objects.filter(
            area=area_del_jefe,
            estado='pendiente'
        ).order_by('fecha_inicio')
    else:
        solicitudes_pendientes = []

    context = {
        'solicitudes': solicitudes_pendientes,
        'area_del_jefe': area_del_jefe
    }
    return render(request, 'revisar_solicitudes_vacaciones.html', context)

@login_required
def gestionar_solicitud_vacaciones(request, solicitud_id, accion):
    if not request.user.groups.filter(name='Jefatura').exists():
        return HttpResponseForbidden("No tienes permiso.")

    solicitud = get_object_or_404(SolicitudVacaciones, id=solicitud_id)

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
    return redirect('revisar_solicitudes_vacaciones')

# --- Vistas de Licencia Médica ---

@login_required
def crear_licencia_medica(request):
    if request.method == 'POST':
        form = LicenciaMedicaForm(request.POST, request.FILES)
        if form.is_valid():
            licencia = form.save(commit=False)
            licencia.solicitante = request.user
            
            try:
                perfil = request.user.perfil
                licencia.area = perfil.area
            except PerfilUsuario.DoesNotExist:
                pass 
                
            licencia.save()
            return redirect('inicio')
    else:
        form = LicenciaMedicaForm()
    
    return render(request, 'crear_licencia_medica.html', {'form': form})

@login_required
def revisar_licencias_medicas(request):
    if not request.user.groups.filter(name='Jefatura').exists():
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    area_del_jefe = None
    try:
        area_del_jefe = Area.objects.get(jefe=request.user)
    except Area.DoesNotExist:
        pass 

    if area_del_jefe:
        licencias_pendientes = LicenciaMedica.objects.filter(
            area=area_del_jefe,
            estado='en revision'
        ).order_by('fecha_inicio')
    else:
        licencias_pendientes = []

    context = {
        'licencias': licencias_pendientes,
        'area_del_jefe': area_del_jefe
    }
    return render(request, 'revisar_licencias_medicas.html', context)

@login_required
def gestionar_licencia_medica(request, licencia_id, accion):
    if not request.user.groups.filter(name='Jefatura').exists():
        return HttpResponseForbidden("No tienes permiso.")

    licencia = get_object_or_404(LicenciaMedica, id=licencia_id)

    try:
        area_del_jefe = Area.objects.get(jefe=request.user)
        if licencia.area != area_del_jefe:
            return HttpResponseForbidden("Esta licencia no pertenece a tu área.")
    except Area.DoesNotExist:
        return HttpResponseForbidden("No eres jefe de ningún área.")

    if accion == 'aprobar':
        licencia.estado = 'aprobado'
        licencia.gestionado_por = request.user
    elif accion == 'rechazar':
        licencia.estado = 'rechazado'
        licencia.gestionado_por = request.user
    
    licencia.save()
    return redirect('revisar_licencias_medicas')

#CRUD
# --- CRUD DE GESTIÓN DE FUNCIONARIOS (PARA DIRECCIÓN) ---

@login_required
def lista_funcionarios(request):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    funcionarios = User.objects.filter(is_superuser=False).select_related('perfil')
    return render(request, 'crud/lista_funcionarios.html', {'funcionarios': funcionarios})

@login_required
def editar_funcionario(request, user_id=None):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    if user_id:
        user_obj = get_object_or_404(User, pk=user_id)
        titulo = "Editar Funcionario"
        FormClass = UserUpdateForm 
        perfil_obj, created = PerfilUsuario.objects.get_or_create(user=user_obj)
    else:
        user_obj = None
        titulo = "Crear Nuevo Funcionario"
        FormClass = UserCreateForm
        perfil_obj = None
    if request.method == 'POST':
        u_form = FormClass(request.POST, instance=user_obj)
        p_form = PerfilUpdateForm(request.POST, instance=perfil_obj)
        if u_form.is_valid() and p_form.is_valid():
            user_created = u_form.save(commit=False)
            if not user_id:
                contrasena_plana = u_form.cleaned_data['password']
                user_created.set_password(contrasena_plana) 
            user_created.save()
            perfil = p_form.save(commit=False)
            perfil.user = user_created
            perfil.save()
            
            messages.success(request, f'Funcionario {user_created.username} guardado correctamente.')
            return redirect('lista_funcionarios')
    else:
        u_form = FormClass(instance=user_obj)
        p_form = PerfilUpdateForm(instance=perfil_obj)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'titulo': titulo
    }
    return render(request, 'crud/form_funcionario.html', context)

@login_required
def eliminar_funcionario(request, user_id):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    
    user_obj = get_object_or_404(User, pk=user_id)
    user_obj.delete()
    messages.warning(request, 'El funcionario ha sido eliminado.')
    return redirect('lista_funcionarios')

# --- GESTIÓN DE ÁREAS (CRUD) ---

@login_required
def lista_areas(request):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    
    areas = Area.objects.all()
    return render(request, 'crud/lista_areas.html', {'areas': areas})

@login_required
def editar_area(request, area_id=None):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")

    if area_id:
        area = get_object_or_404(Area, pk=area_id)
        titulo = "Editar Área"
    else:
        area = None
        titulo = "Nueva Área"

    if request.method == 'POST':
        form = AreaForm(request.POST, instance=area)
        if form.is_valid():
            form.save()
            messages.success(request, 'Área guardada correctamente.')
            return redirect('lista_areas')
    else:
        form = AreaForm(instance=area)

    return render(request, 'crud/form_generico.html', {'form': form, 'titulo': titulo})

@login_required
def eliminar_area(request, area_id):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    
    area = get_object_or_404(Area, pk=area_id)
    area.delete()
    messages.warning(request, 'Área eliminada.')
    return redirect('lista_areas')

# --- GESTIÓN RÁPIDA DE ROLES ---

@login_required
def asignar_rol(request):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    
    if request.method == 'POST':
        form = AsignarRolForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data['usuario']
            nuevo_rol = form.cleaned_data['rol']
            usuario.groups.clear()
            usuario.groups.add(nuevo_rol)
            
            messages.success(request, f'Rol {nuevo_rol.name} asignado a {usuario.username}')
            return redirect('lista_funcionarios')
    else:
        form = AsignarRolForm()

    return render(request, 'crud/form_generico.html', {'form': form, 'titulo': "Asignar Rol a Usuario"})

# crud evento

@login_required
def lista_eventos_gestion(request):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    eventos = Evento.objects.all().order_by('-fecha_inicio')
    return render(request, 'crud/lista_eventos.html', {'eventos': eventos})

@login_required
def editar_evento_gestion(request, evento_id=None):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    
    if evento_id:
        evento = get_object_or_404(Evento, pk=evento_id)
        titulo = "Editar Evento"
    else:
        evento = None
        titulo = "Nuevo Evento"

    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento guardado.')
            return redirect('lista_eventos_gestion')
    else:
        form = EventoForm(instance=evento)

    return render(request, 'crud/form_generico.html', {'form': form, 'titulo': titulo})

@login_required
def eliminar_evento_gestion(request, evento_id):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    
    evento = get_object_or_404(Evento, pk=evento_id)
    evento.delete()
    messages.success(request, 'Evento eliminado.')
    return redirect('lista_eventos_gestion')

# crud anuncio

@login_required
def lista_anuncios_gestion(request):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    anuncios_list = Anuncio.objects.all().order_by('-fecha_publicacion')
    return render(request, 'crud/lista_anuncios.html', {'anuncios': anuncios_list})

@login_required
def editar_anuncio_gestion(request, anuncio_id=None):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    
    if anuncio_id:
        anuncio = get_object_or_404(Anuncio, pk=anuncio_id)
        titulo = "Editar Anuncio"
    else:
        anuncio = None
        titulo = "Nuevo Anuncio"

    if request.method == 'POST':
        form = AnuncioForm(request.POST, instance=anuncio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Anuncio publicado.')
            return redirect('lista_anuncios_gestion')
    else:
        form = AnuncioForm(instance=anuncio)

    return render(request, 'crud/form_generico.html', {'form': form, 'titulo': titulo})

@login_required
def eliminar_anuncio_gestion(request, anuncio_id):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    
    anuncio = get_object_or_404(Anuncio, pk=anuncio_id)
    anuncio.delete()
    messages.success(request, 'Anuncio eliminado.')
    return redirect('lista_anuncios_gestion')


@login_required
def dashboard_direccion(request):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    total_usuarios = User.objects.count()
    total_jefes = User.objects.filter(groups__name='Jefatura').count()
    sesiones_activas = Session.objects.filter(expire_date__gte=timezone.now())
    lista_user_id = []
    for sesion in sesiones_activas:
        data = sesion.get_decoded()
        user_id = data.get('_auth_user_id', None)
        if user_id and user_id not in lista_user_id:
            lista_user_id.append(user_id)
    cantidad_online = len(lista_user_id)

    solicitudes_pendientes = SolicitudDiaLibre.objects.filter(estado='pendiente').count()
    context = {
        'total_usuarios': total_usuarios,
        'total_jefes': total_jefes,
        'cantidad_online': cantidad_online,
        'solicitudes_pendientes': solicitudes_pendientes
    }
    return render(request, 'crud/dashboard.html', context)



# Gestion de reportes de problemas 

@login_required
def gestionar_reporte(request, reporte_id, accion):
    grupos_permitidos = ['Direccion', 'Subdireccion Administrativa', 'Subdireccion Clinica']
    if not request.user.groups.filter(name__in=grupos_permitidos).exists():
        return HttpResponseForbidden("Acceso denegado")
    reporte = get_object_or_404(ReporteProblema, pk=reporte_id)
    if accion == 'procesar':
        reporte.estado = 'en_proceso'
        messages.info(request, f'Reporte "{reporte.titulo}" marcado como En Proceso.')
    elif accion == 'resolver':
        reporte.estado = 'resuelto'
        messages.success(request, f'Reporte "{reporte.titulo}" marcado como Resuelto.')
    elif accion == 'eliminar':
        reporte.delete()
        messages.warning(request, 'Reporte eliminado.')
        return redirect('avisos')
    reporte.save()
    return redirect('avisos')