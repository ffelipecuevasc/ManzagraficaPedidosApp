"""Las funciones de datos de prueba construyen objetos coherentes (02-01)."""
from datetime import timezone as tz_utc
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

    def test_momento_chile_es_mediodia_local_y_consciente(self):
        # Octubre de 2026 es horario de verano en Chile continental (UTC-3).
        momento = factorias.momento_chile(2026, 10, 15)
        self.assertIsNotNone(momento.utcoffset())
        self.assertEqual((momento.hour, momento.minute), (12, 0))
        self.assertEqual(momento.astimezone(tz_utc.utc).hour, 15)

    def test_pago_con_fecha_dada(self):
        fecha = factorias.momento_chile(2026, 9, 10)
        pago = factorias.crear_pago(monto=1_000, fecha=fecha)
        pago.refresh_from_db()
        self.assertEqual(pago.fecha, fecha)
