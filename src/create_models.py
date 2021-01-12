'''
Vista para la creación dinámica de modelos
'''
import re

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.db import models, connection
from rest_framework import serializers


def destroy_model(name):
    '''
    Método encargado de la eliminación de los modelos en la base de
    datos
    '''
    cursor = connection.cursor()
    cursor.execute('DROP TABLE IF EXISTS %s;' % (name,))
    return True

class GenerateModel:
    '''
    Clase para la validación de los modelos a crear
    '''

    def __init__(self, input_json):
        '''
        Método contructor encargado de inicializar atributos
        Parámetros:
        input_json -- JSON ingresado
        '''
 
        self.jsonname = input_json['model']
        self.jsonfields = input_json['fields']
        self.app_label = 'db'
        self.model_name = self.set_name()

    def define_model(self, name, fields):
        '''
        Método encargado de la definición de los modelos a crear. 

        Parámetros:
        name -- nombre del modelo a ser creado
        fields -- diccionario de campos tendrá el modelo

        Retorna el modelo a crear.
        '''

        class Meta:
            pass
        # Nombre arbitrario del módulo para ser usado como fuente del
        # modelo
        module = ''
        # Etiqueta de aplicación personalizada para el modelo
        app_label = self.app_label
        # Establecimiento de app_label utilizando la clase Meta
        setattr(Meta, 'app_label', app_label)
        # Establecimiento de un diccionario para la simulación de las
        # declaraciones dentro de una clase
        attrs = {
            '__module__': module,
            'Meta': Meta,
        }
        # Adición de los campos del modelo en el diccionario attrs
        attrs.update(fields)

        # Definción del modelo mediante el uso de type()
        model = type(name, (models.Model,), attrs)

        return model

    def set_fields(self):
        '''
        Método encargado de adaptar los campos que contendrá el modelo.

        Retorna un diccionario con los campos del modelo usando la 
        convención de nombres lower_case_with_underscores.
        '''
        # Diccionario creado para el ingreso de elementos
        dict_fields = {}
        for fields_content in self.jsonfields:
            name_field = fields_content['name']
            name_field = name_field.lower()
            dict_fields[name_field] = models.CharField(blank=True, null=True, max_length=1000)
        return dict_fields

    def set_name(self):
        '''
        Método encargado de adaptar el nombre que tendrá el modelo.

        Retorna un valor tipo cadena con el nombre del modelo usando la
        convención de nombres lower_case_with_underscores.
        '''

        self.jsonname = self.jsonname.lower()
        self.jsonname = self.jsonname

        return self.jsonname
  

    def create_model(self):
        '''
        Método encargado de la creación de los modelos en la base de
        datos
        '''
        name = self.app_label + "_" + self.model_name
        destroy_model(name)
        # Usando SchemaEditor es creado el modelo definido previamente
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(self.define_model(self.model_name, self.set_fields()))

def get_model(name_model, label_table, fields):
    '''
    Creación de modelo dinamico usando un type para crear una clase manualmente.
    '''

    # Creamos una clase meta y posteriormente le agregamos atributos
    class Meta:
        pass

    structure = {}

    # Se le agregan atributos a la clase meta creada anteriormente
    setattr(Meta, 'app_label', label_table)
    attrs = {
        '__module__': '',
        'Meta': Meta,
    }

    # Por cada uno de los campos de la estructura de la campaña se crea un charfield estandar para ser usado por el ORM
    for field in fields:
        structure[field] = models.CharField(max_length=1000, blank=True, null=True)

    # cargamos la estructura en los attrs
    attrs.update(structure)

    # Creamos la clase del modelo haciendo uso de la función de python TYPE y le pasamos los attrs creados
    model = type(name_model, (models.Model,), attrs)

    return model


def get_serializer(model):
    '''
    Creación de serialiador dinámico el cual recibe una clase modelo y unos fields para poder
    '''

    attrs = {}

    # Creamos una clase meta y posteriormente le agregamos atributos
    expand = serializers.SerializerMethodField()

    def get_expand(self, obj):
        return False

    class Meta:
        pass

    # Le agregamos a la clase meta el model y los fields
    setattr(Meta, 'model', model)
    setattr(Meta, 'fields', '__all__')
    attrs['info_data'] = {
        'order': {},
        'fields': {}
    }
    attrs['Meta'] = Meta
    attrs['expand'] = expand
    # Se usa la función TYPE de python para crear el serializador haciendo uso de los attrs creados
    serializer = type('model', (serializers.ModelSerializer,), attrs)
    serializer.get_expand = get_expand

    return serializer
