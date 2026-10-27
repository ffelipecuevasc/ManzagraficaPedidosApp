"""Flujos críticos de cotizaciones: pruebas de caracterización (iteración 02-03).

La doble conversión (AUD-02-005) y la pérdida de ítems al editar (AUD-01-002) son
regresiones de la 02-04. Las reglas sin confirmar llevan PENDIENTE_CLIENTE.
"""
from datetime import date
from decimal import Decimal

from django.test import TestCase

from pedidos.models import Cotizacion, Pago, Pedido, RegistroEvento

from . import ayudas
from .factorias import crear_cliente, crear_cotizacion, crear_producto, crear_usuario


class CotizacionBase(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)
        self.cliente = crear_cliente()
        self.producto = crear_producto(valor_neto=10_000)
        self.otro = crear_producto(valor_neto=4_000)

    def ejecutar(self, metodo, ruta, datos=None):
        with self.captureOnCommitCallbacks(execute=True):
            return getattr(self.client, metodo)(ruta, datos or {})

    def datos(self, **campos):
        datos = {
            'cliente': self.cliente.pk, 'resumen': 'Pendones', 'detalles': '<p>Detalle</p>',
            'valor_total': 30_000, 'validez': 15, 'fecha_emision': '2026-10-15',
            'items_json': ayudas.items_json((self.producto, '2', 10_000), (self.otro, '2.5', 4_000)),
        }
        datos.update(campos)
        return datos


class CrearCotizacionTests(CotizacionBase):
    def test_formulario_responde_con_la_fecha_de_hoy(self):
        with ayudas.congelar_hora():
            respuesta = self.client.get('/cotizaciones/nueva/')

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['fecha_hoy'], '2026-10-15')

    def test_post_valido_crea_cotizacion_con_items(self):
        respuesta = self.ejecutar('post', '/cotizaciones/nueva/', self.datos())

        cotizacion = Cotizacion.objects.get()
        self.assertRedirects(respuesta, f'/cotizaciones/detalle/{cotizacion.pk}/',
                             fetch_redirect_response=False)
        self.assertEqual((cotizacion.estado, cotizacion.valor_total), ('BORRADOR', 30_000))
        items = sorted(cotizacion.items.values_list('producto_id', 'cantidad', 'precio_unitario'))
        self.assertEqual(items, sorted([(self.producto.pk, Decimal('2.00'), 10_000),
                                        (self.otro.pk, Decimal('2.50'), 4_000)]))
        # Hoy crear una cotización no deja evento (no está en el inventario de 01-04).
        self.assertFalse(RegistroEvento.objects.exists())

    def test_fecha_de_vencimiento(self):
        self.ejecutar('post', '/cotizaciones/nueva/', self.datos(validez=10))

        self.assertEqual(Cotizacion.objects.get().fecha_vencimiento, date(2026, 10, 25))


class EditarCotizacionTests(CotizacionBase):
    def setUp(self):
        super().setUp()
        self.cotizacion = crear_cotizacion(cliente=self.cliente, valor_total=10_000, items=[
            {'producto': self.producto, 'cantidad': '1', 'precio_unitario': 10_000}])

    def test_cambia_campos_y_reemplaza_items(self):
        respuesta = self.ejecutar('post', f'/cotizaciones/editar/{self.cotizacion.pk}/', self.datos(
            resumen='Pendones editados', items_json=ayudas.items_json((self.otro, '3', 4_000))))

        self.assertRedirects(respuesta, f'/cotizaciones/detalle/{self.cotizacion.pk}/',
                             fetch_redirect_response=False)
        self.cotizacion.refresh_from_db()
        self.assertEqual((self.cotizacion.resumen, self.cotizacion.valor_total),
                         ('Pendones editados', 30_000))
        self.assertEqual(list(self.cotizacion.items.values_list('producto_id', 'cantidad')),
                         [(self.otro.pk, Decimal('3.00'))])

    def test_aceptada_no_se_edita(self):
        self.cotizacion.estado = 'ACEPTADA'
        self.cotizacion.save()

        for metodo in ('get', 'post'):
            with self.subTest(metodo=metodo):
                respuesta = self.ejecutar(metodo, f'/cotizaciones/editar/{self.cotizacion.pk}/',
                                          self.datos(resumen='No debe cambiar'))
                self.assertRedirects(respuesta, f'/cotizaciones/detalle/{self.cotizacion.pk}/',
                                     fetch_redirect_response=False)
        self.cotizacion.refresh_from_db()
        self.assertNotEqual(self.cotizacion.resumen, 'No debe cambiar')
        self.assertEqual(self.cotizacion.items.count(), 1)


class ConvertirCotizacionTests(CotizacionBase):
    def setUp(self):
        super().setUp()
        self.cotizacion = crear_cotizacion(
            cliente=self.cliente, resumen='Letrero', detalles='<p>Letrero luminoso</p>',
            valor_total=50_000, estado='ENVIADA', items=[
                {'producto': self.producto, 'cantidad': '2', 'precio_unitario': 10_000},
                {'producto': self.otro, 'cantidad': '1.5', 'precio_unitario': 4_000}])
        self.ruta = f'/cotizaciones/convertir/{self.cotizacion.pk}/'

    def convertir(self, **campos):
        datos = {'fecha_entrega': '2026-10-30', 'valor_abonado': '0'}
        datos.update(campos)
        respuesta = self.ejecutar('post', self.ruta, datos)
        return respuesta, Pedido.objects.get()

    def test_pantalla_sugiere_entrega_en_siete_dias(self):
        with ayudas.congelar_hora():
            respuesta = self.client.get(self.ruta)

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['fecha_sugerida'], date(2026, 10, 22))

    def test_copia_cabecera_items_y_cierra_la_cotizacion(self):
        respuesta, pedido = self.convertir()

        self.assertRedirects(respuesta, f'/{pedido.pk}/', fetch_redirect_response=False)
        self.assertEqual(
            (pedido.cliente, pedido.resumen_pedido, pedido.detalles_pedido, pedido.fecha_entrega,
             pedido.estado, pedido.creado_por),
            (self.cliente, 'Letrero', '<p>Letrero luminoso</p>', date(2026, 10, 30),
             'PENDIENTE', self.usuario))
        self.assertEqual(
            sorted(pedido.items.values_list('producto_id', 'cantidad', 'precio_unitario')),
            sorted(self.cotizacion.items.values_list('producto_id', 'cantidad', 'precio_unitario')))
        self.cotizacion.refresh_from_db()
        self.assertEqual(self.cotizacion.estado, 'ACEPTADA')
        self.assertEqual(list(RegistroEvento.objects.values_list('tipo', flat=True)),
                         ['cotizacion_convertida'])

    def test_valor_venta_es_el_valor_total_sin_iva(self):
        # PENDIENTE_CLIENTE (AUD-02-014): ¿el valor de la cotización es neto o incluye IVA?
        # Hoy se copia tal cual: no se suma IVA ni se compara con la suma de los ítems
        # (aquí 26.000 neto en ítems frente a 50.000 de valor total).
        _, pedido = self.convertir()

        self.assertEqual(pedido.valor_venta, self.cotizacion.valor_total)
        self.assertEqual(pedido.valor_venta, 50_000)

    def test_abono(self):
        # (descripción, valor_abonado enviado, método enviado, monto del pago o None,
        #  método guardado, estado_pago)
        casos = [
            ('sin abono', '0', None, None, None, 'PENDIENTE'),
            ('abono parcial, método por defecto', '20000', None, 20_000, 'TRANSFERENCIA', 'PARCIAL'),
            ('abono total con método', '50000', 'EFECTIVO', 50_000, 'EFECTIVO', 'PAGADO'),
            ('abono no numérico', 'veinte', None, None, None, 'PENDIENTE'),
            ('abono negativo', '-5000', None, None, None, 'PENDIENTE'),
        ]
        for descripcion, abono, metodo, monto, metodo_guardado, estado_pago in casos:
            with self.subTest(descripcion):
                Pedido.objects.all().delete()
                datos = {'valor_abonado': abono}
                if metodo:
                    datos['metodo_pago'] = metodo

                _, pedido = self.convertir(**datos)

                pago = Pago.objects.filter(pedido=pedido).first()
                if monto is None:
                    self.assertIsNone(pago)
                else:
                    self.assertEqual((pago.monto, pago.metodo, pago.registrado_por),
                                     (monto, metodo_guardado, self.usuario))
                    self.assertEqual(pago.nota, f'Abono inicial por conversión de Cotización #{self.cotizacion.pk}')
                self.assertEqual(pedido.estado_pago, estado_pago)
