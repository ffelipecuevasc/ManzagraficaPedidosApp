"""Confirmación reforzada al eliminar un pedido con pagos (04-10).

Con pagos, la pantalla dice cuántos son y cuánto suman, y el servidor exige escribir
ELIMINAR (exacto, sensible a mayúsculas, con strip()) y que la cantidad vista coincida
con la real (D2 a D4). Sin pagos se elimina como antes. El evento `pedido_eliminado`
lleva la cantidad de pagos, nunca el monto (D1).

El monto sale con `intcomma`, como en el resto de la aplicación: con `es-cl`, Django pone
un espacio duro (\xa0) como separador de miles, no un punto (PENDIENTE_DESARROLLADOR, 04-10).

TestCase nunca confirma su transacción: los `on_commit` se ejecutan con
`captureOnCommitCallbacks(execute=True)`.
"""
from unittest import mock

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from pedidos.models import ItemPedido, Pago, Pedido, RegistroEvento

from . import factorias

AVISO_FALTA = 'Escribe ELIMINAR para confirmar. No se eliminó nada.'
AVISO_CAMBIO = 'Mientras tanto cambió la cantidad de pagos de este pedido.'
SIN_PAGOS = 'Este pedido no tiene pagos registrados.'


def ruta(pedido):
    return f'/pedido/eliminar/{pedido.pk}/'


class EliminarPedidoBase(TestCase):
    def setUp(self):
        self.usuario = factorias.crear_superusuario()
        self.client.force_login(self.usuario)

    def crear_con_pagos(self, *montos):
        pedido = factorias.crear_pedido(items=[{}])
        for monto in montos:
            factorias.crear_pago(pedido=pedido, monto=monto)
        return pedido

    def enviar(self, pedido, **datos):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(ruta(pedido), datos)

    def assertNadaBorrado(self, pedido, pagos):
        self.assertTrue(Pedido.objects.filter(pk=pedido.pk).exists())
        self.assertEqual(ItemPedido.objects.filter(pedido_id=pedido.pk).count(), 1)
        self.assertEqual(Pago.objects.filter(pedido_id=pedido.pk).count(), pagos)
        self.assertFalse(RegistroEvento.objects.exists())

    def assertBorrado(self, pedido):
        self.assertFalse(Pedido.objects.filter(pk=pedido.pk).exists())
        self.assertFalse(ItemPedido.objects.filter(pedido_id=pedido.pk).exists())
        self.assertFalse(Pago.objects.filter(pedido_id=pedido.pk).exists())

    def evento_unico(self, pedido):
        eventos = list(RegistroEvento.objects.all())
        self.assertEqual(len(eventos), 1, [e.resumen for e in eventos])
        evento = eventos[0]
        self.assertEqual((evento.tipo, evento.usuario, evento.entidad, evento.entidad_id),
                         ('pedido_eliminado', self.usuario, 'pedido', pedido.pk))
        return evento


class AvisoTests(EliminarPedidoBase):
    def test_con_pagos_muestra_cantidad_monto_campo_y_cantidad_oculta(self):
        pedido = self.crear_con_pagos(30_000, 15_000)
        respuesta = self.client.get(ruta(pedido))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, '2 pagos registrados por un total de $45\xa0000')
        self.assertContains(respuesta, 'esos pagos también se borrarán')
        self.assertContains(respuesta, 'name="confirmacion"')
        self.assertContains(respuesta, 'aria-describedby="aviso-pagos"')
        self.assertContains(respuesta, '<label for="confirmacion"')
        self.assertContains(respuesta, '<input type="hidden" name="pagos_vistos" value="2">', html=True)
        self.assertNotContains(respuesta, SIN_PAGOS)

    def test_un_pago_en_singular(self):
        pedido = self.crear_con_pagos(1_500_000)
        respuesta = self.client.get(ruta(pedido))
        self.assertContains(respuesta, '1 pago registrado por un total de $1\xa0500\xa0000')

    def test_sin_pagos_lo_dice_y_no_pide_confirmacion(self):
        pedido = self.crear_con_pagos()
        respuesta = self.client.get(ruta(pedido))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, SIN_PAGOS)
        self.assertNotContains(respuesta, 'name="confirmacion"')
        self.assertContains(respuesta, 'Esta acción es permanente')

    def test_conserva_el_bloqueo_de_doble_envio(self):
        pedido = self.crear_con_pagos(5_000)
        self.assertContains(self.client.get(ruta(pedido)), 'data-bloquear-envio="Eliminando…"')


class EliminarTests(EliminarPedidoBase):
    def test_sin_pagos_se_elimina_como_antes(self):
        pedido = self.crear_con_pagos()
        respuesta = self.enviar(pedido)
        self.assertRedirects(respuesta, '/pedidos/lista/', fetch_redirect_response=False)
        self.assertBorrado(pedido)
        self.assertEqual(self.evento_unico(pedido).resumen, f'Pedido #{pedido.pk} eliminado, sin pagos')

    def test_con_pagos_y_confirmacion_borra_todo_y_registra_la_cantidad(self):
        pedido = self.crear_con_pagos(30_000, 15_000)
        respuesta = self.enviar(pedido, confirmacion='ELIMINAR', pagos_vistos='2')
        self.assertRedirects(respuesta, '/pedidos/lista/', fetch_redirect_response=False)
        self.assertBorrado(pedido)
        evento = self.evento_unico(pedido)
        self.assertEqual(evento.resumen, f'Pedido #{pedido.pk} eliminado, con 2 pagos')
        self.assertNotIn('45', evento.resumen.replace(str(pedido.pk), ''))
        self.assertNotIn(pedido.cliente.nombre, evento.resumen)

    def test_un_pago_en_singular_en_el_evento(self):
        pedido = self.crear_con_pagos(5_000)
        self.enviar(pedido, confirmacion='ELIMINAR', pagos_vistos='1')
        self.assertEqual(self.evento_unico(pedido).resumen, f'Pedido #{pedido.pk} eliminado, con 1 pago')

    def test_espacios_alrededor_de_eliminar_se_aceptan(self):
        pedido = self.crear_con_pagos(5_000)
        respuesta = self.enviar(pedido, confirmacion='  ELIMINAR \n', pagos_vistos='1')
        self.assertEqual(respuesta.status_code, 302)
        self.assertBorrado(pedido)


class SinConfirmacionTests(EliminarPedidoBase):
    def test_falta_vacia_o_distinta_no_borra_ni_registra(self):
        casos = {
            'sin campo': {'pagos_vistos': '2'},
            'vacío': {'confirmacion': '', 'pagos_vistos': '2'},
            'solo espacios': {'confirmacion': '   ', 'pagos_vistos': '2'},
            'minúsculas': {'confirmacion': 'eliminar', 'pagos_vistos': '2'},
            'otra palabra': {'confirmacion': 'BORRAR', 'pagos_vistos': '2'},
        }
        pedido = self.crear_con_pagos(30_000, 15_000)
        for nombre, datos in casos.items():
            with self.subTest(nombre):
                respuesta = self.enviar(pedido, **datos)
                self.assertEqual(respuesta.status_code, 200)
                self.assertContains(respuesta, AVISO_FALTA)
                self.assertContains(respuesta, 'role="alert"')
                self.assertContains(respuesta, '2 pagos registrados por un total de $45\xa0000')
                self.assertNadaBorrado(pedido, pagos=2)

    def test_cantidad_cambiada_repinta_con_las_cifras_nuevas_sin_borrar(self):
        pedido = self.crear_con_pagos(10_000)
        self.client.get(ruta(pedido))
        factorias.crear_pago(pedido=pedido, monto=2_500)
        respuesta = self.enviar(pedido, confirmacion='ELIMINAR', pagos_vistos='1')
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, AVISO_CAMBIO)
        self.assertContains(respuesta, 'No se eliminó nada.')
        self.assertContains(respuesta, '2 pagos registrados por un total de $12\xa0500')
        self.assertContains(respuesta, '<input type="hidden" name="pagos_vistos" value="2">', html=True)
        self.assertNadaBorrado(pedido, pagos=2)

    def test_pagos_aparecidos_en_un_pedido_que_se_vio_sin_pagos_no_se_borran(self):
        pedido = self.crear_con_pagos()
        factorias.crear_pago(pedido=pedido, monto=2_500)
        respuesta = self.enviar(pedido, pagos_vistos='0')
        self.assertContains(respuesta, AVISO_CAMBIO)
        self.assertNadaBorrado(pedido, pagos=1)

    def test_con_pagos_sin_cantidad_vista_no_se_borra(self):
        pedido = self.crear_con_pagos(5_000)
        respuesta = self.enviar(pedido, confirmacion='ELIMINAR')
        self.assertEqual(respuesta.status_code, 200)
        self.assertNadaBorrado(pedido, pagos=1)


class AtomicidadTests(EliminarPedidoBase):
    def test_un_solo_atomic_si_delete_falla_no_cambia_nada_ni_hay_evento(self):
        pedido = self.crear_con_pagos(5_000)
        with mock.patch.object(Pedido, 'delete', side_effect=RuntimeError('falla forzada')):
            with self.assertRaises(RuntimeError):
                self.enviar(pedido, confirmacion='ELIMINAR', pagos_vistos='1')
        self.assertNadaBorrado(pedido, pagos=1)

    def test_recuento_y_borrado_ocurren_dentro_del_mismo_atomic(self):
        pedido = self.crear_con_pagos(5_000)
        profundidades = []
        original = Pedido.delete

        def delete_espia(instancia, *args, **kwargs):
            profundidades.append(len(connection.savepoint_ids))
            return original(instancia, *args, **kwargs)

        base = len(connection.savepoint_ids)  # los atomic propios de TestCase
        with mock.patch.object(Pedido, 'delete', delete_espia):
            self.enviar(pedido, confirmacion='ELIMINAR', pagos_vistos='1')
        self.assertEqual(profundidades, [base + 1])  # la vista agrega exactamente uno


class ConsultasTests(EliminarPedidoBase):
    """Excepción a AGENTS.md, sección 11: como máximo +1 consulta (04-10)."""

    def consultas(self, metodo, pedido, **datos):
        with CaptureQueriesContext(connection) as capturadas:
            getattr(self.client, metodo)(ruta(pedido), datos)
        return [q['sql'] for q in capturadas.captured_queries
                if not q['sql'].upper().startswith(('SAVEPOINT', 'RELEASE SAVEPOINT'))]

    def test_get_con_pagos_a_lo_mas_una_consulta_mas(self):
        pedido = self.crear_con_pagos(5_000, 5_000)
        self.assertLessEqual(len(self.consultas('get', pedido)), 4 + 1)  # medido antes del cambio: 4

    def test_post_con_pagos_a_lo_mas_una_consulta_mas(self):
        pedido = self.crear_con_pagos(5_000, 5_000)
        self.assertLessEqual(len(self.consultas('post', pedido, confirmacion='ELIMINAR', pagos_vistos='2')), 6 + 1)  # medido antes del cambio: 6
