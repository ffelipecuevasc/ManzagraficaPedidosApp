"""Regresiones de defectos conocidos (iteración 02-04).

Cada prueba afirma el comportamiento CORRECTO y hoy falla a propósito por el defecto que
describe su comentario (`AUD-…`, qué falla hoy y qué iteración lo corrige). Lleva
`@tag('regresion')` y `@expectedFailure`: el día que la corrección llegue, el resumen
informa `unexpected successes` y la iteración que corrige quita las dos marcas.

Numeración (decisión D3 del desarrollador, 2026-10-27): R1 a R15, R18 y R19. R16 está
reservado para AUD-02-021 y R17 está libre. R6 son tres pruebas. R5 no se escribió: el
defecto no se reprodujo como estaba descrito (ver su sección).

Contrato de R1 a R4 (decisión D1): «todo o nada». Si falla un ítem, no queda rastro en la
base: ni pedido o cotización a medias, ni ítems anteriores borrados.

Los errores que se provocan a propósito se absorben con `absorber_errores` (envuelve
`assertLogs`). No exige que haya registros, para que la prueba pase cuando la corrección
deje de registrar el error.

TestCase no confirma la transacción: los eventos (`on_commit`) se ejecutan con
`captureOnCommitCallbacks(execute=True)`.
"""
import os
import tempfile
from contextlib import contextmanager
from datetime import date, timezone as tz
from decimal import Decimal
from unittest import expectedFailure, mock

from django.db.models import ProtectedError
from django.test import TestCase, tag

from pedidos import views
from pedidos.models import Cotizacion, HistorialBD, ItemCotizacion, ItemPedido, Pedido
from pedidos.utils import registrar_metricas_diarias

from . import ayudas
from .factorias import (
    crear_cliente, crear_cotizacion, crear_pago, crear_pedido, crear_producto,
    crear_superusuario, crear_usuario, momento_chile,
)

# Un producto que no existe: hace fallar el segundo ítem de `items_json`.
PRODUCTO_INEXISTENTE = 999_999

# Borde de día y de mes (AUD-02-003): a las 22:00 de Chile en octubre (UTC−3) ya es la
# 01:00 del día siguiente en UTC. El parche devuelve el instante en UTC, igual que el
# `timezone.now()` real con USE_TZ: con la zona de Chile, `.date()` escondería el defecto.
NOCHE_15 = momento_chile(2026, 10, 15, hora=22).astimezone(tz.utc)
NOCHE_31 = momento_chile(2026, 10, 31, hora=22).astimezone(tz.utc)


class _ProductoFalso:
    pk = PRODUCTO_INEXISTENTE


@contextmanager
def absorber_errores(prueba, *registradores):
    """`assertLogs` de cada registrador, sin exigir que haya registros.

    Absorbe el ruido de los errores provocados a propósito. Si la corrección deja de
    registrar el error, la prueba no debe fallar por eso.
    """
    contextos = [prueba.assertLogs(nombre, 'ERROR') for nombre in registradores or ('pedidos',)]
    for contexto in contextos:
        contexto.__enter__()
    try:
        yield
    finally:
        for contexto in reversed(contextos):
            try:
                contexto.__exit__(None, None, None)
            except AssertionError:
                pass  # Sin registros: la corrección ya no registra este error.


class RegresionBase(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)

    def ejecutar(self, metodo, ruta, datos=None):
        with self.captureOnCommitCallbacks(execute=True):
            return getattr(self.client, metodo)(ruta, datos or {})


# ---------------------------------------------------------------------------
# Tarea 2 · Oráculo de estado_pago (prueba normal, en verde)
# ---------------------------------------------------------------------------
class OraculoEstadoPagoTests(TestCase):
    def test_reglas_del_oraculo(self):
        # (valor_venta, pagos, estado esperado)
        casos = [
            (10_000, [], 'PENDIENTE'),
            (10_000, [4_000], 'PARCIAL'),
            (10_000, [4_000, 6_000], 'PAGADO'),
            (10_000, [12_000], 'PAGADO'),
            (0, [], 'PAGADO'),  # La regla de linea_base.sql: saldo 0 cuenta como pagado.
        ]
        for valor, pagos, esperado in casos:
            with self.subTest(valor=valor, pagos=pagos):
                pedido = crear_pedido(valor_venta=valor)
                for monto in pagos:
                    crear_pago(pedido, monto=monto)

                self.assertEqual(ayudas.estado_pago_esperado(pedido), esperado)


# ---------------------------------------------------------------------------
# R1 a R4 · Ítems: todo o nada (AUD-01-002, AUD-02-008)
# ---------------------------------------------------------------------------
class ItemsTodoONadaTests(RegresionBase):
    def setUp(self):
        super().setUp()
        self.cliente = crear_cliente()
        self.viejo = crear_producto(valor_neto=10_000)
        self.nuevo = crear_producto(valor_neto=4_000)
        # Un ítem válido seguido de uno que falla.
        self.items_con_fallo = ayudas.items_json((self.nuevo, '3', 4_000),
                                                 (_ProductoFalso, '1', 1_000))

    @tag('regresion')
    @expectedFailure  # R1 · AUD-01-002: hoy borra los ítems y recrea hasta el fallo. Lo corrige la 03-03.
    def test_r1_editar_pedido_con_item_fallido_no_deja_rastro(self):
        pedido = crear_pedido(cliente=self.cliente, valor_venta=10_000, items=[
            {'producto': self.viejo, 'cantidad': '1', 'precio_unitario': 10_000}])

        with absorber_errores(self):
            self.ejecutar('post', f'/pedido/editar/{pedido.pk}/', {
                'cliente': self.cliente.pk, 'resumen_pedido': 'Editado', 'valor_venta': 15_000,
                'items_json': self.items_con_fallo})

        pedido.refresh_from_db()
        self.assertEqual(list(pedido.items.values_list('producto_id', 'cantidad', 'precio_unitario')),
                         [(self.viejo.pk, Decimal('1.00'), 10_000)])
        self.assertEqual(pedido.valor_venta, 10_000)

    @tag('regresion')
    @expectedFailure  # R2 · AUD-01-002: igual que R1, en cotizaciones. Lo corrige la 03-03.
    def test_r2_editar_cotizacion_con_item_fallido_no_deja_rastro(self):
        cotizacion = crear_cotizacion(cliente=self.cliente, valor_total=10_000, items=[
            {'producto': self.viejo, 'cantidad': '1', 'precio_unitario': 10_000}])

        with absorber_errores(self):
            self.ejecutar('post', f'/cotizaciones/editar/{cotizacion.pk}/', {
                'cliente': self.cliente.pk, 'resumen': 'Editada', 'detalles': '<p>Detalle</p>',
                'valor_total': 15_000, 'validez': 15, 'fecha_emision': '2026-10-15',
                'items_json': self.items_con_fallo})

        cotizacion.refresh_from_db()
        self.assertEqual(
            list(cotizacion.items.values_list('producto_id', 'cantidad', 'precio_unitario')),
            [(self.viejo.pk, Decimal('1.00'), 10_000)])
        self.assertEqual(cotizacion.valor_total, 10_000)

    @tag('regresion')
    @expectedFailure  # R3 · AUD-02-008: el try/except interno anula el atomic; queda el pedido con ítems parciales. Lo corrige la 03-03.
    def test_r3_crear_pedido_con_item_fallido_no_deja_rastro(self):
        with absorber_errores(self):
            self.ejecutar('post', '/pedidos/nuevo/', {
                'cliente': self.cliente.pk, 'resumen_pedido': 'Nuevo', 'valor_venta': 13_000,
                'items_json': self.items_con_fallo})

        self.assertEqual((Pedido.objects.count(), ItemPedido.objects.count()), (0, 0))

    @tag('regresion')
    @expectedFailure  # R4 · AUD-01-002: queda la cotización con ítems parciales. Lo corrige la 03-03.
    def test_r4_crear_cotizacion_con_item_fallido_no_deja_rastro(self):
        with absorber_errores(self):
            self.ejecutar('post', '/cotizaciones/nueva/', {
                'cliente': self.cliente.pk, 'resumen': 'Nueva', 'detalles': '<p>Detalle</p>',
                'valor_total': 13_000, 'validez': 15, 'fecha_emision': '2026-10-15',
                'items_json': self.items_con_fallo})

        self.assertEqual((Cotizacion.objects.count(), ItemCotizacion.objects.count()), (0, 0))


# ---------------------------------------------------------------------------
# R5 · No se registra (AUD-01-006 no se reprodujo como estaba descrito)
# ---------------------------------------------------------------------------
# Dos llamadas a `registrar_metricas_diarias()` en el mismo instante, a mediodía de Chile,
# dejan UNA fila: la prueba dio «unexpected success» y no se marca como regresión
# (bitacora-02-04.md). A las 22:00 de Chile sí deja dos, pero ese es el día en UTC
# (AUD-02-003), que ya comprueba R8 en la base.


# ---------------------------------------------------------------------------
# R6 · Escritura por GET (AUD-02-006, plan 4.1)
# ---------------------------------------------------------------------------
class EscrituraPorGetTests(RegresionBase):
    # Estas pruebas usan GET a propósito, sin pasar por `ayudas`: afirman que GET se rechaza.

    @tag('regresion')
    @expectedFailure  # R6a · AUD-02-006: cambiar_estado escribe con GET y redirige (302). Lo corrige la 04-01.
    def test_r6_cambiar_estado_rechaza_get(self):
        pedido = crear_pedido(estado='PENDIENTE')

        respuesta = self.ejecutar('get', f'/pedido/{pedido.pk}/cambiar/EN_PROCESO/')

        pedido.refresh_from_db()
        self.assertEqual((respuesta.status_code, pedido.estado), (405, 'PENDIENTE'))

    @tag('regresion')
    @expectedFailure  # R6b · AUD-02-006: duplicar_pedido crea un pedido con GET y redirige (302). Lo corrige la 04-01.
    def test_r6_duplicar_pedido_rechaza_get(self):
        pedido = crear_pedido()

        respuesta = self.ejecutar('get', f'/pedido/duplicar/{pedido.pk}/')

        self.assertEqual((respuesta.status_code, Pedido.objects.count()), (405, 1))

    @tag('regresion')
    @expectedFailure  # R6c · AUD-02-006: generar_respaldo_bd genera el respaldo con GET (200). Lo corrige la 04-01.
    def test_r6_generar_respaldo_rechaza_get(self):
        self.client.force_login(crear_superusuario())
        # Nunca se ejecuta mysqldump: se reemplaza la función donde la busca la vista.
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        ruta = os.path.join(carpeta.name, 'respaldo_prueba.sql')
        with open(ruta, 'w', encoding='utf-8') as archivo:
            archivo.write('-- respaldo de prueba\n')

        with mock.patch.object(views, 'generar_respaldo_mysql', return_value=ruta) as generar:
            respuesta = self.ejecutar('get', '/base_datos/respaldar_bd/accion/')
        respuesta.close()  # Cierra el archivo que abre FileResponse.

        self.assertEqual((respuesta.status_code, generar.called), (405, False))


# ---------------------------------------------------------------------------
# R7 · Eliminar pago sin plantilla de confirmación (AUD-02-002)
# ---------------------------------------------------------------------------
class EliminarPagoTests(RegresionBase):
    @tag('regresion')
    @expectedFailure  # R7 · AUD-02-002: falta pedidos/pago_confirm_delete.html y responde 500. Lo corrige la 04-01.
    def test_r7_confirmacion_de_eliminar_pago_responde_200(self):
        pago = crear_pago(crear_pedido(valor_venta=10_000), monto=4_000)

        with absorber_errores(self, 'pedidos', 'django.request'):
            respuesta = self.client.get(f'/pagos/eliminar/{pago.pk}/')

        self.assertEqual(respuesta.status_code, 200)


# ---------------------------------------------------------------------------
# R8 y R9 · Día y mes en UTC (AUD-02-003)
# ---------------------------------------------------------------------------
class BordesDeHoraChileTests(RegresionBase):
    def setUp(self):
        super().setUp()
        # El panel lista los .sql de BASE_DIR/backups: carpeta temporal vacía.
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        parche = mock.patch.object(views.settings, 'BASE_DIR', carpeta.name)
        parche.start()
        self.addCleanup(parche.stop)

    @tag('regresion')
    @expectedFailure  # R8 · AUD-02-003: a las 22:00 de Chile el panel usa el día UTC (el 16). Lo corrige la 06-01.
    def test_r8_panel_y_chequeo_diario_usan_el_dia_de_chile(self):
        # Pedido que se entrega HOY en Chile (15 de octubre): no está atrasado.
        crear_pedido(estado='PENDIENTE', fecha_entrega=date(2026, 10, 15))
        # Métricas ya registradas HOY en Chile, a las 10:00.
        with ayudas.congelar_hora(momento_chile(2026, 10, 15, hora=10).astimezone(tz.utc)):
            registrar_metricas_diarias()

        with ayudas.congelar_hora(NOCHE_15):
            respuesta = self.client.get('/')

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual((respuesta.context['criticos_count'], respuesta.context['urgentes_count']),
                         (0, 1))
        # Base: el chequeo diario no vuelve a escribir el mismo día de Chile.
        self.assertEqual(HistorialBD.objects.count(), 1)

    @tag('regresion')
    @expectedFailure  # R9 · AUD-02-003: el 31 a las 22:00 de Chile, «ingresos del mes» usa noviembre (UTC). Lo corrige la 06-01.
    def test_r9_ingresos_del_mes_usan_el_mes_de_chile(self):
        crear_pago(crear_pedido(valor_venta=50_000), monto=10_000,
                   fecha=momento_chile(2026, 10, 15))

        with ayudas.congelar_hora(NOCHE_31):
            respuesta = self.client.get('/pagos/estadisticas/')

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['ingresos_mes_actual'], 10_000)


# ---------------------------------------------------------------------------
# R10 a R12 · estado_pago desincronizado (AUD-02-004)
# ---------------------------------------------------------------------------
class EstadoPagoTests(RegresionBase):
    def setUp(self):
        super().setUp()
        self.cliente = crear_cliente()

    @tag('regresion')
    @expectedFailure  # R10 · AUD-02-004: crear con abono deja estado_pago PENDIENTE. Lo corrige la 03-03.
    def test_r10_crear_con_abono_deja_estado_pago_coherente(self):
        self.ejecutar('post', '/pedidos/nuevo/', {
            'cliente': self.cliente.pk, 'resumen_pedido': 'Con abono', 'valor_venta': 10_000,
            'abono_inicial': 4_000})

        pedido = Pedido.objects.get()
        self.assertEqual(pedido.estado_pago, ayudas.estado_pago_esperado(pedido))  # PARCIAL

    @tag('regresion')
    @expectedFailure  # R11 · AUD-02-004: editar valor_venta no recalcula estado_pago. Lo corrige la 03-03.
    def test_r11_editar_valor_venta_recalcula_estado_pago(self):
        pedido = crear_pedido(cliente=self.cliente, valor_venta=10_000, estado_pago='PAGADO')
        crear_pago(pedido, monto=10_000)

        self.ejecutar('post', f'/pedido/editar/{pedido.pk}/', {
            'cliente': self.cliente.pk, 'resumen_pedido': pedido.resumen_pedido,
            'valor_venta': 20_000})

        pedido.refresh_from_db()
        self.assertEqual(pedido.valor_venta, 20_000)
        self.assertEqual(pedido.estado_pago, ayudas.estado_pago_esperado(pedido))  # PARCIAL

    @tag('regresion')
    @expectedFailure  # R12 · AUD-02-004: mover un pago de pedido no recalcula el pedido anterior. Lo corrige la 03-03.
    def test_r12_mover_pago_recalcula_ambos_pedidos(self):
        anterior = crear_pedido(cliente=self.cliente, valor_venta=10_000, estado_pago='PAGADO')
        destino = crear_pedido(cliente=self.cliente, valor_venta=10_000, estado_pago='PENDIENTE')
        pago = crear_pago(anterior, monto=10_000)

        self.ejecutar('post', f'/pagos/editar/{pago.pk}/', {
            'pedido': destino.pk, 'monto': 10_000, 'metodo': 'EFECTIVO', 'nota': ''})

        anterior.refresh_from_db()
        destino.refresh_from_db()
        self.assertEqual(destino.estado_pago, ayudas.estado_pago_esperado(destino))  # PAGADO
        self.assertEqual(anterior.estado_pago, ayudas.estado_pago_esperado(anterior))  # PENDIENTE


# ---------------------------------------------------------------------------
# R13 y R18 · Conversión de cotizaciones (AUD-02-005, AUD-02-027)
# ---------------------------------------------------------------------------
class ConvertirCotizacionTests(RegresionBase):
    def setUp(self):
        super().setUp()
        self.cotizacion = crear_cotizacion(valor_total=20_000, estado='ENVIADA', items=[
            {'cantidad': '2', 'precio_unitario': 10_000}])
        self.ruta = f'/cotizaciones/convertir/{self.cotizacion.pk}/'

    @tag('regresion')
    @expectedFailure  # R13 · AUD-02-005: la segunda conversión crea otro pedido. Lo corrige la 03-03.
    def test_r13_convertir_dos_veces_crea_un_solo_pedido(self):
        datos = {'fecha_entrega': '2026-10-30', 'valor_abonado': '0'}
        self.ejecutar('post', self.ruta, datos)

        self.ejecutar('post', self.ruta, datos)

        self.assertEqual(Pedido.objects.count(), 1)

    @tag('regresion')
    @expectedFailure  # R18 · AUD-02-027: con fecha_entrega vacía el guardado falla y responde 500. Lo corrige la 03-04.
    def test_r18_convertir_sin_fecha_de_entrega_no_responde_500(self):
        with absorber_errores(self, 'pedidos', 'django.request'):
            respuesta = self.ejecutar('post', self.ruta, {'fecha_entrega': '', 'valor_abonado': '0'})

        # Primero la respuesta: hoy el ValidationError deja la transacción de la prueba
        # marcada para revertir y cualquier consulta posterior daría otro error.
        self.assertEqual(respuesta.status_code, 200)  # Devuelve el formulario con su error.
        self.cotizacion.refresh_from_db()
        self.assertEqual((Pedido.objects.count(), self.cotizacion.estado), (0, 'ENVIADA'))


# ---------------------------------------------------------------------------
# R14 · Borrado en cascada del historial de un cliente (AUD-02-001)
# ---------------------------------------------------------------------------
class HistorialClienteTests(TestCase):
    @tag('regresion')
    @expectedFailure  # R14 · AUD-02-001: on_delete=CASCADE borra pedidos, ítems, pagos y cotizaciones. Lo corrige la 04-06.
    def test_r14_eliminar_cliente_con_pedidos_se_rechaza(self):
        cliente = crear_cliente()
        pedido = crear_pedido(cliente=cliente, valor_venta=10_000)
        crear_pago(pedido, monto=4_000)

        with self.assertRaises(ProtectedError):
            cliente.delete()

        self.assertTrue(Pedido.objects.filter(pk=pedido.pk).exists())


# ---------------------------------------------------------------------------
# R15 · Porcentaje pagado con float (AUD-02-025)
# ---------------------------------------------------------------------------
class PorcentajePagadoTests(TestCase):
    @tag('regresion')
    @expectedFailure  # R15 · AUD-02-025: int(29 / 100 * 100) da 28 por el float. Lo corrige la 07-02 (antes 06-05).
    def test_r15_porcentaje_pagado_con_enteros(self):
        pedido = crear_pedido(valor_venta=100)
        crear_pago(pedido, monto=29)

        self.assertEqual(pedido.porcentaje_pagado, 29)


# ---------------------------------------------------------------------------
# R19 · Pedido duplicado sin autor (AUD-02-028)
# ---------------------------------------------------------------------------
class DuplicarPedidoTests(RegresionBase):
    @tag('regresion')
    @expectedFailure  # R19 · AUD-02-028: el duplicado queda con creado_por nulo. Iteración: PENDIENTE_DESARROLLADOR.
    def test_r19_duplicado_queda_con_el_usuario_que_duplica(self):
        original = crear_pedido(creado_por=crear_usuario())

        # Escribe con GET hoy; pasa por la ayuda para que la 04-01 cambie una sola línea.
        ayudas.duplicar(self.client, original)

        duplicado = Pedido.objects.exclude(pk=original.pk).get()
        self.assertEqual(duplicado.creado_por, self.usuario)
