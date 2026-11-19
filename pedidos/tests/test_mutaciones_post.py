"""Mutaciones solo por POST (04-01; AUD-02-002, AUD-02-006, AUD-02-028 y AUD-03-002).

Las afirmaciones de GET → 405 están en R6a, R6b y R6c (`test_regresiones.py`); la confirmación de
eliminar pago con GET 200, en R7; el autor del duplicado, en R19. Aquí van las demás.
"""
import os
import tempfile
from pathlib import Path
from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from pedidos import views
from pedidos.models import Pago, Pedido

from . import ayudas
from .factorias import crear_pago, crear_pedido, crear_superusuario, crear_usuario

PLANTILLAS = Path(settings.BASE_DIR) / 'pedidos' / 'templates' / 'pedidos'


def _plantilla(nombre):
    return (PLANTILLAS / nombre).read_text(encoding='utf-8')


class CambiarEstadoPostTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_usuario())

    def test_post_cambia_el_estado(self):
        pedido = crear_pedido(estado='PENDIENTE')

        respuesta = self.client.post(f'/pedido/{pedido.pk}/cambiar/EN_PROCESO/')

        pedido.refresh_from_db()
        self.assertRedirects(respuesta, reverse('detalle_pedido', args=[pedido.pk]),
                             fetch_redirect_response=False)
        self.assertEqual(pedido.estado, 'EN_PROCESO')


class DuplicarPostTests(TestCase):
    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)

    def test_post_duplica_con_el_usuario_como_autor(self):
        original = crear_pedido()

        self.client.post(f'/pedido/duplicar/{original.pk}/', ayudas.datos_reabrir())  # fecha: 14-02

        duplicado = Pedido.objects.exclude(pk=original.pk).get()
        self.assertEqual(duplicado.creado_por, self.usuario)


class EliminarPagoConfirmacionTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_usuario())

    def test_get_muestra_la_confirmacion_y_no_borra(self):
        pago = crear_pago(crear_pedido(valor_venta=10_000), monto=4_000)

        respuesta = self.client.get(f'/pagos/eliminar/{pago.pk}/')

        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, 'pedidos/pago_confirm_delete.html')
        self.assertContains(respuesta, 'method="post"')
        self.assertContains(respuesta, 'name="csrfmiddlewaretoken"')
        self.assertContains(respuesta, 'data-bloquear-envio')
        self.assertTrue(Pago.objects.filter(pk=pago.pk).exists())

    def test_get_a_pago_inexistente_responde_404(self):
        self.assertEqual(self.client.get('/pagos/eliminar/999999/').status_code, 404)


class GenerarRespaldoPostTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_superusuario())
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        self.ruta = os.path.join(carpeta.name, 'respaldo_prueba.sql')
        with open(self.ruta, 'w', encoding='utf-8') as archivo:
            archivo.write('-- respaldo de prueba\n')

    def test_post_descarga_el_respaldo(self):
        with mock.patch.object(views, 'generar_respaldo_mysql', return_value=self.ruta) as generar:
            respuesta = self.client.post('/base_datos/respaldar_bd/accion/')
        ayudas.cerrar_respuesta(respuesta)

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(generar.called)
        self.assertIn('attachment', respuesta['Content-Disposition'])


class PlantillasConFormularioPostTests(TestCase):
    """Las acciones que escriben son formularios POST con CSRF, no enlaces (regla 8.5)."""

    def setUp(self):
        self.client.force_login(crear_usuario())

    def _detalle(self, estado):
        pedido = crear_pedido(estado=estado)
        return pedido, self.client.get(reverse('detalle_pedido', args=[pedido.pk])).content.decode()

    def test_cambiar_estado_es_formulario_post(self):
        for estado, destino in (('PENDIENTE', 'EN_PROCESO'), ('EN_PROCESO', 'TERMINADO')):
            with self.subTest(estado=estado):
                pedido, html = self._detalle(estado)
                ruta = f'/pedido/{pedido.pk}/cambiar/{destino}/'
                self.assertNotIn(f'href="{ruta}"', html)
                self.assertIn(f'<form method="post" action="{ruta}"', html)
                self.assertIn('name="csrfmiddlewaretoken"', html)

    def test_reabrir_es_enlace_a_la_pagina_de_la_fecha(self):
        # Desde la 14-02 (D4) Reabrir lleva a una página que pide la fecha; esa página crea por
        # POST con CSRF (test_duplicar_items.PaginaTests). Excepción a la 04-01, como P1.
        pedido, html = self._detalle('TERMINADO')
        ruta = f'/pedido/duplicar/{pedido.pk}/'
        self.assertNotIn(f'data-url="{ruta}"', html)
        self.assertIn(f'href="{ruta}"', html)
        self.assertNotIn(f'action="{ruta}"', html)

    def test_respaldo_es_formulario_post_sin_recarga(self):
        texto = _plantilla('respaldar_bd.html')

        self.assertNotIn('location.reload', texto)
        self.assertNotIn("href=\"{% url 'generar_respaldo_bd' %}\"", texto)
        self.assertIn("action=\"{% url 'generar_respaldo_bd' %}\"", texto)
        self.assertIn('{% csrf_token %}', texto)


class AnonimoVaAlAccesoTests(TestCase):
    """Con `@require_POST` como decorador más interno, un anónimo recibe 302 al acceso, no 405."""

    def test_get_anonimo_redirige_al_acceso(self):
        pedido = crear_pedido()
        rutas = [
            f'/pedido/{pedido.pk}/cambiar/EN_PROCESO/',
            f'/pedido/duplicar/{pedido.pk}/',
            '/base_datos/respaldar_bd/accion/',
        ]
        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertEqual(respuesta.status_code, 302)
                self.assertIn(settings.LOGIN_URL, respuesta['Location'])
