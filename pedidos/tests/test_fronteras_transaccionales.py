"""Fronteras transaccionales por vista (iteración 03-03, RDA-019).

Cada vista que escribe más de una fila relacionada lo hace dentro de un único
`transaction.atomic()` y la excepción sale del bloque: si algo falla, no queda nada a medias
en la base. El aviso al usuario y la conservación del formulario son de la 03-04: mientras
tanto, un fallo del sistema responde la página 500 de la 01-03 (decisión 1 del 2026-11-04).

El cliente de pruebas no relanza la excepción (`raise_request_exception = False`), para ver lo
que recibe el usuario. TestCase no confirma la transacción: los eventos (`on_commit`) se
ejecutan con `captureOnCommitCallbacks(execute=True)`.
"""
import inspect
import json
from decimal import Decimal
from unittest import mock

from django.test import TestCase, override_settings

from pedidos import views
from pedidos.models import Cotizacion, ItemCotizacion, ItemPedido, Pago, Pedido, RegistroEvento

from . import ayudas
from .factorias import (
    crear_cliente, crear_cotizacion, crear_pago, crear_pedido, crear_producto, crear_usuario,
)
from .test_registro import formatear_como_error_log


class FronteraBase(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)

    def ejecutar(self, metodo, ruta, datos=None):
        with self.captureOnCommitCallbacks(execute=True):
            return getattr(self.client, metodo)(ruta, datos or {})

    def eventos(self):
        return RegistroEvento.objects.count()

    def falla_al_final(self):
        """Simula un fallo cualquiera después de las escrituras, justo antes de terminar la vista.

        `registrar_evento` es lo último que ejecutan estas vistas dentro del bloque.
        """
        return mock.patch.object(views, 'registrar_evento', side_effect=RuntimeError('falla de prueba'))


# ---------------------------------------------------------------------------
# Ítems que fallan: pedido (edición) y cotizaciones (creación y edición)
# ---------------------------------------------------------------------------
class CasosDeItemFallido:
    """Las cinco causas de fallo de un ítem; el primer ítem es válido y el segundo falla."""

    def preparar_items(self):
        self.producto = crear_producto(valor_neto=10_000)

    def item(self, **campos):
        item = {'producto_id': str(self.producto.pk), 'cantidad': '1', 'precio_unitario': 1_000}
        item.update(campos)
        return item

    def casos(self):
        valido = self.item()
        return [
            ('producto inexistente', json.dumps([valido, self.item(producto_id='999999')])),
            ('JSON inválido', '[{"producto_id":'),
            ('clave ausente', json.dumps([valido, {'cantidad': '1', 'precio_unitario': 1_000}])),
            ('cantidad no numérica', json.dumps([valido, self.item(cantidad='abc')])),
            ('precio no numérico', json.dumps([valido, self.item(precio_unitario='abc')])),
        ]


@override_settings(DEBUG=False)
class EditarPedidoItemFallidoTests(CasosDeItemFallido, FronteraBase):
    def setUp(self):
        super().setUp()
        self.client.raise_request_exception = False
        self.preparar_items()
        self.viejo = crear_producto(valor_neto=4_000)
        self.pedido = crear_pedido(valor_venta=10_000, items=[
            {'producto': self.viejo, 'cantidad': '2', 'precio_unitario': 5_000}])
        self.ruta = f'/pedido/editar/{self.pedido.pk}/'

    def datos(self, items_json):
        return {'cliente': self.pedido.cliente.pk, 'resumen_pedido': 'Editado', 'valor_venta': 15_000,
                'items_json': items_json}

    def items_actuales(self):
        return list(self.pedido.items.values_list('producto_id', 'cantidad', 'precio_unitario'))

    def test_item_fallido_conserva_el_pedido_y_responde_500(self):
        resumen = self.pedido.resumen_pedido
        for descripcion, items_json in self.casos():
            with self.subTest(descripcion):
                with self.assertLogs('django.request', 'ERROR'):
                    respuesta = self.ejecutar('post', self.ruta, self.datos(items_json))

                self.assertEqual(respuesta.status_code, 500)
                self.assertTemplateUsed(respuesta, 'pedidos/errors/500.html')
                self.pedido.refresh_from_db()
                self.assertEqual((self.pedido.resumen_pedido, self.pedido.valor_venta), (resumen, 10_000))
                self.assertEqual(self.items_actuales(), [(self.viejo.pk, Decimal('2.00'), 5_000)])
                self.assertEqual(self.eventos(), 0)

    def test_un_fallo_al_final_revierte_los_items_nuevos(self):
        items_json = ayudas.items_json((self.producto, '3', 4_000))

        with self.falla_al_final(), self.assertLogs('django.request', 'ERROR'):
            respuesta = self.ejecutar('post', self.ruta, self.datos(items_json))

        self.assertEqual(respuesta.status_code, 500)
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.valor_venta, 10_000)
        self.assertEqual(self.items_actuales(), [(self.viejo.pk, Decimal('2.00'), 5_000)])

    def test_deja_una_sola_linea_con_traza(self):
        items_json = json.dumps([self.item(), self.item(producto_id='999999')])

        with self.assertLogs(level='ERROR') as capturado:
            self.ejecutar('post', self.ruta, self.datos(items_json))

        self.assertEqual([r.name for r in capturado.records], ['django.request'])
        linea = formatear_como_error_log(capturado.records[0])
        self.assertIn(f'metodo=POST ruta={self.ruta} usuario=', linea)
        self.assertIn('Traceback (most recent call last):', linea)
        self.assertNotIn('Editado', linea)  # nunca el contenido del formulario

    def test_la_vista_no_captura_y_abre_su_transaccion(self):
        fuente = inspect.getsource(views.editar_pedido)
        self.assertNotIn('except Exception', fuente)
        self.assertIn('transaction.atomic()', fuente)


@override_settings(DEBUG=False)
class CrearCotizacionItemFallidoTests(CasosDeItemFallido, FronteraBase):
    def setUp(self):
        super().setUp()
        self.client.raise_request_exception = False
        self.preparar_items()
        self.cliente = crear_cliente()

    def datos(self, items_json):
        return {'cliente': self.cliente.pk, 'resumen': 'Nueva', 'detalles': '<p>Detalle</p>',
                'valor_total': 13_000, 'validez': 15, 'fecha_emision': '2026-10-15',
                'items_json': items_json}

    def test_item_fallido_no_deja_cotizacion_ni_items_y_responde_500(self):
        for descripcion, items_json in self.casos():
            with self.subTest(descripcion):
                with self.assertLogs('django.request', 'ERROR'):
                    respuesta = self.ejecutar('post', '/cotizaciones/nueva/', self.datos(items_json))

                self.assertEqual(respuesta.status_code, 500)
                self.assertTemplateUsed(respuesta, 'pedidos/errors/500.html')
                self.assertEqual((Cotizacion.objects.count(), ItemCotizacion.objects.count(),
                                  self.eventos()), (0, 0, 0))

    def test_deja_una_sola_linea_con_traza(self):
        items_json = json.dumps([self.item(), self.item(producto_id='999999')])

        with self.assertLogs(level='ERROR') as capturado:
            self.ejecutar('post', '/cotizaciones/nueva/', self.datos(items_json))

        self.assertEqual([r.name for r in capturado.records], ['django.request'])
        linea = formatear_como_error_log(capturado.records[0])
        self.assertIn('metodo=POST ruta=/cotizaciones/nueva/ usuario=', linea)
        self.assertIn('Traceback (most recent call last):', linea)

    def test_la_vista_no_captura_y_abre_su_transaccion(self):
        fuente = inspect.getsource(views.crear_cotizacion)
        self.assertNotIn('except Exception', fuente)
        self.assertIn('transaction.atomic()', fuente)


@override_settings(DEBUG=False)
class EditarCotizacionItemFallidoTests(CasosDeItemFallido, FronteraBase):
    def setUp(self):
        super().setUp()
        self.client.raise_request_exception = False
        self.preparar_items()
        self.viejo = crear_producto(valor_neto=4_000)
        self.cotizacion = crear_cotizacion(valor_total=10_000, items=[
            {'producto': self.viejo, 'cantidad': '2', 'precio_unitario': 5_000}])
        self.ruta = f'/cotizaciones/editar/{self.cotizacion.pk}/'

    def datos(self, items_json):
        return {'cliente': self.cotizacion.cliente.pk, 'resumen': 'Editada', 'detalles': '<p>Detalle</p>',
                'valor_total': 15_000, 'validez': 15, 'fecha_emision': '2026-10-15',
                'items_json': items_json}

    def test_item_fallido_conserva_la_cotizacion_y_responde_500(self):
        resumen = self.cotizacion.resumen
        for descripcion, items_json in self.casos():
            with self.subTest(descripcion):
                with self.assertLogs('django.request', 'ERROR'):
                    respuesta = self.ejecutar('post', self.ruta, self.datos(items_json))

                self.assertEqual(respuesta.status_code, 500)
                self.assertTemplateUsed(respuesta, 'pedidos/errors/500.html')
                self.cotizacion.refresh_from_db()
                self.assertEqual((self.cotizacion.resumen, self.cotizacion.valor_total), (resumen, 10_000))
                self.assertEqual(
                    list(self.cotizacion.items.values_list('producto_id', 'cantidad', 'precio_unitario')),
                    [(self.viejo.pk, Decimal('2.00'), 5_000)])

    def test_deja_una_sola_linea_con_traza(self):
        items_json = json.dumps([self.item(), self.item(producto_id='999999')])

        with self.assertLogs(level='ERROR') as capturado:
            self.ejecutar('post', self.ruta, self.datos(items_json))

        self.assertEqual([r.name for r in capturado.records], ['django.request'])

    def test_la_vista_no_captura_y_abre_su_transaccion(self):
        fuente = inspect.getsource(views.editar_cotizacion)
        self.assertNotIn('except Exception', fuente)
        self.assertIn('transaction.atomic()', fuente)


# ---------------------------------------------------------------------------
# Pagos: el pago y el estado financiero del pedido van juntos
# ---------------------------------------------------------------------------
@override_settings(DEBUG=False)
class PagosAtomicosTests(FronteraBase):
    def setUp(self):
        super().setUp()
        self.client.raise_request_exception = False
        self.pedido = crear_pedido(valor_venta=10_000)

    def test_ingresar_pago_con_fallo_no_deja_pago_ni_estado(self):
        with self.falla_al_final(), self.assertLogs('django.request', 'ERROR'):
            respuesta = self.ejecutar('post', '/pagos/ingresar/', {
                'pedido': self.pedido.pk, 'monto': 10_000, 'metodo': 'EFECTIVO', 'nota': ''})

        self.assertEqual(respuesta.status_code, 500)
        self.pedido.refresh_from_db()
        self.assertEqual((Pago.objects.count(), self.pedido.estado_pago), (0, 'PENDIENTE'))

    def test_editar_pago_con_fallo_deja_el_pago_y_los_estados_como_estaban(self):
        pago = crear_pago(self.pedido, monto=10_000)
        self.pedido.estado_pago = 'PAGADO'
        self.pedido.save()

        with self.falla_al_final(), self.assertLogs('django.request', 'ERROR'):
            respuesta = self.ejecutar('post', f'/pagos/editar/{pago.pk}/', {
                'pedido': self.pedido.pk, 'monto': 3_000, 'metodo': 'EFECTIVO', 'nota': ''})

        self.assertEqual(respuesta.status_code, 500)
        pago.refresh_from_db()
        self.pedido.refresh_from_db()
        self.assertEqual((pago.monto, self.pedido.estado_pago), (10_000, 'PAGADO'))

    def test_eliminar_pago_con_fallo_conserva_el_pago(self):
        pago = crear_pago(self.pedido, monto=4_000)

        with self.falla_al_final(), self.assertLogs('django.request', 'ERROR'):
            respuesta = self.ejecutar('post', f'/pagos/eliminar/{pago.pk}/')

        self.assertEqual(respuesta.status_code, 500)
        self.assertTrue(Pago.objects.filter(pk=pago.pk).exists())

    def test_las_vistas_de_pagos_abren_su_transaccion_y_no_capturan(self):
        for vista in (views.ingresar_pago, views.editar_pago, views.eliminar_pago):
            with self.subTest(vista=vista.__name__):
                fuente = inspect.getsource(vista)
                self.assertNotIn('except Exception', fuente)
                self.assertIn('transaction.atomic()', fuente)


class EstadoPagoCoherenteTests(FronteraBase):
    """`estado_pago` sigue a los pagos y al valor de venta (AUD-02-004), con la regla del oráculo."""

    def test_crear_con_abono_igual_al_total_deja_pagado(self):
        cliente = crear_cliente()

        self.ejecutar('post', '/pedidos/nuevo/', {
            'cliente': cliente.pk, 'resumen_pedido': 'Pagado', 'valor_venta': 10_000,
            'abono_inicial': 10_000})

        self.assertEqual(Pedido.objects.get().estado_pago, 'PAGADO')

    def test_crear_sin_abono_queda_pendiente(self):
        cliente = crear_cliente()

        self.ejecutar('post', '/pedidos/nuevo/', {
            'cliente': cliente.pk, 'resumen_pedido': 'Sin abono', 'valor_venta': 10_000})

        self.assertEqual(Pedido.objects.get().estado_pago, 'PENDIENTE')

    def test_bajar_el_valor_de_venta_hasta_lo_pagado_deja_pagado(self):
        pedido = crear_pedido(valor_venta=10_000, estado_pago='PARCIAL')
        crear_pago(pedido, monto=6_000)

        self.ejecutar('post', f'/pedido/editar/{pedido.pk}/', {
            'cliente': pedido.cliente.pk, 'resumen_pedido': pedido.resumen_pedido, 'valor_venta': 6_000})

        pedido.refresh_from_db()
        self.assertEqual((pedido.valor_venta, pedido.estado_pago), (6_000, 'PAGADO'))

    def test_eliminar_el_unico_pago_vuelve_a_pendiente(self):
        pedido = crear_pedido(valor_venta=10_000, estado_pago='PAGADO')
        pago = crear_pago(pedido, monto=10_000)

        self.ejecutar('post', f'/pagos/eliminar/{pago.pk}/')

        pedido.refresh_from_db()
        self.assertEqual((Pago.objects.count(), pedido.estado_pago), (0, 'PENDIENTE'))

    def test_editar_el_pago_sin_cambiar_de_pedido_recalcula_solo_ese_pedido(self):
        pedido = crear_pedido(valor_venta=10_000, estado_pago='PAGADO')
        otro = crear_pedido(valor_venta=10_000, estado_pago='PAGADO')  # sin pagos: no se toca
        pago = crear_pago(pedido, monto=10_000)

        self.ejecutar('post', f'/pagos/editar/{pago.pk}/', {
            'pedido': pedido.pk, 'monto': 3_000, 'metodo': 'EFECTIVO', 'nota': ''})

        pedido.refresh_from_db()
        otro.refresh_from_db()
        self.assertEqual((pedido.estado_pago, otro.estado_pago), ('PARCIAL', 'PAGADO'))

    def test_el_precio_del_item_no_se_recalcula(self):
        # Regla de negocio confirmada (2026-10-27): el precio de cada ítem lo fija el vendedor.
        cliente = crear_cliente()
        producto = crear_producto(valor_neto=10_000)
        pedido = crear_pedido(cliente=cliente, valor_venta=7_000)

        self.ejecutar('post', f'/pedido/editar/{pedido.pk}/', {
            'cliente': cliente.pk, 'resumen_pedido': 'Precio a mano', 'valor_venta': 7_000,
            'items_json': ayudas.items_json((producto, '1', 7_000))})

        self.assertEqual(list(pedido.items.values_list('precio_unitario', flat=True)), [7_000])


# ---------------------------------------------------------------------------
# Conversión de cotización a pedido (AUD-02-005)
# ---------------------------------------------------------------------------
class ConversionBase(FronteraBase):
    def setUp(self):
        super().setUp()
        self.cliente = crear_cliente()
        self.producto = crear_producto(valor_neto=10_000)
        self.cotizacion = crear_cotizacion(
            cliente=self.cliente, valor_total=50_000, estado='ENVIADA', items=[
                {'producto': self.producto, 'cantidad': '2', 'precio_unitario': 10_000}])
        self.ruta = f'/cotizaciones/convertir/{self.cotizacion.pk}/'
        self.detalle = f'/cotizaciones/detalle/{self.cotizacion.pk}/'

    def datos(self, **campos):
        datos = {'fecha_entrega': '2026-10-30', 'valor_abonado': '0'}
        datos.update(campos)
        return datos

    def nada_creado(self):
        self.cotizacion.refresh_from_db()
        self.assertEqual((Pedido.objects.count(), ItemPedido.objects.count(), Pago.objects.count(),
                          self.eventos(), self.cotizacion.estado), (0, 0, 0, 0, 'ENVIADA'))


class ConversionRepetidaTests(ConversionBase):
    """Decisión 4 del 2026-11-04: una cotización ya aceptada vuelve a su detalle, sin mensaje."""

    def aceptar(self):
        self.cotizacion.estado = 'ACEPTADA'
        self.cotizacion.save()

    def test_get_de_una_cotizacion_aceptada_redirige_al_detalle(self):
        self.aceptar()

        respuesta = self.client.get(self.ruta)

        self.assertRedirects(respuesta, self.detalle, fetch_redirect_response=False)

    def test_post_de_una_cotizacion_aceptada_no_crea_nada_y_redirige_al_detalle(self):
        self.aceptar()

        respuesta = self.ejecutar('post', self.ruta, self.datos(valor_abonado='5000'))

        self.assertRedirects(respuesta, self.detalle, fetch_redirect_response=False)
        self.assertEqual((Pedido.objects.count(), Pago.objects.count(), self.eventos()), (0, 0, 0))

    def test_convertir_dos_veces_deja_un_pedido_y_un_solo_pago(self):
        primera = self.ejecutar('post', self.ruta, self.datos(valor_abonado='5000'))
        segunda = self.ejecutar('post', self.ruta, self.datos(valor_abonado='5000'))

        self.assertEqual(primera.status_code, 302)
        self.assertRedirects(segunda, self.detalle, fetch_redirect_response=False)
        self.assertEqual((Pedido.objects.count(), Pago.objects.count()), (1, 1))

    def test_no_se_agrega_ningun_mensaje_al_rechazar(self):
        self.aceptar()

        respuesta = self.ejecutar('post', self.ruta, self.datos())

        self.assertEqual(list(respuesta.wsgi_request._messages), [])


class ConversionFormularioTests(ConversionBase):
    def test_datos_invalidos_devuelven_la_pagina_con_el_error_y_no_crean_nada(self):
        casos = [
            ('fecha vacía', self.datos(fecha_entrega=''), 'fecha_entrega'),
            ('fecha ilegible', self.datos(fecha_entrega='no-es-fecha'), 'fecha_entrega'),
            ('abono no numérico', self.datos(valor_abonado='veinte'), 'valor_abonado'),
            ('abono decimal', self.datos(valor_abonado='10.5'), 'valor_abonado'),
            ('abono negativo', self.datos(valor_abonado='-5000'), 'valor_abonado'),
            ('abono mayor que el total', self.datos(valor_abonado='50001'), 'valor_abonado'),
        ]
        for descripcion, datos, campo in casos:
            with self.subTest(descripcion):
                respuesta = self.ejecutar('post', self.ruta, datos)

                self.assertEqual(respuesta.status_code, 200)
                self.assertTemplateUsed(respuesta, 'pedidos/cotizacion_convertir.html')
                self.assertIn(campo, respuesta.context['form'].errors)
                self.nada_creado()

    def test_la_pagina_conserva_lo_que_escribio_el_usuario(self):
        respuesta = self.ejecutar('post', self.ruta, self.datos(
            fecha_entrega='2026-11-15', valor_abonado='60000', metodo_pago='EFECTIVO'))

        contenido = respuesta.content.decode()
        self.assertIn('value="2026-11-15"', contenido)
        self.assertIn('value="60000"', contenido)
        self.assertIn('El abono no puede ser mayor al valor total de la cotización.', contenido)

    def test_abono_igual_al_total_se_acepta_y_deja_pagado(self):
        self.ejecutar('post', self.ruta, self.datos(valor_abonado='50000', metodo_pago='EFECTIVO'))

        pedido = Pedido.objects.get()
        self.assertEqual((pedido.estado_pago, Pago.objects.get().monto), ('PAGADO', 50_000))

    def test_abono_vacio_equivale_a_cero(self):
        self.ejecutar('post', self.ruta, self.datos(valor_abonado=''))

        self.assertEqual((Pedido.objects.get().estado_pago, Pago.objects.count()), ('PENDIENTE', 0))

    def test_con_total_cero_cualquier_abono_se_acepta(self):
        # PENDIENTE_CLIENTE (pedido de valor $0): la misma regla de `PedidoForm`, hoy provisoria.
        self.cotizacion.valor_total = 0
        self.cotizacion.save()

        self.ejecutar('post', self.ruta, self.datos(valor_abonado='1000'))

        self.assertEqual(Pago.objects.get().monto, 1_000)

    def test_el_valor_de_venta_sigue_siendo_el_valor_total_sin_iva(self):
        # PENDIENTE_CLIENTE (AUD-02-014): no se toca mientras el cliente no responda.
        self.ejecutar('post', self.ruta, self.datos())

        self.assertEqual(Pedido.objects.get().valor_venta, 50_000)

    def test_el_abono_ya_no_se_convierte_en_cero_en_silencio(self):
        self.assertNotIn('except ValueError', inspect.getsource(views.convertir_a_pedido))


@override_settings(DEBUG=False)
class ConversionAtomicaTests(ConversionBase):
    def setUp(self):
        super().setUp()
        self.client.raise_request_exception = False

    def test_un_fallo_al_copiar_los_items_no_deja_nada_a_medias(self):
        with mock.patch.object(ItemPedido.objects, 'create', side_effect=RuntimeError('falla de prueba')), \
                self.assertLogs('django.request', 'ERROR'):
            respuesta = self.ejecutar('post', self.ruta, self.datos(valor_abonado='5000'))

        self.assertEqual(respuesta.status_code, 500)
        self.assertTemplateUsed(respuesta, 'pedidos/errors/500.html')
        self.nada_creado()

    def test_un_fallo_al_final_deja_la_cotizacion_sin_aceptar(self):
        with self.falla_al_final(), self.assertLogs('django.request', 'ERROR'):
            respuesta = self.ejecutar('post', self.ruta, self.datos(valor_abonado='5000'))

        self.assertEqual(respuesta.status_code, 500)
        self.nada_creado()

    def test_la_vista_abre_su_transaccion_y_bloquea_la_cotizacion(self):
        fuente = inspect.getsource(views.convertir_a_pedido)
        self.assertNotIn('except Exception', fuente)
        self.assertIn('transaction.atomic()', fuente)
        self.assertIn('select_for_update()', fuente)
