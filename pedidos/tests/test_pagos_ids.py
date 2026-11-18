"""Pagos de pedidos con id desde 1.000 y selector de pedidos (14-01, AUD-05-010 y AUD-05-011).

Con `LANGUAGE_CODE = 'es-cl'` y `USE_THOUSAND_SEPARATOR = True`, `{{ x.id }}` escribe el id con
separador de miles (un espacio duro en el formato de Django para «es»): el pedido 1002 sale
«1\xa0002» y el formulario lo rechaza como opción no válida.
"""
import re

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from pedidos.models import Pago, RegistroEvento

from . import ayudas
from .factorias import crear_cliente, crear_pago, crear_pedido, crear_producto, crear_usuario

TEXTO_PEDIDO_NO_VALIDO = 'No se reconoció el pedido. Vuelve a abrir el pago desde el pedido o elígelo en la lista.'


def _valor_oculto_pedido(respuesta):
    coincidencia = re.search(r'<input type="hidden" name="pedido" value="([^"]*)"', respuesta.content.decode())
    return coincidencia.group(1) if coincidencia else None


class PagoPedidoGrandeTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_usuario('cajero'))
        self.pedido = crear_pedido(id=1002, valor_venta=10_000)
        self.ruta = '/pagos/ingresar/1002/'

    def test_t1_pago_desde_pedido_grande_se_guarda(self):
        respuesta = self.client.get(self.ruta)
        self.assertEqual(respuesta.status_code, 200)
        valor = _valor_oculto_pedido(respuesta)
        self.assertEqual(valor, '1002')
        self.assertNotContains(respuesta, 'Pedido #1\xa0002')

        datos = {'pedido': valor, 'monto': '4000', 'metodo': 'EFECTIVO', 'nota': '',
                 'token_envio': ayudas.token_de(respuesta)}
        with self.captureOnCommitCallbacks(execute=True):  # el evento se escribe en on_commit
            envio = self.client.post(self.ruta, datos)

        self.assertRedirects(envio, '/pagos/lista/', fetch_redirect_response=False)
        self.assertEqual(Pago.objects.filter(pedido=self.pedido).count(), 1)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado_pago, 'PARCIAL')
        self.assertTrue(RegistroEvento.objects.filter(tipo='pago_registrado').exists())

    def test_t2_error_de_pedido_se_ve(self):
        datos = ayudas.con_token(self.client, self.ruta, {
            'pedido': '1\xa0002', 'monto': '4000', 'metodo': 'EFECTIVO', 'nota': ''})
        respuesta = self.client.post(self.ruta, datos)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Pago.objects.count(), 0)
        self.assertContains(respuesta, 'id="error-pedido"')
        self.assertContains(respuesta, 'role="alert"')
        self.assertContains(respuesta, TEXTO_PEDIDO_NO_VALIDO)


class IdProductoTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_usuario('vendedor'))
        crear_producto(id=1002)

    def test_t3_id_de_producto_sin_separador_en_pedido(self):
        respuesta = self.client.get('/pedidos/nuevo/')
        self.assertContains(respuesta, '<option value="1002"')
        self.assertNotContains(respuesta, 'value="1\xa0002"')

    def test_t3_id_de_producto_sin_separador_en_cotizacion(self):
        respuesta = self.client.get('/cotizaciones/nueva/')
        self.assertContains(respuesta, '<option value="1002"')
        self.assertNotContains(respuesta, 'value="1\xa0002"')


class SelectorPedidosConsultasTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_usuario('cajero'))

    def _crear_pedidos(self, cantidad):
        for _ in range(cantidad):
            crear_pedido(cliente=crear_cliente(), valor_venta=10_000)

    def _consultas(self, ruta):
        with CaptureQueriesContext(connection) as contexto:
            respuesta = self.client.get(ruta)
        self.assertEqual(respuesta.status_code, 200)
        return len(contexto.captured_queries)

    def test_t4_ingresar_pago_no_hace_una_consulta_por_pedido(self):
        self._crear_pedidos(3)
        con_3 = self._consultas('/pagos/ingresar/')
        self._crear_pedidos(27)
        con_30 = self._consultas('/pagos/ingresar/')
        self.assertEqual(con_3, con_30)

    def test_t5_editar_pago_no_hace_una_consulta_por_pedido(self):
        self._crear_pedidos(2)
        pago = crear_pago(pedido=crear_pedido(valor_venta=10_000))
        ruta = f'/pagos/editar/{pago.pk}/'
        con_3 = self._consultas(ruta)
        self._crear_pedidos(27)
        con_30 = self._consultas(ruta)
        self.assertEqual(con_3, con_30)
