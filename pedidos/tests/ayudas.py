"""Ayudas para las pruebas de flujos (iteración 02-03).

- `items_json`: arma el campo oculto `items_json` que envía el JavaScript de los formularios.
- `cambiar_estado` y `duplicar`: concentran el método HTTP ACTUAL de esas rutas (GET).
  Cuando la 04-01 las pase a POST, se cambia solo aquí (y las pruebas que lo declaran).
- `congelar_hora`: fija `timezone.now()` donde lo buscan las vistas (decisión D3 de la 02-02).
  Es la única definición: `test_dinero.py` la importa desde aquí (tarea 0 de la 02-04).
- `cerrar_respuesta`: cierra un `FileResponse` sin romper la transacción de la prueba (02-05).
- `estado_pago_esperado`: oráculo de `estado_pago` para las regresiones R10 a R12 (02-04).
"""
import json
import re
from unittest import mock

from django.core.signals import request_finished
from django.db import close_old_connections

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


def cerrar_respuesta(respuesta):
    """Cierra la respuesta (y el archivo de un `FileResponse`) sin cerrar la conexión.

    `respuesta.close()` emite `request_finished`, que llama a `close_old_connections`: dentro
    de la transacción de `TestCase` eso deja la conexión marcada para revertir y la siguiente
    consulta falla. El cliente de pruebas de Django desconecta la misma señal en cada petición.
    """
    request_finished.disconnect(close_old_connections)
    try:
        respuesta.close()
    finally:
        request_finished.connect(close_old_connections)


# Textos aprobados por el desarrollador el 2026-11-04 (03-04). Se escriben literales a propósito:
# si el texto de la aplicación cambia, las pruebas lo notan.
TEXTO_ITEM_FALLIDO = ('No pudimos guardar el detalle de productos. Lo que escribiste sigue en pantalla: '
                      'revísalo y vuelve a guardar. Si el problema sigue, avisa en qué pantalla estabas y a qué hora.')
TEXTO_FORMULARIO_VENCIDO = 'Este formulario venció y no se guardó. Revisa los datos y vuelve a guardar.'
TEXTO_IMAGEN = 'Vuelve a elegir la imagen de referencia: el navegador no la conserva.'
TEXTO_PAGINA_500 = 'Si el problema sigue, avísale al administrador y cuéntale en qué pantalla estabas y a qué hora.'


def token_de(respuesta):
    """Token de envío único de un formulario (03-04): el campo oculto `token_envio`, o '' si no hay."""
    coincidencia = re.search(r'name="token_envio" value="([^"]+)"', respuesta.content.decode())
    return coincidencia.group(1) if coincidencia else ''


# Rutas de creación que exigen el token de envío único (03-04, decisión 7-A).
RUTAS_CON_TOKEN = ('/pedidos/nuevo/', '/cotizaciones/nueva/', '/pagos/ingresar/')


def con_token(client, ruta, datos):
    """Devuelve `datos` con el token que el navegador recibiría al abrir el formulario.

    Solo para las rutas de creación; si `datos` ya trae `token_envio`, no lo toca. Las pruebas del
    contrato del token no lo usan: arman el envío a mano.
    """
    if not ruta.startswith(RUTAS_CON_TOKEN) or 'token_envio' in datos:
        return datos
    return {**datos, 'token_envio': token_de(client.get(ruta))}
