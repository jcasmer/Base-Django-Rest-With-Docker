# -*- coding: utf-8 -*-

import json

from django.contrib.auth.models import Group, User, Permission
from django.urls import reverse

from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.metadata import SimpleMetadata


def validate_permission(type, permission_code, request):
    try:
        permission_name_user = '{}.{}_{}'.format('auth', type, permission_code)
        permission_name_app = '{}.{}_{}'.format('app', type, permission_code)

        if permission_code == 'user':
            if not request.user.has_perm(permission_name_user):
                return Response({'detail': 'No tiene permisos para ejecutar esta acción'}, status=403)
        elif not request.user.has_perm(permission_name_app):
            return Response({'detail': 'No tiene permisos para ejecutar esta acción'}, status=403)
    except AttributeError:
        return Response({'detail': 'No tiene permisos para ejecutar esta acción'}, status=403)
    except Exception:
        return Response({'detail': 'Error inesperado validando permisos.'}, status=402)

    return True


class BaseViewSet(viewsets.ModelViewSet):

    permission_code = None

    def initialize_request(self, request, *args, **kwargs):
        return super().initialize_request(request, *args, **kwargs)

    @list_route(methods=['post'])
    def info(self, request):

        simple_metadata = SimpleMetadata()
        metedata = simple_metadata.determine_metadata(request, self)
        metedata_serializer = {}
        metedata_serializer['fields'] = metedata['actions']['POST']
        metedata_serializer['name'] = metedata['name']
        metedata_serializer['description'] = metedata['description']

        try:
            new_info_data = json.loads(json.dumps(self.serializer_class.info_data))
        except AttributeError as error:
            new_info_data = {}

        for key, value in new_info_data['fields'].items():
            if key in metedata_serializer['fields']:

                # Filtros.
                try:
                    metedata_serializer['fields'][key]['filters'] = self.filter_class.Meta.fields[key]
                except KeyError:
                    pass

                # Ordenamiento.
                metedata_serializer['fields'][key]['ordering'] = True if key in self.ordering_fields else False

                try:
                    for choice in metedata_serializer['fields'][key]['choices']:
                        choice['label'] = choice['display_name']
                except KeyError:
                    pass

                if 'source' in value:
                    value['source']['url'] = request.build_absolute_uri(reverse(value['source']['url']))
                metedata_serializer['fields'][key].update(value)

        metedata_serializer['order'] = new_info_data['order']

        return Response(metedata_serializer)

    def list(self, request):
        permission = validate_permission('list', self.permission_code, request)
        if not permission is True:
            return permission

        if request.GET.get('nopaginate'):
            self.pagination_class = None
        return super().list(request)

    def create(self, request):
        permission = validate_permission('add', self.permission_code, request)
        if not permission is True:
            return permission

        return super().create(request)

    def retrieve(self, request, pk=None):
        permission = validate_permission('retrieve', self.permission_code, request)
        if not permission is True:
            return permission

        return super().retrieve(request, pk)

    def update(self, request, pk=None):
        permission = validate_permission('change', self.permission_code, request)
        if not permission is True:
            return permission

        return super().update(request, pk)

    def partial_update(self, request, pk=None):
        permission = validate_permission('change', self.permission_code, request)
        if not permission is True:
            return permission

        return super().partial_update(request, pk)

    def destroy(self, request, pk=None):
        permission = validate_permission('delete', self.permission_code, request)
        if not permission is True:
            return permission

        return super().destroy(request, pk)
