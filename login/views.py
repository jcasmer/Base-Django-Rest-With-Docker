# pylint: disable=C0111
'''
Vista del archivo login
'''
import random
import string
import requests

from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View
from rest_framework import status, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
# Importar nuevas librerias de login...
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

class LoginView(TokenObtainPairView):
    '''
    Metodo para iniciar sesión.
    '''

    authentication_classes = ()
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        '''
        Se sobreescribe el metodo para retorna información adicional como los datos del usuario.
        '''
        try:
            # Inicializar objecto para almacenar los datos del usuarios.
            return_data = {}

            # Validar campos requeridos
            errors = {}

            username = request.data.get('username')
            password = request.data.get('password')

            if username == '' or username is None:
                errors['username'] = ['Este campo es requerido.']
            if password == '' or password is None:
                errors['password'] = ['Este campo es requerido.']

            if len(errors) > 0:
                return Response(errors, status=status.HTTP_401_UNAUTHORIZED)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid()

            # Generar token
            user = User.objects.get(username=username)
            serializer_data = serializer.validated_data
            return_data['refresh'] = serializer_data['refresh']
            return_data['token'] = serializer_data['access']
                
        except TokenError:
            return Response({'detail': ['Por favor validar el token']}, status=status.HTTP_401_UNAUTHORIZED)
        except exceptions.AuthenticationFailed as e:           
      
            return Response({'detail': ['Usuario o contraseña incorrectos']}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'detail': ['Ocurrio un error inesperado, por favor intentar nuevamente']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Arreglos para guardar la informaciÃon de roles y accesos del usuario.
        permission_list = []
        group_list = []

        # Arreglo de 2 dimensiones.
        # 0 - Nombres de los grupos.
        # 1 - Id de los grupos.
        GROUP_NAME_POS = 0
        GROUP_ID_POS = 1
        groups = list(zip(*user.groups.values_list('name', 'id')))
        try:
            # Tomar los nombres de los grupos para retornarlos.
            group_list = groups[GROUP_NAME_POS]
            # Tomar los nombres de los permisos para retornarlos.
            permission_list = list(Permission.objects.values_list('codename', flat=True).filter(group__id__in=groups[GROUP_ID_POS]))
            if not permission_list:
                return Response({'detail': ['El rol del usuario no tiene ningún permiso asignado, validar con el administrador del sistema.']}, status=status.HTTP_401_UNAUTHORIZED)
        except IndexError as e:
            if user.is_superuser:
                # Tomar los nombres de los permisos para retornarlos.
                permission_list = list(Permission.objects.values_list('codename', flat=True))
            else:
                return Response({'detail': ['El usuario no tiene ningún rol asignado, validar con el administrador del sistema.']}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'detail': ['Por favor validar la configuración del usuario con el administrador.']}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            login_type = user.user_data_user.login_type
        except Exception as e:
            login_type = None

        return_data['permissions'] = permission_list
        return_data['staff'] = user.is_staff
        return_data['superuser'] = user.is_superuser
        return_data['id'] = user.id
        return_data['full_name'] = user.first_name + ' ' + user.last_name
        return_data['groups'] = group_list
        return_data['login_type'] = login_type
        
        return Response(return_data, status=status.HTTP_200_OK)


class GetTokenView(TokenObtainPairView):
    '''
    Metodo para retornar token.
    '''

    authentication_classes = ()
    permission_classes = ()

    def post(self, request):

        try:
            # Inicializar objecto para almacenar los datos del usuarios.
            return_data = {}

            # Validar campos requeridos
            errors = {}

            username = request.data.get('username')
            password = request.data.get('password')

            if username == '' or username is None:
                errors['username'] = ['Este campo es requerido.']
            if password == '' or password is None:
                errors['password'] = ['Este campo es requerido.']

            if len(errors) > 0:
                return Response(errors, status=status.HTTP_401_UNAUTHORIZED)

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid()

            # Generar token
            user = User.objects.get(username=username)
            serializer_data = serializer.validated_data
            return_data['token'] = serializer_data['access']
                
        except TokenError as e:
            return Response({'detail': ['Por favor validar el token']}, status=status.HTTP_401_UNAUTHORIZED)
        except exceptions.AuthenticationFailed as e:
            
            return Response({'detail': ['Usuario o contraseña incorrectos']}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response({'detail': ['Ocurrio un error inesperado, por favor intentar nuevamente']}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(return_data, status=status.HTTP_200_OK)


class LoginAdminView(View):
    '''
    Clase para iniciar sesión.
    '''
    template_name = 'index.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        """
        Método que para iniciar session desde el administrador del api
        """

        usuariol = request.POST.get('username')
        passwordl = request.POST.get('password')

        if usuariol and passwordl:

            info = {'user': usuariol, 'password': passwordl}

            try:
                users = User.objects.get(username=usuariol)
            except ObjectDoesNotExist:
                messages.error(request, 'El usuario no se encuentra registrado en la aplicación.')
                return HttpResponseRedirect(reverse('login:login_admin'))

            user = authenticate(username=usuariol, password=passwordl)
            if user is not None:
                login(request, users)
                request.session.set_expiry(settings.SESSION_TIMEOUT)

                if not users.is_staff:
                    messages.error(request, 'El usuario es valido pero no tiene acceso al sitio de administración.')
                    return HttpResponseRedirect(reverse('login:login_admin'))

                return HttpResponseRedirect(reverse('admin:index'))

            try:
                ws_response = requests.post(settings.URL_AUTHENTICATION, data=info)
                ws_response.json()
                if ws_response.status_code == requests.codes.ok:

                    login(request, users)
                    request.session.set_expiry(settings.SESSION_TIMEOUT)
                    if not users.is_staff:
                        messages.error(request, 'El usuario es valido pero no tiene acceso al sitio de administración.')
                        return HttpResponseRedirect(reverse('login:login_admin'))
                    return HttpResponseRedirect(reverse('admin:index'))

                else:
                    messages.error(request, 'Nombre de usuario o Contraseña incorrectos.')
                    return HttpResponseRedirect(reverse('login:login_admin'))
            except Exception as e:
                messages.error(request, 'Actualmente no se puede ingresar a la aplicación por favor intente más tarde')
                return HttpResponseRedirect(reverse('login:login_admin'))
        else:
            messages.error(request, 'Nombre de usuario y contraseña son obligatorios.')
            return HttpResponseRedirect(reverse('login:login_admin'))


class LogoutView(APIView):
    '''
    Metodo para cerrar la sesión.
    '''

    def get(self, request):

        # El token llega con el formato "Toke <numero_token>" se ejecuta el split y se toma la segunda posicion...
        token_number = request.META.get('Autorization').split(' ')[1]
        try:
            token = Token.objects.get(key=token_number)
            user = token.user
            token.delete()

            Token.objects.create(user=user)
        except Token.DoesNotExist:
            return Response({'detail':['Token incorrecto']}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response({}, status=status.HTTP_202_ACCEPTED)
        return response
