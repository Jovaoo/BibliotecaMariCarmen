import unicodedata
import codecs
import hashlib
import os
import time
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import formats, timezone
from datetime import datetime
from dateutil import parser
from .forms import ChangePassword, Importar
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse,QueryDict
import requests
from .models import Centro, Libro, Log, Prestamo, User, ItemCatalogo, Ejemplar, CD, DVD, BR, Dispositivo
from django.views.decorators.csrf import csrf_exempt
import csv
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.db.models import Q
from .forms import UserForm
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Max
from django.db.models.functions import ExtractYear
from django.contrib.sessions.models import Session

from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.socialaccount.models import SocialAccount

from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
import requests

from allauth.account.signals import user_signed_up
from django.dispatch import receiver

@receiver(user_signed_up)
def handle_user_signed_up(sender, request, user, **kwargs):
    # Aquí puedes acceder al objeto de usuario recién creado (user)
    # y actualizar los campos específicos según los datos que llegan de GitHub
    social_account = user.socialaccount_set.first()  # Obtener la cuenta social asociada al usuario
    if social_account:
        extra_data = social_account.extra_data  # Datos adicionales proporcionados por GitHub
        # print(extra_data)  # Imprimir todos los datos adicionales de GitHub
        
        # Por ejemplo, si quieres actualizar el campo 'nombre' del usuario con el nombre de GitHub
        user.nombre = extra_data.get('name', '')  # 'name' es el campo de nombre en los datos de GitHub
        user.has_password_changed = True  # Actualiza el campo específico del usuario
        user.centro = 'Esteve Terradas Illa'
        user.fecha_nacimiento = '1998-12-07'
        avatar_url = extra_data.get('avatar_url')
        if avatar_url:
            user.image = avatar_url
            user.save()  # Guarda los cambios
        else:
            user.save()  # Guarda los cambios




# Create your views here.
def index(request):
    try:
        user_image = str(request.user.image)  # Convierte la URL a una cadena de texto
        print(user_image)
        if user_image.startswith("https://"):
            is_external_url = True
            print("htt")
        else:
            is_external_url = False
            print("noo httt")
    except:
        pass
    if request.method == "POST":

        # Validate using the User model
        username = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not user.has_password_changed:
                if user.email == 'admin@admin.com':
                    user.has_password_changed = True
                    user.save()
                    registrar_evento(f'Inicio de sesión exitoso', 'INFO', request.user)
                    messages.success(request, 'Inici de sessió correcte!')
                    return redirect('index')
                else:
                    messages.warning(request, 'La contrasenya predeterminada és insegura. Canvia-la ara mateix per poder accedir als continguts.')
                    return redirect('canviar_contrasenya')
            else:
                # Aqui deberia ir un mensaje de exito.
                registrar_evento(f'Inicio de sesión exitoso', 'INFO', request.user)
                messages.success(request, 'Inici de sessió correcte!')
                return redirect('dashboard')
        else:
            # Aqui deberia ir un mensaje de error.
            registrar_evento('Inici de sessió fallit', 'ERROR')
            messages.error(request, 'Email o contrasenya incorrectes')
            return redirect('index')
    else:
        try:
            return render(request, 'myapp/index.html', {'is_external_url': is_external_url})
        except:
            return render(request, 'myapp/index.html', {})

    

@login_required
def usuari(request):
    user = request.user
    if not user.has_password_changed:
        messages.warning(request, 'La contrasenya predeterminada és insegura. Canvia-la ara mateix per poder accedir als continguts.')
        return render(request, 'myapp/dashboard/canviar_contrasenya.html')
    users = User.objects.all()

    # actualizar datos del usuario
    if request.method == "POST":
        user_id = request.POST.get('id')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                image_file = request.FILES.get('image')

                # DESARROLLO:
                if image_file:
                    # Generar un nombre único para la imagen utilizando un hash
                    hash_object = hashlib.md5(image_file.read())
                    hashed_name = hash_object.hexdigest() + '.png'

                    # Guardar la imagen en el directorio adecuado
                    file_path = os.path.join(settings.STATIC_ROOT)
                    with open(file_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
                    
                    # Asignar el nombre de la imagen al usuario
                    user.image = request.FILES.get('image')


                ''' PRODUCCION:
                if image_file:
                    # Generar un nombre único para la imagen utilizando un hash
                    hash_object = hashlib.md5(image_file.read())
                    hashed_name = hash_object.hexdigest() + '.png'

                    # Normalizar el nombre del archivo para eliminar caracteres no ASCII
                    normalized_name = unicodedata.normalize('NFKD', hashed_name).encode('ASCII', 'ignore').decode('ASCII')

                    # Guardar la imagen en el directorio adecuado con el nombre normalizado
                    file_path = os.path.join('/djangoApp/BibliotecaMariCarmen/BibliotecaIETI/static/profile_photos', normalized_name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)                    # Asignar el nombre de la imagen al usuario
                    user.image = f'profile_photos/{normalized_name}'
                '''

                if user.first_name != request.POST.get('first_name', user.first_name):
                    user.first_name = request.POST.get('first_name', user.first_name)
                if user.last_name != request.POST.get('last_name', user.last_name):
                    user.last_name = request.POST.get('last_name', user.last_name)
                if user.centro != request.POST.get('centro', user.centro):
                    user.centro = request.POST.get('centro', user.centro)
                if user.ciclo != request.POST.get('ciclo', user.ciclo):
                    user.ciclo = request.POST.get('ciclo', user.ciclo)
                if user.telefono != request.POST.get('telefono', user.telefono):
                    user.telefono = request.POST.get('telefono', user.telefono)
                if user.fecha_nacimiento != parser.parse(request.POST.get('fecha_nacimiento', user.fecha_nacimiento)):
                    user.fecha_nacimiento = parser.parse(request.POST.get('fecha_nacimiento', user.fecha_nacimiento))
                
                user.save()
                messages.success(request, 'Datos actualizados correctamente')
                registrar_evento(f'Datos de "{user}" actualizados correctamente', 'INFO')
                return redirect('usuari')
            except User.DoesNotExist:
                messages.error(request, 'El usuario no existe')
                registrar_evento(f'Intento de actualización de datos para un usuario inexistente', 'ERROR')
                return redirect('usuari')
        else:
            messages.error(request, 'Falta el campo ID')
            registrar_evento('Intento de actualización de datos sin ID', 'ERROR')
            return redirect('usuari')
    
    user_image = str(request.user.image)  # Convierte la URL a una cadena de texto
    print(user_image)
    if user_image.startswith("https://"):
        is_external_url = True
        print("htt")
    else:
        is_external_url = False
        print("noo httt")
    # Obtener fecha de nacimiento del usuario
    fecha_nacimiento = None
    if request.user.fecha_nacimiento:
        fecha_nacimiento = request.user.fecha_nacimiento.strftime('%Y-%m-%d')

    return render(request, 'myapp/dashboard/usuari.html', {'users': users, 'fecha_nacimiento': fecha_nacimiento, 'is_external_url': is_external_url})

#Editar Otros usuarios,
@login_required
def editUsuaris(request):
    user = request.user
    if not user.has_password_changed:
        messages.warning(request, 'La contrasenya predeterminada és insegura. Canvia-la ara mateix per poder accedir als continguts.')
        return render(request, 'myapp/dashboard/canviar_contrasenya.html')

    # actualizar datos del usuario
    if request.method == "POST":
        user_id = request.POST.get('id')
        if user_id:
            try:
                user = User.objects.get(pk=user_id)
                image_file = request.FILES.get('image')
                
                # DESARROLLO:
                if image_file:
                    # Generar un nombre único para la imagen utilizando un hash
                    hash_object = hashlib.md5(image_file.read())
                    hashed_name = hash_object.hexdigest() + '.png'

                    # Guardar la imagen en el directorio adecuado
                    file_path = os.path.join(settings.STATIC_ROOT)
                    with open(file_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
                    
                    # Asignar el nombre de la imagen al usuario
                    user.image = request.FILES.get('image')


                ''' PRODUCCION:
                if image_file:
                    # Generar un nombre único para la imagen utilizando un hash
                    hash_object = hashlib.md5(image_file.read())
                    hashed_name = hash_object.hexdigest() + '.png'

                    # Normalizar el nombre del archivo para eliminar caracteres no ASCII
                    normalized_name = unicodedata.normalize('NFKD', hashed_name).encode('ASCII', 'ignore').decode('ASCII')

                    # Guardar la imagen en el directorio adecuado con el nombre normalizado
                    file_path = os.path.join('/djangoApp/BibliotecaMariCarmen/BibliotecaIETI/static/profile_photos', normalized_name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)                    # Asignar el nombre de la imagen al usuario
                    user.image = f'profile_photos/{normalized_name}'
                '''
                 
                if user.first_name != request.POST.get('first_name', user.first_name):
                    user.first_name = request.POST.get('first_name', user.first_name)
                if user.last_name != request.POST.get('last_name', user.last_name):
                    user.last_name = request.POST.get('last_name', user.last_name)
                if user.centro != request.POST.get('centro', user.centro):
                    user.centro = request.POST.get('centro', user.centro)
                if user.ciclo != request.POST.get('ciclo', user.ciclo):
                    user.ciclo = request.POST.get('ciclo', user.ciclo)
                if user.telefono != request.POST.get('telefono', user.telefono):
                    user.telefono = request.POST.get('telefono', user.telefono)
                if user.fecha_nacimiento != parser.parse(request.POST.get('fecha_nacimiento', user.fecha_nacimiento)):
                    user.fecha_nacimiento = parser.parse(request.POST.get('fecha_nacimiento', user.fecha_nacimiento))

                user.save()
                messages.success(request, 'Datos actualizados correctamente')
                registrar_evento(f'Datos de "{user}" actualizados correctamente', 'INFO')
                return redirect('usuaris')
            except User.DoesNotExist:
                messages.error(request, 'El usuario no existe')
                registrar_evento(f'Intento de actualización de datos para un usuario inexistente', 'ERROR')
                return redirect('usuaris')
        else:
            messages.error(request, 'Falta el campo ID')
            registrar_evento('Intento de actualización de datos sin ID', 'ERROR')
            return redirect('usuaris')



    return render(request, 'myapp/dashboard/usuaris.html')

@login_required
def EditUsuarisView(request, user_id):
    # Obtener el usuario por su ID
    user = get_object_or_404(User, id=user_id)
    
    # Aquí podrías definir el formulario de edición de usuario
    # Por ejemplo, si estás utilizando forms.py:
    # from .forms import UserForm
    # form = UserForm(instance=user)

    # Obtener la fecha de nacimiento del usuario si está disponible
    fecha_nacimiento = None
    if user.fecha_nacimiento:
        fecha_nacimiento = user.fecha_nacimiento.strftime('%Y-%m-%d')
    
    # Luego, renderizas el template con el formulario y el usuario
    return render(request, 'myapp/dashboard/EditUsuaris.html', {'user': user, 'fecha_nacimiento': fecha_nacimiento})

@login_required
def dashboard(request):
    user = request.user
    user_image = str(request.user.image)  # Convierte la URL a una cadena de texto
    print(user_image)
    if user_image.startswith("https://"):
        is_external_url = True
        print("htt")
    else:
        is_external_url = False
        print("noo httt")
    if not user.has_password_changed:
        messages.warning(request, 'La contrasenya predeterminada és insegura. Canvia-la ara mateix per poder accedir als continguts.')
        return render(request, 'myapp/dashboard/canviar_contrasenya.html')
    return render(request, 'myapp/dashboard/dashboard.html',{'user': user,'is_external_url': is_external_url})

@login_required
def logout_user(request):
    logout(request)
    messages.info(request, 'Fins aviat!')
    registrar_evento('Sessió tancada amb èxit', 'INFO')
    return redirect('index')

@login_required
def canviar_contrasenya(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            if not user.has_password_changed:
                user.has_password_changed = True
                user.save()
                update_session_auth_hash(request, user)  # Actualiza la sesión para que el usuario no sea deslogueado
                messages.success(request, 'Contraseña cambiada correctamente')
                registrar_evento('Contrasenya canviada correctament', 'INFO')
                return redirect('dashboard')
            else:
                update_session_auth_hash(request, user)  # Actualiza la sesión para que el usuario no sea deslogueado
                messages.success(request, 'Contraseña cambiada correctamente')
                registrar_evento('Contrasenya canviada correctament', 'INFO')
                return redirect('usuari')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'myapp/dashboard/canviar_contrasenya.html', {'form': form})

@csrf_exempt
def cerca_cataleg(request):
    try:
        user_image = str(request.user.image)  # Convierte la URL a una cadena de texto
        print(user_image)
        if user_image.startswith("https://"):
            is_external_url = True
            print("htt")
        else:
            is_external_url = False
            print("noo httt")
    except:
        pass
    tipos_ocio = ItemCatalogo.objects.values_list('ocio', flat=True).distinct()
    tipos_dataEdicion = ItemCatalogo.objects.annotate(year=ExtractYear('data_edicion')).values_list('year', flat=True).distinct()
    tipos_dataEdicion = sorted(tipos_dataEdicion, reverse=True)
    tipos_dataEdicion = [tipos_dataEdicion[0], tipos_dataEdicion[-1]]
    tipos_centros = Centro.objects.all()
    estados = ['Disponible', 'Reservat', 'Prestat', 'No disponible']

    # Eliminar los parámetros de búsqueda de la sesión al cargar la página
    if not request.GET:
        if 'original_params' in request.session:
            del request.session['original_params']
            request.session.save()

    original_params = request.session.get('original_params', {})
    query = original_params.get('query', '')
    only_available = original_params.get('only_available', '')
    max_year_search = original_params.get('maxYearSearch', '')
    min_year_search = original_params.get('minYearSearch', '')

    if request.method == 'GET':
        new_params = request.GET.copy()
        query = new_params.get('cerca', query)
        only_available = new_params.get('nomes_disponible', only_available)
        max_year_search = new_params.get('maxYearSearch', max_year_search)
        min_year_search = new_params.get('minYearSearch', min_year_search)
        tipo_ocio_search = request.GET.getlist('tipo', [])  
        centro_search = request.GET.getlist('centro', [])  # Obtener la lista de centros seleccionados
        tipo_query_string = '&'.join([f'tipo={tipo}' for tipo in tipo_ocio_search])
        centro_query_string = '&'.join([f'centro={centro}' for centro in centro_search])  # Convertir la lista de centros en una cadena de consulta
        # estado del elemento
        estado_search = request.GET.getlist('estado')
        estado_query_string = '&'.join([f'estado={estado}' for estado in estado_search])

        print(estado_query_string)

        request.session['original_params'] = {
            'query': query,
        }

        if len(query) >= 3:
            if len(query) >= 3:
                if only_available:
                    response = requests.get(f'http://127.0.0.1:8000/get_ItemCatalogo?search={query}&only_available=true&maxYearSearch={max_year_search}&minYearSearch={min_year_search}&{tipo_query_string}&{centro_query_string}&{estado_query_string}')  # Incluir los centros seleccionados en la solicitud
                else:
                    response = requests.get(f'http://127.0.0.1:8000/get_ItemCatalogo?search={query}&maxYearSearch={max_year_search}&minYearSearch={min_year_search}&{tipo_query_string}&{centro_query_string}&{estado_query_string}')  # Incluir los centros seleccionados en la solicitud
            
            if response.status_code == 200:
                data = response.json().get('ItemCatalogo', [])
                for item in data:
                    centros = item.get('centros', [])
                    for centro in centros:
                        centro_id = centro.get('centro_id')
                        centro_name = get_object_or_404(Centro, id=centro_id).nombre  # Modificar esta línea para buscar por id_centro en lugar de id
                        centro['nombre_centro'] = centro_name

                paginator = Paginator(data, 25)
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)

                try:
                    return render(request, 'myapp/cerca_cataleg.html', {'is_external_url': is_external_url,'query': query, 'resultados': page_obj, 'tipos_ocio': tipos_ocio, 'tipos_dataEdicion': tipos_dataEdicion, 'tipos_centros': tipos_centros, 'estados': estados})
                except:
                    return render(request, 'myapp/cerca_cataleg.html', {'query': query, 'resultados': page_obj, 'tipos_ocio': tipos_ocio, 'tipos_dataEdicion': tipos_dataEdicion, 'tipos_centros': tipos_centros, 'estados': estados})
            else:
                error_message = 'Error al obtener resultados de la búsqueda'
                registrar_evento('Error al obtener resultados de la búsqueda', 'ERROR')
                return render(request, 'myapp/cerca_cataleg.html', {'query': query, 'error_message': error_message})
        else:
            error_message = 'La consulta debe tener al menos 3 caracteres'
            try:
                return render(request, 'myapp/cerca_cataleg.html', {'is_external_url': is_external_url, 'query': query, 'error_message': error_message})
            except:
                return render(request, 'myapp/cerca_cataleg.html', {'query': query, 'error_message': error_message})

    else:
        try:
            return render(request, 'myapp/cerca_cataleg.html', {'is_external_url': is_external_url, 'tipos_ocio': tipos_ocio, 'tipos_dataEdicion': tipos_dataEdicion, 'tipos_centros': tipos_centros, 'estados': estados})
        except:
            return render(request, 'myapp/cerca_cataleg.html', {'tipos_ocio': tipos_ocio, 'tipos_dataEdicion': tipos_dataEdicion, 'tipos_centros': tipos_centros, 'estados': estados})

def registrar_evento(evento, nivel, usuario=None):
    # Si no se proporciona un usuario, se asumirá como Anónimo
    if usuario is None:
        usuario = User.objects.get(username='Anonimo')

    # Crear el registro de log
    Log.objects.create(evento=evento, nivel=nivel, usuario=usuario)

@csrf_exempt
def guardar_log(request):
    if request.method == 'POST':
        evento = request.POST.get('evento')
        nivel = request.POST.get('nivel')
        
        if request.user.is_authenticated:
            usuario = request.user
        else:
            usuario_anonimo = User.objects.get(username='Anonimo')
            usuario = usuario_anonimo
        
        Log.objects.create(evento=evento, nivel=nivel, usuario=usuario)
        
        return JsonResponse({'mensaje': 'Log guardat correctament.'})
    else:
        return JsonResponse({'error': 'Mètode no permès.'}, status=405)

def process_csv(csv_file, centre_educatiu, request):
    user = request.user
    if not user.has_password_changed:
        messages.warning(request, 'La contrasenya predeterminada és insegura. Canvia-la ara mateix per poder accedir als continguts.')
        return render(request, 'myapp/dashboard/canviar_contrasenya.html')
    
    # Directorio donde se almacenarán los archivos CSV
    csv_directory = os.path.join(settings.MEDIA_ROOT, 'csv_files')
    
    # Asegurarse de que el directorio exista, si no, créalo
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)
    
    # Nombre del archivo
    file_name = csv_file.name
    
    # Ruta relativa del archivo CSV
    file_path = os.path.join(csv_directory, file_name)
    
    # Guardar el archivo CSV en el sistema de archivos
    with open(file_path, 'wb+') as destination:
        for chunk in csv_file.chunks():
            destination.write(chunk)
    
    # Ahora abrir el archivo CSV desde la ubicación guardada
    with open(file_path, 'r', encoding='ISO-8859-1') as file:
        csv_reader = csv.reader(file, delimiter=',')
        # contraseña hash
        hashed_password = make_password("password")

        # Iterar sobre cada fila del archivo CSV
        for line_number, row in enumerate(csv_reader, start=1):
            try:
                # Supongamos que el archivo CSV tiene el formato: nombre, apellidos, email, fecha de nacimiento, ciclo, roles
                username, last_name, email, fecha_nacimiento, ciclo, centro, roles, telefono  = row
                # Crea un nuevo objeto User y asigna los valores
                user = User(
                    username=email,
                    password=hashed_password,  # Guarda la contraseña hasheada
                    first_name=username,
                    last_name=last_name,
                    email=email,
                    fecha_nacimiento=fecha_nacimiento,
                    centro=centre_educatiu,
                    ciclo=ciclo,
                    roles=roles, # Guarda la imagen y asigna la ruta
                    telefono=telefono
                )
                # Guarda el objeto User en la base de datos
                user.save()
            except ValueError:
                # Manejar el caso donde la fila no tiene el formato correcto
                messages.warning(request, f"Línea {line_number}: No s'ha importat correctament. Format incorrecte.")

# En tu vista Django
def upload_file(request):
    if request.method == 'POST':
        form = Importar(request.POST, request.FILES)
        if form.is_valid():  # Verificar si el formulario es válido
            csv_file = request.FILES.get('csv_file')  # Obtener el archivo CSV si existe
            if csv_file:  # Verificar si se proporcionó un archivo CSV
                print("Paso por aqui 2") 
                centre_educatiu = form.cleaned_data.get('centre_educatiu') 
                process_csv(csv_file, centre_educatiu,request)
                messages.success(request, "El fitxer CSV s'ha importat correctament.")
                return render(request, 'myapp/dashboard/importar.html', {'form': form})
            else:
                # Manejar el caso donde no se proporciona el archivo CSV
                messages.error(request, "No s'ha proporcionat cap fitxer CSV.")
                print(form.errors)  # Imprime los errores del formulario en la consola
    else:
        form = Importar()
        print("Paso por aqui 3") 
    return render(request, 'myapp/dashboard/importar.html', {'form': form})

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def usuaris(request):
    # Obtén todos los usuarios excluyendo el usuario anónimo y el superusuario
    centro_usuario_actual = request.user.centro
    users = User.objects.exclude(email='Anonimo@Anonimo.com').exclude(is_superuser=True).exclude(id=request.user.id).filter(centro=centro_usuario_actual)
    
    # Pagina los usuarios
    paginator = Paginator(users, 25)  # Divide los usuarios en grupos de 25 por página
    page_number = request.GET.get('page')  # Obtiene el número de página de la solicitud GET
    
    try:
        users = paginator.page(page_number)
    except PageNotAnInteger: 
        # Si la página no es un número entero, muestra la primera página
        users = paginator.page(1)
    except EmptyPage: 
        # Si la página está fuera de rango (por encima del número máximo de páginas), muestra la última página
        users = paginator.page(paginator.num_pages)
    
    # Pasa el número total de páginas al contexto de la plantilla
    total_pages = paginator.num_pages
    
    # Renderiza el template con la lista de usuarios paginada
    return render(request, 'myapp/dashboard/usuaris.html', {'users': users, 'total_pages': total_pages})


@login_required
def EditUsuaris(request, user_id):
    # Obtener el usuario por su ID
    user = get_object_or_404(User, id=user_id)
    
    # Aquí podrías definir el formulario de edición de usuario
    # Por ejemplo, si estás utilizando forms.py:
    # from .forms import UserForm
    # form = UserForm(instance=user)
    
    # Luego, renderizas el template con el formulario y el usuario
    return render(request, 'myapp/dashboard/EditUsuaris.html', {'user': user})

## Prestamos

@login_required
def prestamos(request):
    
    # Obtén todos los préstamos
    prestamos = Prestamo.objects.all()
    
    # Pagina los préstamos
    paginator = Paginator(prestamos, 25)  # Divide los préstamos en grupos de 25 por página
    page_number = request.GET.get('page')  # Obtiene el número de página de la solicitud GET
    
    try:
        prestamos = paginator.page(page_number)
    except PageNotAnInteger: 
        # Si la página no es un número entero, muestra la primera página
        prestamos = paginator.page(1)
    except EmptyPage: 
        # Si la página está fuera de rango (por encima del número máximo de páginas), muestra la última página
        prestamos = paginator.page(paginator.num_pages)
    
    if request.method == 'POST':        
        prestamo_id = request.POST.get('id')
        prestamo = Prestamo.objects.get(pk=prestamo_id)
        ejemplar = Ejemplar.objects.get(pk=prestamo.ejemplar.id)
        elemento = ejemplar.elemento
        elemento.cantidad_disponible += 1
        elemento.save()
        prestamo.delete()
        
        messages.success(request, '¡Préstamo eliminado correctamente!')

    # Renderiza el template con la lista de préstamos paginada
    return render(request, 'myapp/dashboard/prestecs.html', {'prestamos': prestamos})

@login_required
def nou_prestec(request):
    items_catalogo = ItemCatalogo.objects.all()
    users = User.objects.all()
    
    if request.method == 'POST':
        # añadir nuevo Ejemplar a la base de datos 
        ejemplar_objs = []
        elemento = None
        # espera de 0.5s para evitar errores de concurrencia
        time.sleep(0.5)
        if request.POST.get('article').startswith('CD'):
            elemento = CD.objects.get(id_catalogo=request.POST.get('article'))
        elif request.POST.get('article').startswith('DVD'):
            elemento = DVD.objects.get(id_catalogo=request.POST.get('article'))
        elif request.POST.get('article').startswith('BR'):
            elemento = BR.objects.get(id_catalogo=request.POST.get('article'))
        elif request.POST.get('article').startswith('DIS'):
            elemento = Dispositivo.objects.get(id_catalogo=request.POST.get('article'))
        elif request.POST.get('article').startswith('LB'):
            elemento = Libro.objects.get(id_catalogo=request.POST.get('article'))
        # asignar un nuevo codigo a cada ejemplar a partir del ultimo codigo (EJ001)
        codigo = Ejemplar.objects.all().order_by('-codigo').first().codigo
        codigo = f'EJ{int(codigo[2:])+1:03}'
        time.sleep(0.3)
        ejemplar_objs.append(Ejemplar(
            elemento=elemento,
            codigo=codigo,
            disponible=False
        ))
        Ejemplar.objects.bulk_create(ejemplar_objs)

        # restar 1 a la cantidad de ejemplares disponibles
        elemento.cantidad_disponible -= 1
        elemento.save()

        # añadir nuevo prestamo a la base de datos
        usuario = User.objects.get(pk=request.POST.get('usuari'))
        ejemplar = Ejemplar.objects.get(codigo=codigo)

        # convierto la fecha de prestamo a formato datetime
        fecha_fin = timezone.make_aware(datetime.strptime(request.POST.get('date_range'), "%d-%m-%Y %H:%M"))

        print(fecha_fin)
        Prestamo.objects.create(
            usuario=usuario,
            ejemplar=ejemplar,
            fecha_devolucion=fecha_fin,
        )
        messages.success(request, 'Prestec creat correctament!')


    return render(request, 'myapp/dashboard/nou_prestec.html', {'items_catalogo': items_catalogo, 'users': users})
    
# CREAR USUARIO PANEL
def crear_usuari(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        
        try:
            # Contraseña hash
            hashed_password = make_password("P@ssw0rd")

            if form.is_valid():
                username = request.POST.get('username')
                #email = request.POST.get('email')

                if User.objects.filter(username=username).exists():
                    messages.error(request, 'El nom de usuario ja está en us.')
                    return render(request, 'myapp/dashboard/crear_usuari.html', {'form': form})
                
                user = form.save(commit=False)
                user.has_password_changed = False
                user.first_name = request.POST.get('first_name')
                user.last_name = request.POST.get('last_name')
                user.username = request.POST.get('email')
                user.password = hashed_password
                user.save()
                messages.success(request, 'Usuario creat amb éxit.')
                return render(request, 'myapp/dashboard/crear_usuari.html', {'form': form})
            else:
                # Capturar errores de validación específicos del campo email
                email_errors = form.errors.get('email')
                username_errors = form.errors.get('username')

                if email_errors:
                    messages.error(request, email_errors)
                elif username_errors:
                    messages.error(request, username_errors)
                else:
                    messages.error(request, 'Error de validació en el formulari')
                
                return render(request, 'myapp/dashboard/crear_usuari.html', {'form': form})

        except Exception as e:
            print("Error:", str(e))
            messages.error(request, 'El nom de usuari ya existeix.')
            return render(request, 'myapp/dashboard/crear_usuari.html', {'form': form})

    else:
        form = UserForm()
   
    return render(request, 'myapp/dashboard/crear_usuari.html', {'form': form})

#AÑADIR NUEVO LIBRO A PARTIR DE API EXTERNA                 
def nou_element(request):
    print("Entro en la funcion OK")
    
    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        titulo = request.POST.get('titulo')
        autor = request.POST.get('autor')
        editorial = request.POST.get('editorial')
        numpag = request.POST.get('numpag')
        data = request.POST.get('data')
        
        try:
            # Verificar si ya existe un libro con el mismo ISBN
            existing_libro = Libro.objects.filter(ISBN=isbn).exists()
            if existing_libro:
                messages.error(request, "L'exemplar amb aquest ISBN ja existeix al cataleg")
                return render(request, 'myapp/dashboard/nou_element.html', {'error_message': 'Error al crear el libro'})
            
            # Obtener el último valor de id_catalogo
            last_id_catalogo = Libro.objects.aggregate(Max('id_catalogo'))['id_catalogo__max']
            
            # Si no hay ningún libro en la base de datos, empezar desde LB001
            if last_id_catalogo:
                # Extraer el número y convertirlo a entero
                last_id_number = int(last_id_catalogo[2:])
                
                # Incrementar en uno
                new_id_number = last_id_number + 1
                
                # Formar el nuevo id_catalogo
                new_id_catalogo = "LB" + str(new_id_number).zfill(3)
            else:
                new_id_catalogo = "LB001"
            
            # Crear un nuevo objeto Libro con los datos proporcionados
            libro = Libro(ISBN=isbn, titulo=titulo, autor=autor, editorial=editorial, paginas=numpag, data_edicion=data, id_catalogo=new_id_catalogo, ocio="Novel·la",CDU='821.133.1(73)-31' )
            libro.save()
            
            # Redireccionar a alguna página de éxito o a donde desees
            messages.success(request, 'Exemplar afegit amb exit.')
            return redirect('nou_element')
            
        except Exception as e:
            print("Error:", str(e))
            messages.error(request, "L'exemplar ja existeix al cataleg")
            # Manejar cualquier error que pueda ocurrir al guardar el libro
            
            # Renderizar el formulario con el error
            return render(request, 'myapp/dashboard/nou_element.html', {'error_message': 'Error al crear el libro'})

    # Si no es una solicitud POST, simplemente renderiza el formulario vacío
    return render(request, 'myapp/dashboard/nou_element.html', {})
