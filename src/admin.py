def delete_selected(modeladmin, request, queryset):
    '''
    Para evitar la eliminación nativa de los elementos en el admin, se modifica
    para realizar un update con deleted=True
    '''
    queryset.update(deleted=True)

delete_selected.short_description = 'Eliminar seleccionados'


def activate_selected(modeladmin, request, queryset):
    '''
    Activa los elementos seleccionados
    '''
    queryset.update(is_active=True)

activate_selected.short_description = 'Activar seleccionados'


def inactivate_selected(modeladmin, request, queryset):
    '''
    Activa los elementos seleccionados
    '''
    queryset.update(is_active=False)

inactivate_selected.short_description = 'Inactivar seleccionados'