from django.contrib import admin
from .models import Cliente, Pedido, Cotizacion, Producto

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'email')
    search_fields = ('nombre', 'telefono')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'resumen_pedido', 'estado', 'fecha_entrega', 'valor_pendiente')
    list_filter = ('estado', 'fecha_entrega')
    search_fields = ('cliente__nombre', 'resumen_pedido')
    list_editable = ('estado',)
    list_per_page = 20

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio_venta', 'fecha_ingreso')
    search_fields = ('nombre',)
    list_filter = ('fecha_ingreso',)
    ordering = ('-fecha_ingreso',)