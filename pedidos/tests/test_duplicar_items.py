"""Reabrir Pedido copia los ítems y pide la fecha de entrega (iteración 14-02, AUD-05-012).

Decisiones del desarrollador (2026-11-19): D1 precio unitario del original; D2 sin trato
especial del producto; D3 se conserva `valor_venta`; D4 página intermedia que pide la fecha
de entrega, obligatoria, vacía al abrir y desde mañana en hora de Chile.
"""
from datetime import date, timedelta
from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from pedidos.forms import FechaDesdeMananaValidator
from pedidos.models import ItemPedido, Pedido, RegistroEvento

from . import ayudas
from .factorias import (
    crear_pago, crear_pedido, crear_producto, crear_usuario, momento_chile,
)

# 23:30 en Chile del 15 de octubre: en UTC ya es el 16. «Mañana» en Chile es el 16.
CASI_MEDIANOCHE = momento_chile(2026, 10, 15, hora=23, minuto=30)
MANANA_CHILE = date(2026, 10, 16)


def ruta(pedido_o_pk):
    pk = getattr(pedido_o_pk, 'pk', pedido_o_pk)
    return f'/pedido/duplicar/{pk}/'


class ReabrirBase(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)
        self.producto_a = crear_producto()
        self.producto_b = crear_producto()
        # Los ítems (2 × $5.000 + 1,5 × $3.000 = $14.500) no cuadran con el total a propósito (D3).
        self.original = crear_pedido(
            estado='TERMINADO', estado_pago='PAGADO', valor_venta=25_000,
            fecha_entrega=date(2026, 9, 1), creado_por=crear_usuario(),
            items=[
                {'producto': self.producto_a, 'cantidad': '2', 'precio_unitario': 5_000},
                {'producto': self.producto_b, 'cantidad': Decimal('1.5'), 'precio_unitario': 3_000},
            ])
        crear_pago(self.original, monto=25_000)

    def reabrir(self, fecha, momento=CASI_MEDIANOCHE):
        datos = {} if fecha is None else {'fecha_entrega': str(fecha)}
        with ayudas.congelar_hora(momento), self.captureOnCommitCallbacks(execute=True):
            return self.client.post(ruta(self.original), datos)

    def nuevos(self):
        return Pedido.objects.exclude(pk=self.original.pk)


class CopiaTests(ReabrirBase):
    def test_copia_los_items_con_producto_cantidad_y_precio(self):
        self.reabrir(MANANA_CHILE)

        nuevo = self.nuevos().get()
        copiados = sorted(nuevo.items.values_list('producto_id', 'cantidad', 'precio_unitario'))
        originales = sorted(self.original.items.values_list('producto_id', 'cantidad', 'precio_unitario'))
        self.assertEqual(copiados, originales)
        self.assertIn((self.producto_b.pk, Decimal('1.50'), 3_000), copiados)
        self.assertEqual(self.original.items.count(), 2)  # el original conserva los suyos

    def test_no_copia_pagos_y_nace_pendiente(self):
        self.reabrir(MANANA_CHILE)

        nuevo = self.nuevos().get()
        self.assertFalse(nuevo.pagos.exists())
        self.assertEqual((nuevo.estado, nuevo.estado_pago), ('PENDIENTE', 'PENDIENTE'))
        self.assertEqual(nuevo.creado_por, self.usuario)

    def test_conserva_valor_venta_y_usa_la_fecha_elegida(self):
        respuesta = self.reabrir(MANANA_CHILE)

        nuevo = self.nuevos().get()
        self.assertRedirects(respuesta, f'/{nuevo.pk}/', fetch_redirect_response=False)
        self.assertEqual(nuevo.valor_venta, 25_000)
        self.assertEqual(nuevo.fecha_entrega, MANANA_CHILE)

    def test_pedido_sin_items(self):
        self.original.items.all().delete()

        self.reabrir(MANANA_CHILE)

        self.assertFalse(self.nuevos().get().items.exists())

    def test_un_evento_pedido_duplicado(self):
        self.reabrir(MANANA_CHILE)

        nuevo = self.nuevos().get()
        eventos = list(RegistroEvento.objects.values_list('tipo', 'entidad_id'))
        self.assertEqual(eventos, [('pedido_duplicado', nuevo.pk)])


class FechaTests(ReabrirBase):
    def assertRechaza(self, fecha):
        respuesta = self.reabrir(fecha)
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'pedidos/pedido_duplicar.html')
        self.assertContains(respuesta, 'role="alert"')
        self.assertFalse(self.nuevos().exists())
        self.assertFalse(ItemPedido.objects.exclude(pedido=self.original).exists())
        self.assertFalse(RegistroEvento.objects.exists())

    def test_vacia_se_rechaza(self):
        self.assertRechaza(None)
        self.assertRechaza('')

    def test_pasada_se_rechaza(self):
        self.assertRechaza(date(2026, 10, 1))

    def test_hoy_en_chile_se_rechaza(self):
        self.assertRechaza(date(2026, 10, 15))

    def test_manana_en_chile_se_acepta_aunque_en_utc_ya_sea_ese_dia(self):
        # Con la fecha UTC (16) como «hoy», el 16 se rechazaría: se exige la fecha local.
        self.reabrir(MANANA_CHILE)
        self.assertEqual(self.nuevos().get().fecha_entrega, MANANA_CHILE)

    def test_fecha_futura_se_acepta(self):
        self.reabrir(date(2026, 12, 24))
        self.assertEqual(self.nuevos().get().fecha_entrega, date(2026, 12, 24))


class PaginaTests(ReabrirBase):
    def test_get_muestra_la_pagina_con_la_fecha_vacia_y_no_escribe(self):
        with ayudas.congelar_hora(CASI_MEDIANOCHE):
            respuesta = self.client.get(ruta(self.original))

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'pedidos/pedido_duplicar.html')
        html = respuesta.content.decode()
        self.assertIn('<label for="id_fecha_entrega"', html)
        self.assertIn('data-bloquear-envio', html)
        self.assertIn('name="csrfmiddlewaretoken"', html)
        self.assertIn(f'min="{MANANA_CHILE.isoformat()}"', html)
        self.assertNotIn('value="2026-09-01"', html)  # vacía al abrir, no la del original
        self.assertNotIn('role="alert"', html)
        self.assertFalse(self.nuevos().exists())
        self.assertFalse(RegistroEvento.objects.exists())

    def test_anonimo_va_al_acceso(self):
        self.client.logout()
        for metodo in ('get', 'post'):
            with self.subTest(metodo=metodo):
                respuesta = getattr(self.client, metodo)(ruta(self.original))
                self.assertEqual(respuesta.status_code, 302)
                self.assertIn(settings.LOGIN_URL, respuesta['Location'])
        self.assertFalse(self.nuevos().exists())

    def test_pk_inexistente_da_404(self):
        for metodo in ('get', 'post'):
            with self.subTest(metodo=metodo):
                self.assertEqual(getattr(self.client, metodo)(ruta(999_999)).status_code, 404)

    def test_detalle_enlaza_a_la_pagina(self):
        html = self.client.get(f'/{self.original.pk}/').content.decode()
        self.assertIn(f'href="{ruta(self.original)}"', html)
        self.assertNotIn(f'action="{ruta(self.original)}"', html)

    def test_consultas_de_la_pagina(self):
        # Medición 14-02: la confirmación de eliminar usa 4 consultas; esta no supera 4 + 1.
        with CaptureQueriesContext(connection) as consultas:
            self.client.get(ruta(self.original))
        self.assertLessEqual(len(consultas.captured_queries), 5)


class AtomicidadTests(ReabrirBase):
    def test_si_falla_la_copia_de_items_no_queda_nada(self):
        with mock.patch.object(ItemPedido.objects, 'bulk_create', side_effect=RuntimeError('falla')):
            with self.assertRaises(RuntimeError):
                self.reabrir(MANANA_CHILE)

        self.assertFalse(self.nuevos().exists())
        self.assertEqual(ItemPedido.objects.count(), 2)
        self.assertFalse(RegistroEvento.objects.exists())

    def test_vista_usa_un_solo_atomic(self):
        import inspect
        from pedidos import views
        fuente = inspect.getsource(views.duplicar_pedido)
        self.assertEqual(fuente.count('transaction.atomic()'), 1)


class ValidadorTests(TestCase):
    def test_rechaza_hoy_y_acepta_manana_en_hora_de_chile(self):
        validar = FechaDesdeMananaValidator()
        with ayudas.congelar_hora(CASI_MEDIANOCHE):
            with self.assertRaises(ValidationError):
                validar(date(2026, 10, 15))
            validar(MANANA_CHILE)
            self.assertEqual(validar.minimo(), MANANA_CHILE)
        self.assertEqual(timezone.localdate(CASI_MEDIANOCHE) + timedelta(days=1), MANANA_CHILE)
