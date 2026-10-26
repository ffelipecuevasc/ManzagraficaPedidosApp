"""Funciones que construyen datos de prueba coherentes bajo demanda (iteración 02-01).

Reglas (docs/operacion/pruebas.md):
- Valores por defecto válidos; cada prueba pasa solo lo que le importa.
- Datos ficticios: nunca nombres, teléfonos ni montos copiados de la réplica.
- Montos enteros en pesos; cantidades con Decimal; fechas con timezone.
- No aplican reglas de negocio de las vistas (por ejemplo, no recalculan `valor_venta`
  ni `estado_pago`): eso es lo que prueban 02-02 y 02-03.
"""
from datetime import datetime
from decimal import Decimal
from itertools import count
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.utils import timezone

from pedidos.models import (
    Cliente, Cotizacion, ItemCotizacion, ItemPedido, Pago, Pedido, Producto, RegistroEvento,
)

_correlativo = count(1)

ZONA_CHILE = ZoneInfo('America/Santiago')


def momento_chile(anio, mes, dia, hora=12, minuto=0):
    """Instante consciente en hora de Chile (por defecto, mediodía), para fechas de prueba (02-02)."""
    return datetime(anio, mes, dia, hora, minuto, tzinfo=ZONA_CHILE)


def _siguiente():
    return next(_correlativo)


def crear_usuario(username=None, password='clave-prueba-123', **campos):
    username = username or f'usuario{_siguiente()}'
    return get_user_model().objects.create_user(username, password=password, **campos)


def crear_superusuario(username=None, password='clave-prueba-123', **campos):
    username = username or f'admin{_siguiente()}'
    return get_user_model().objects.create_superuser(username, password=password, **campos)


def crear_cliente(**campos):
    n = _siguiente()
    datos = {'nombre': f'Cliente de prueba {n}', 'telefono': '+56 9 0000 0000'}
    datos.update(campos)
    return Cliente.objects.create(**datos)


def crear_producto(valor_neto=10_000, **campos):
    datos = {'nombre': f'Producto de prueba {_siguiente()}', 'valor_neto': valor_neto}
    datos.update(campos)
    return Producto.objects.create(**datos)  # save() calcula iva y valor_bruto


def crear_pedido(cliente=None, items=(), **campos):
    """Crea un pedido. `items` es una lista de diccionarios para `crear_item_pedido`."""
    datos = {
        'cliente': cliente or crear_cliente(),
        'resumen_pedido': f'Pedido de prueba {_siguiente()}',
        'valor_venta': 0,
    }
    datos.update(campos)
    pedido = Pedido.objects.create(**datos)
    for item in items:
        crear_item_pedido(pedido, **item)
    return pedido


def crear_item_pedido(pedido, producto=None, cantidad='1', precio_unitario=10_000):
    return ItemPedido.objects.create(
        pedido=pedido, producto=producto or crear_producto(),
        cantidad=Decimal(str(cantidad)), precio_unitario=precio_unitario,
    )


def crear_pago(pedido=None, monto=5_000, **campos):
    datos = {'pedido': pedido or crear_pedido(), 'monto': monto}
    datos.update(campos)
    return Pago.objects.create(**datos)


def crear_cotizacion(cliente=None, items=(), **campos):
    """Crea una cotización. `items` es una lista de diccionarios para `crear_item_cotizacion`."""
    datos = {
        'cliente': cliente or crear_cliente(),
        'resumen': f'Cotización de prueba {_siguiente()}',
        'detalles': 'Detalle de prueba',
        'valor_total': 0,
        'fecha_emision': timezone.localdate(),
    }
    datos.update(campos)
    cotizacion = Cotizacion.objects.create(**datos)
    for item in items:
        crear_item_cotizacion(cotizacion, **item)
    return cotizacion


def crear_item_cotizacion(cotizacion, producto=None, cantidad='1', precio_unitario=10_000):
    return ItemCotizacion.objects.create(
        cotizacion=cotizacion, producto=producto or crear_producto(),
        cantidad=Decimal(str(cantidad)), precio_unitario=precio_unitario,
    )


def crear_evento(momento=None, tipo='pedido_creado', usuario=None, entidad='pedido',
                 entidad_id=1, resumen=None):
    return RegistroEvento.objects.create(
        momento=momento or timezone.now(), tipo=tipo, usuario=usuario,
        entidad=entidad, entidad_id=entidad_id,
        resumen=resumen or f'{entidad.capitalize()} #{entidad_id}',
    )
