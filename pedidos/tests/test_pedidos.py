"""Flujos críticos de pedidos y pagos: pruebas de caracterización (iteración 02-03).

Congelan lo que hacen HOY las vistas, de la URL a la base. Los caminos de fallo y los
defectos conocidos (pérdida de ítems, `estado_pago`, escritura por GET, eliminar pago) son
regresiones de la 02-04 y no se prueban aquí. Las reglas sin confirmar llevan PENDIENTE_CLIENTE.

TestCase no confirma la transacción: los eventos (`on_commit`) se ejecutan con
`captureOnCommitCallbacks(execute=True)`.
"""
import tempfile
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone

from pedidos.models import ItemPedido, Pago, Pedido, RegistroEvento

from . import ayudas
from .factorias import (
    crear_cliente, crear_item_pedido, crear_pago, crear_pedido, crear_producto, crear_usuario,
    momento_chile,
)


class FlujoBase(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)

    def ejecutar(self, metodo, ruta, datos=None, **extra):
        with self.captureOnCommitCallbacks(execute=True):
            return getattr(self.client, metodo)(ruta, datos or {}, **extra)

    def tipos_de_evento(self):
        return list(RegistroEvento.objects.values_list('tipo', flat=True))


# ---------------------------------------------------------------------------
# Tarea 1 · Ayudas
# ---------------------------------------------------------------------------
class AyudasTests(FlujoBase):
    def test_items_json_arma_el_formato_del_navegador(self):
        producto = crear_producto()

        datos = ayudas.items_json((producto, '2.5', 4_000))

        self.assertEqual(datos, f'[{{"producto_id": "{producto.pk}", "cantidad": "2.5", '
                                f'"precio_unitario": 4000}}]')

    def test_cambiar_estado_usa_la_ruta_actual(self):
        pedido = crear_pedido()

        respuesta = ayudas.cambiar_estado(self.client, pedido, 'EN_PROCESO')

        self.assertRedirects(respuesta, f'/{pedido.pk}/', fetch_redirect_response=False)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'EN_PROCESO')

    def test_duplicar_usa_la_ruta_actual(self):
        pedido = crear_pedido()

        ayudas.duplicar(self.client, pedido)

        self.assertEqual(Pedido.objects.count(), 2)

    def test_congelar_hora_fija_timezone_now(self):
        with ayudas.congelar_hora():
            self.assertEqual(timezone.now(), ayudas.MEDIODIA)
        self.assertNotEqual(timezone.now(), ayudas.MEDIODIA)


# ---------------------------------------------------------------------------
# Tarea 2 · Crear pedido
# ---------------------------------------------------------------------------
class CrearPedidoTests(FlujoBase):
    def setUp(self):
        super().setUp()
        self.cliente = crear_cliente()
        self.tarjetas = crear_producto(valor_neto=10_000)
        self.lona = crear_producto(valor_neto=8_000, unidad='METRO_CUADRADO')

    def datos(self, **campos):
        datos = {
            'cliente': self.cliente.pk, 'resumen_pedido': 'Tarjetas y lona',
            'valor_venta': 31_800,
            'items_json': ayudas.items_json((self.tarjetas, '2', 11_900), (self.lona, '2.5', 3_200)),
        }
        datos.update(campos)
        return datos

    def test_formulario_responde(self):
        self.assertEqual(self.client.get('/pedidos/nuevo/').status_code, 200)

    def test_post_valido_crea_pedido_con_items(self):
        respuesta = self.ejecutar('post', '/pedidos/nuevo/', self.datos())

        pedido = Pedido.objects.get()
        self.assertRedirects(respuesta, f'/{pedido.pk}/', fetch_redirect_response=False)
        self.assertEqual((pedido.creado_por, pedido.estado, pedido.valor_venta),
                         (self.usuario, 'PENDIENTE', 31_800))
        items = {i.producto_id: i for i in pedido.items.all()}
        self.assertEqual(items[self.tarjetas.pk].cantidad, Decimal('2.00'))
        self.assertEqual(items[self.lona.pk].cantidad, Decimal('2.50'))
        self.assertEqual(items[self.lona.pk].precio_unitario, 3_200)
        self.assertEqual(self.tipos_de_evento(), ['pedido_creado'])

    def test_precio_del_item_queda_congelado(self):
        self.ejecutar('post', '/pedidos/nuevo/', self.datos())

        self.tarjetas.valor_neto = 20_000
        self.tarjetas.save()

        item = ItemPedido.objects.get(producto=self.tarjetas)
        self.assertEqual(item.precio_unitario, 11_900)

    def test_el_precio_lo_envia_el_navegador(self):
        # El servidor guarda el precio que llega en items_json, sin compararlo con el
        # catálogo. Regla de negocio confirmada el 2026-10-27: el vendedor ajusta a mano el
        # precio de cada ítem (bitacora-02-03-cierre.md). No validar contra el catálogo sin
        # consultar al desarrollador.
        self.ejecutar('post', '/pedidos/nuevo/', self.datos(
            items_json=ayudas.items_json((self.tarjetas, '1', 1))))

        self.assertEqual(ItemPedido.objects.get().precio_unitario, 1)

    def test_abono_inicial_crea_un_pago(self):
        casos = [
            ('método enviado', {'metodo_pago': 'TRANSFERENCIA'}, 'TRANSFERENCIA'),
            ('método por defecto', {}, 'EFECTIVO'),
        ]
        for descripcion, extra, metodo in casos:
            with self.subTest(descripcion):
                self.ejecutar('post', '/pedidos/nuevo/', self.datos(abono_inicial=10_000, **extra))

                pago = Pago.objects.latest('id')
                self.assertEqual((pago.monto, pago.metodo, pago.registrado_por, pago.nota),
                                 (10_000, metodo, self.usuario, 'Abono inicial al crear pedido'))

    def test_sin_abono_no_hay_pagos(self):
        for abono in ('', 0):
            with self.subTest(abono=abono):
                self.ejecutar('post', '/pedidos/nuevo/', self.datos(abono_inicial=abono))
        self.assertEqual(Pedido.objects.count(), 2)
        self.assertFalse(Pago.objects.exists())

    def test_sin_items_json_crea_el_pedido_sin_items(self):
        datos = self.datos()
        del datos['items_json']

        self.ejecutar('post', '/pedidos/nuevo/', datos)

        self.assertFalse(Pedido.objects.get().items.exists())

    def test_formulario_invalido_no_crea_nada(self):
        with self.assertLogs('pedidos.views', level='INFO'):
            respuesta = self.ejecutar('post', '/pedidos/nuevo/', self.datos(resumen_pedido=''))

        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(Pedido.objects.exists())


# ---------------------------------------------------------------------------
# Tarea 3 · Editar pedido
# ---------------------------------------------------------------------------
class EditarPedidoTests(FlujoBase):
    def setUp(self):
        super().setUp()
        self.viejo = crear_producto()
        self.nuevo = crear_producto()
        self.pedido = crear_pedido(valor_venta=10_000, items=[
            {'producto': self.viejo, 'cantidad': '1', 'precio_unitario': 10_000}])

    def datos(self, **campos):
        datos = {'cliente': self.pedido.cliente.pk, 'resumen_pedido': 'Resumen editado',
                 'valor_venta': 15_000}
        datos.update(campos)
        return datos

    def test_formulario_responde_con_los_items_precargados(self):
        respuesta = self.client.get(f'/pedido/editar/{self.pedido.pk}/')

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(f'"producto_id": {self.viejo.pk}', respuesta.context['items_json'])

    def test_cambia_campos_y_valor_venta(self):
        respuesta = self.ejecutar('post', f'/pedido/editar/{self.pedido.pk}/', self.datos())

        self.assertRedirects(respuesta, f'/{self.pedido.pk}/', fetch_redirect_response=False)
        self.pedido.refresh_from_db()
        self.assertEqual((self.pedido.resumen_pedido, self.pedido.valor_venta),
                         ('Resumen editado', 15_000))
        self.assertEqual(self.tipos_de_evento(), ['pedido_modificado'])

    def test_reemplaza_los_items(self):
        self.ejecutar('post', f'/pedido/editar/{self.pedido.pk}/', self.datos(
            items_json=ayudas.items_json((self.nuevo, '3', 5_000))))

        items = list(self.pedido.items.values_list('producto_id', 'cantidad', 'precio_unitario'))
        self.assertEqual(items, [(self.nuevo.pk, Decimal('3.00'), 5_000)])

    def test_sin_items_json_conserva_los_items(self):
        self.ejecutar('post', f'/pedido/editar/{self.pedido.pk}/', self.datos())

        self.assertEqual(list(self.pedido.items.values_list('producto_id', flat=True)), [self.viejo.pk])


# ---------------------------------------------------------------------------
# Tarea 6 · Cambiar estado (decisión D3: se fija lo que permite hoy la vista)
# ---------------------------------------------------------------------------
class CambiarEstadoTests(FlujoBase):
    ESTADOS = ['PENDIENTE', 'EN_PROCESO', 'TERMINADO', 'ENTREGADO']

    def test_cualquier_transicion_se_acepta(self):
        # Hoy no hay reglas de transición: se acepta avanzar, retroceder y saltar estados.
        # Depende del GET actual (ayudas.cambiar_estado; 04-01).
        for origen in self.ESTADOS:
            for destino in self.ESTADOS:
                with self.subTest(origen=origen, destino=destino):
                    pedido = crear_pedido(estado=origen)
                    respuesta = ayudas.cambiar_estado(self.client, pedido, destino)
                    self.assertRedirects(respuesta, f'/{pedido.pk}/', fetch_redirect_response=False)
                    pedido.refresh_from_db()
                    self.assertEqual(pedido.estado, destino)

    def test_estado_inexistente_redirige_sin_cambiar_nada(self):
        # Depende del GET actual (ayudas.cambiar_estado; 04-01).
        pedido = crear_pedido(estado='EN_PROCESO')
        for estado in ('INVENTADO', 'pendiente'):
            with self.subTest(estado=estado):
                with self.captureOnCommitCallbacks(execute=True):
                    respuesta = ayudas.cambiar_estado(self.client, pedido, estado)
                self.assertRedirects(respuesta, f'/{pedido.pk}/', fetch_redirect_response=False)
                pedido.refresh_from_db()
                self.assertEqual(pedido.estado, 'EN_PROCESO')
        self.assertEqual(self.tipos_de_evento(), [])

    def test_pedido_inexistente_responde_404(self):
        self.assertEqual(self.client.get('/pedido/999999/cambiar/TERMINADO/').status_code, 404)

    def test_no_toca_el_estado_de_pago(self):
        pedido = crear_pedido(valor_venta=10_000, estado_pago='PARCIAL')
        ayudas.cambiar_estado(self.client, pedido, 'ENTREGADO')
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado_pago, 'PARCIAL')


# ---------------------------------------------------------------------------
# Tarea 7 · Duplicar pedido
# ---------------------------------------------------------------------------
class DuplicarPedidoTests(FlujoBase):
    def setUp(self):
        super().setUp()
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        parche = override_settings(MEDIA_ROOT=carpeta.name)  # nunca el media/ real (AUD-02-023)
        parche.enable()
        self.addCleanup(parche.disable)
        imagen = SimpleUploadedFile('referencia.png', b'\x89PNG prueba', content_type='image/png')
        self.original = crear_pedido(
            valor_venta=25_000, estado='ENTREGADO', estado_pago='PAGADO', detalles_pedido='Detalle',
            fecha_entrega=momento_chile(2026, 10, 20).date(), creado_por=crear_usuario(),
            fecha_solicitud=momento_chile(2026, 1, 5), imagen_referencia=imagen,
            items=[{'cantidad': '2', 'precio_unitario': 5_000}])
        crear_pago(self.original, monto=25_000)

    def duplicar(self):
        # Depende del GET actual (ayudas.duplicar; 04-01).
        antes = timezone.now()
        with self.captureOnCommitCallbacks(execute=True):
            respuesta = ayudas.duplicar(self.client, self.original)
        despues = timezone.now()
        return respuesta, Pedido.objects.exclude(pk=self.original.pk).get(), antes, despues

    def test_copia_cabecera_y_redirige_al_nuevo(self):
        respuesta, nuevo, _, _ = self.duplicar()

        self.assertRedirects(respuesta, f'/{nuevo.pk}/', fetch_redirect_response=False)
        self.assertNotEqual(nuevo.pk, self.original.pk)
        copiados = ('cliente_id', 'resumen_pedido', 'detalles_pedido', 'valor_venta', 'fecha_entrega')
        for campo in copiados:
            with self.subTest(campo):
                self.assertEqual(getattr(nuevo, campo), getattr(self.original, campo))
        # Comparte el mismo archivo: no se copia la imagen, solo su ruta.
        self.assertEqual(nuevo.imagen_referencia.name, self.original.imagen_referencia.name)
        self.assertEqual(self.tipos_de_evento(), ['pedido_duplicado'])

    def test_lo_que_no_se_copia(self):
        _, nuevo, antes, despues = self.duplicar()

        self.assertEqual(nuevo.estado, 'PENDIENTE')
        self.assertEqual(nuevo.estado_pago, 'PENDIENTE')  # valor por defecto del modelo
        self.assertIsNone(nuevo.creado_por)  # ni el original ni el usuario que duplica
        self.assertFalse(nuevo.pagos.exists())
        # PENDIENTE_CLIENTE: ¿al duplicar se deben copiar los ítems? Hoy no se copian.
        self.assertFalse(nuevo.items.exists())
        self.assertEqual(self.original.items.count(), 1)

    def test_fecha_de_solicitud_es_la_actual(self):
        # La fecha la pone `default=timezone.now` del modelo, que el parche de la hora no
        # alcanza: se acota entre dos lecturas del reloj alrededor de la petición.
        _, nuevo, antes, despues = self.duplicar()

        self.assertTrue(antes <= nuevo.fecha_solicitud <= despues)


# ---------------------------------------------------------------------------
# Tarea 8 · Clasificación del panel y del trabajo semanal (AUD-02-013)
# ---------------------------------------------------------------------------
class ClasificacionTests(FlujoBase):
    ESTADOS = ['PENDIENTE', 'EN_PROCESO', 'TERMINADO', 'ENTREGADO']
    FECHAS = {
        'atrasada': momento_chile(2026, 10, 10).date(),
        'esta semana': momento_chile(2026, 10, 18).date(),
        'futura': momento_chile(2026, 11, 5).date(),
        'sin fecha': None,
    }

    def setUp(self):
        super().setUp()
        self.pedidos = {}
        for estado in self.ESTADOS:
            for nombre, fecha in self.FECHAS.items():
                self.pedidos[estado, nombre] = crear_pedido(
                    estado=estado, fecha_entrega=fecha, fecha_solicitud=momento_chile(2026, 10, 1))

    def esperado(self, fecha):
        # Criterio actual: activos = todo lo que no es TERMINADO.
        # PENDIENTE_CLIENTE (AUD-02-013): ¿un ENTREGADO atrasado es crítico? Hoy sí.
        return {self.pedidos[e, fecha].pk for e in ('PENDIENTE', 'EN_PROCESO', 'ENTREGADO')}

    def test_trabajo_semanal(self):
        with ayudas.congelar_hora():
            contexto = self.client.get('/pedidos/trabajo-semanal/').context

        for categoria, fecha in (('criticos', 'atrasada'), ('urgentes', 'esta semana'),
                                 ('normales', 'futura')):
            with self.subTest(categoria):
                self.assertEqual({p.pk for p in contexto[categoria]}, self.esperado(fecha))
        # PENDIENTE_CLIENTE (AUD-02-013): los pedidos sin fecha no caen en ninguna categoría,
        # pero cuentan en el total de activos: 6 de 12 activos en presión → 50 %.
        clasificados = {p.pk for c in ('criticos', 'urgentes', 'normales') for p in contexto[c]}
        self.assertTrue(self.esperado('sin fecha').isdisjoint(clasificados))
        self.assertEqual(contexto['nivel_presion'], 50)
        self.assertEqual(contexto['hoy'], ayudas.MEDIODIA.date())

    def test_panel(self):
        with ayudas.congelar_hora():
            contexto = self.client.get('/').context

        self.assertEqual(contexto['criticos_count'], 3)
        self.assertEqual(contexto['urgentes_count'], 3)


# ---------------------------------------------------------------------------
# Lectura (decisión D2): solo el detalle del pedido
# ---------------------------------------------------------------------------
class DetallePedidoTests(FlujoBase):
    def test_detalle_responde_con_el_pedido(self):
        pedido = crear_pedido(valor_venta=10_000, items=[{}])
        crear_pago(pedido, monto=4_000)

        respuesta = self.client.get(f'/{pedido.pk}/')

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['pedido'], pedido)
        self.assertEqual(self.tipos_de_evento(), [])

    def test_detalle_inexistente_responde_404(self):
        self.assertEqual(self.client.get('/999999/').status_code, 404)


# ---------------------------------------------------------------------------
# Pagos (decisión D1): solo el camino feliz de ingresar y editar
# ---------------------------------------------------------------------------
class PagosTests(FlujoBase):
    def setUp(self):
        super().setUp()
        self.pedido = crear_pedido(valor_venta=10_000)

    def test_ingresar_desde_el_pedido_sugiere_el_saldo(self):
        crear_pago(self.pedido, monto=4_000)

        respuesta = self.client.get(f'/pagos/ingresar/{self.pedido.pk}/')

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['form'].initial['monto'], 6_000)

    def test_ingresar_pago(self):
        # (monto, estado_pago resultante)
        for monto, estado in ((4_000, 'PARCIAL'), (6_000, 'PAGADO')):
            with self.subTest(monto=monto):
                respuesta = self.ejecutar('post', '/pagos/ingresar/', {
                    'pedido': self.pedido.pk, 'monto': monto, 'metodo': 'DEBITO', 'nota': 'Nota'})

                self.assertRedirects(respuesta, '/pagos/lista/', fetch_redirect_response=False)
                pago = Pago.objects.latest('id')
                self.assertEqual((pago.monto, pago.metodo, pago.registrado_por),
                                 (monto, 'DEBITO', self.usuario))
                self.pedido.refresh_from_db()
                self.assertEqual(self.pedido.estado_pago, estado)
        self.assertEqual(self.tipos_de_evento(), ['pago_registrado', 'pago_registrado'])

    def test_editar_pago_recalcula_el_estado(self):
        pago = crear_pago(self.pedido, monto=10_000)
        self.pedido.estado_pago = 'PAGADO'
        self.pedido.save()

        respuesta = self.ejecutar('post', f'/pagos/editar/{pago.pk}/', {
            'pedido': self.pedido.pk, 'monto': 3_000, 'metodo': 'EFECTIVO', 'nota': ''})

        self.assertRedirects(respuesta, f'/{self.pedido.pk}/', fetch_redirect_response=False)
        pago.refresh_from_db()
        self.pedido.refresh_from_db()
        self.assertEqual((pago.monto, self.pedido.estado_pago), (3_000, 'PARCIAL'))
        self.assertEqual(self.tipos_de_evento(), ['pago_modificado'])

    def test_editar_pago_formulario_responde(self):
        pago = crear_pago(self.pedido, monto=1_000)
        self.assertEqual(self.client.get(f'/pagos/editar/{pago.pk}/').status_code, 200)
