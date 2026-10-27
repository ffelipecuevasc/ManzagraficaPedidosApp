"""Ayudas para las pruebas de flujos (iteración 02-03).

- `items_json`: arma el campo oculto `items_json` que envía el JavaScript de los formularios.
- `cambiar_estado` y `duplicar`: concentran el método HTTP ACTUAL de esas rutas (GET).
  Cuando la 04-01 las pase a POST, se cambia solo aquí (y las pruebas que lo declaran).
- `congelar_hora`: fija `timezone.now()` donde lo buscan las vistas (decisión D3 de la 02-02).
  Es la única definición: `test_dinero.py` la importa desde aquí (tarea 0 de la 02-04).
- `estado_pago_esperado`: oráculo de `estado_pago` para las regresiones R10 a R12 (02-04).
"""
import json
from unittest import mock

from .factorias import momento_chile

# Mediodía de Chile, lejos de los bordes de día y de mes en UTC (AUD-02-003, 02-04).
MEDIODIA = momento_chile(2026, 10, 15)


def items_json(*items):
    """`items` son tuplas (producto, cantidad, precio_unitario), como las envía el navegador."""
    return json.dumps([
        {'producto_id': str(producto.pk), 'cantidad': str(cantidad), 'precio_unitario': precio}
        for producto, cantidad, precio in items
    ])


def cambiar_estado(client, pedido, estado):
    # Escribe con GET hoy (AUD-01-003); la 04-01 lo cambia a POST.
    return client.get(f'/pedido/{pedido.pk}/cambiar/{estado}/')


def duplicar(client, pedido):
    # Escribe con GET hoy (AUD-01-003); la 04-01 lo cambia a POST.
    return client.get(f'/pedido/duplicar/{pedido.pk}/')


def congelar_hora(momento=MEDIODIA):
    """Las vistas usan `timezone.now()` del módulo: se parcha `django.utils.timezone.now`.

    No alcanza a los `default=timezone.now` de los modelos (quedan ligados a la función
    original al cargar la clase): esas fechas se pasan explícitas o se acotan con el reloj.
    """
    return mock.patch('django.utils.timezone.now', return_value=momento)


def estado_pago_esperado(pedido):
    """Oráculo de `estado_pago` (02-04, tarea 2), con la regla de
    `scripts/diagnostico/linea_base.sql`: `PAGADO` si el saldo es menor o igual a 0;
    `PARCIAL` si hay pagos; `PENDIENTE` si no. Suma los pagos en Python, sin usar las
    propiedades del modelo ni la función de la vista.
    """
    pagado = sum(pago.monto for pago in pedido.pagos.all())
    if pedido.valor_venta - pagado <= 0:
        return 'PAGADO'
    if pagado > 0:
        return 'PARCIAL'
    return 'PENDIENTE'
