from django.contrib import admin
from django.utils import timezone

from .models import Cliente, Pedido, Cotizacion, Producto, RegistroEvento

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email')
    search_fields = ('nombre', 'telefono')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'resumen_pedido', 'estado', 'fecha_entrega', 'saldo_pendiente')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('cliente__nombre', 'resumen_pedido')
    list_editable = ('estado',)
    list_per_page = 20

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad', 'valor_neto', 'iva', 'valor_bruto', 'fecha_ingreso')
    search_fields = ('nombre',)
    readonly_fields = ('iva', 'valor_bruto')

@admin.register(RegistroEvento)
class RegistroEventoAdmin(admin.ModelAdmin):
    """Consulta de eventos de negocio (01-05): solo lectura y solo superusuarios."""
    list_display = ('momento_chile', 'tipo', 'usuario', 'entidad', 'entidad_id', 'resumen')
    list_filter = (('momento', admin.DateFieldListFilter), 'tipo',
                   ('usuario', admin.RelatedOnlyFieldListFilter))
    search_fields = ('=entidad_id',)  # número exacto: pedido, pago, cliente…
    search_help_text = 'Busca por el identificador de la entidad (por ejemplo, el número de pedido).'
    list_select_related = ('usuario',)
    ordering = ('-momento',)
    list_per_page = 50
    fields = readonly_fields = ('momento_chile', 'tipo', 'usuario', 'entidad', 'entidad_id', 'resumen')

    @admin.display(description='Momento (hora de Chile)', ordering='momento')
    def momento_chile(self, obj):
        local = timezone.localtime(obj.momento)
        return f'{local:%d-%m-%Y %H:%M:%S} (UTC{local:%z})'   # p. ej. «… (UTC-0300)»

    def has_module_permission(self, request):
        return request.user.is_active and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_superuser

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
