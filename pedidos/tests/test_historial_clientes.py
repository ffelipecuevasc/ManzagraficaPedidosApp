"""Protección del historial al eliminar un cliente (04-06, AUD-02-001).

`Pedido.cliente` y `Cotizacion.cliente` pasan a `PROTECT`: un cliente con pedidos o
cotizaciones no se borra y la pantalla dice por qué (D1). La confirmación avisa antes, sin
contar ni ocultar el botón (D2). El rechazo no registra evento (D3). R14 vive en
`test_regresiones.py`; aquí van las pruebas de D4.

TestCase nunca confirma su transacción: los `on_commit` se ejecutan con
`captureOnCommitCallbacks(execute=True)`.
"""
from django.db.models import ProtectedError
from django.test import TestCase

from pedidos.models import Cliente, Cotizacion, ItemCotizacion, ItemPedido, Pago, Pedido, RegistroEvento

from . import factorias

MENSAJE_D1 = ('No se puede eliminar este cliente porque tiene pedidos o cotizaciones registrados. '
              'Para conservar su historial, no está permitido borrarlo.')
AVISO_D2 = 'Solo se puede eliminar un cliente sin pedidos ni cotizaciones'


def ruta(cliente):
    return f'/clientes/eliminar/{cliente.pk}/'


class ModeloProtegeHistorialTests(TestCase):
    def test_cliente_con_solo_una_cotizacion_no_se_borra(self):
        cliente = factorias.crear_cliente()
        cotizacion = factorias.crear_cotizacion(cliente=cliente, items=[{}])

        with self.assertRaises(ProtectedError):
            cliente.delete()

        self.assertTrue(Cotizacion.objects.filter(pk=cotizacion.pk).exists())
        self.assertEqual(ItemCotizacion.objects.filter(cotizacion=cotizacion).count(), 1)


class VistaEliminarClienteTests(TestCase):
    def setUp(self):
        self.client.force_login(factorias.crear_superusuario())

    def test_con_historial_rechaza_con_mensaje_y_sin_evento(self):
        cliente = factorias.crear_cliente()
        pedido = factorias.crear_pedido(cliente=cliente, items=[{}], valor_venta=10_000)
        factorias.crear_pago(pedido, monto=4_000)
        eventos_antes = RegistroEvento.objects.count()

        with self.captureOnCommitCallbacks(execute=True):
            respuesta = self.client.post(ruta(cliente))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, MENSAJE_D1)
        self.assertEqual(RegistroEvento.objects.count(), eventos_antes)
        self.assertTrue(Cliente.objects.filter(pk=cliente.pk).exists())
        self.assertTrue(Pedido.objects.filter(pk=pedido.pk).exists())
        self.assertEqual(ItemPedido.objects.filter(pedido=pedido).count(), 1)
        self.assertEqual(Pago.objects.filter(pedido=pedido).count(), 1)

    def test_sin_historial_se_borra_y_registra_un_evento(self):
        cliente = factorias.crear_cliente()

        with self.captureOnCommitCallbacks(execute=True):
            respuesta = self.client.post(ruta(cliente))

        self.assertRedirects(respuesta, '/clientes/lista/', fetch_redirect_response=False)
        self.assertFalse(Cliente.objects.filter(pk=cliente.pk).exists())
        self.assertEqual(
            RegistroEvento.objects.filter(tipo='cliente_eliminado', entidad_id=cliente.pk).count(), 1)

    def test_confirmacion_avisa_y_conserva_el_boton(self):
        cliente = factorias.crear_cliente()

        respuesta = self.client.get(ruta(cliente))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, AVISO_D2)
        self.assertContains(respuesta, 'Sí, Eliminar')
        self.assertNotContains(respuesta, MENSAJE_D1)
