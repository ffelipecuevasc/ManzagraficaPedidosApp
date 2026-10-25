"""Las funciones de datos de prueba construyen objetos coherentes (02-01)."""
from decimal import Decimal

from django.test import TestCase

from . import factorias


class FactoriasTests(TestCase):
    def test_pedido_con_items_y_pago(self):
        pedido = factorias.crear_pedido(items=[{'cantidad': '2.5', 'precio_unitario': 4_000}])
        factorias.crear_pago(pedido, monto=3_000)
        item = pedido.items.get()
        self.assertEqual(item.cantidad, Decimal('2.50'))
        self.assertEqual(item.subtotal, Decimal('10000'))
        self.assertEqual(pedido.pagos.count(), 1)

    def test_cotizacion_con_items(self):
        cotizacion = factorias.crear_cotizacion(items=[{}, {'cantidad': 3}])
        self.assertEqual(cotizacion.items.count(), 2)

    def test_valores_unicos_por_llamada(self):
        self.assertNotEqual(factorias.crear_usuario().username, factorias.crear_usuario().username)
        self.assertNotEqual(factorias.crear_cliente().nombre, factorias.crear_cliente().nombre)
