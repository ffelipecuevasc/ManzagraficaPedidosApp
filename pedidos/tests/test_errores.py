"""Manejo de errores sin middleware propio: 404, 500 y trazas completas (01-03).

Con DEBUG=False forzado, como en producción. El cliente de pruebas no relanza la excepción
de la vista (`raise_request_exception = False`), para ver la respuesta que recibe el usuario.
"""
import logging
from unittest import mock

from django.conf import settings
from django.test import TestCase, override_settings

from .factorias import crear_cliente, crear_pago, crear_usuario
from .test_registro import formatear_como_error_log


@override_settings(DEBUG=False)
class ErroresSinMiddlewareTests(TestCase):
    def setUp(self):
        self.client.raise_request_exception = False
        self.client.force_login(crear_usuario())

    def test_middleware_propio_retirado(self):
        self.assertNotIn('pedidos.middleware.ErrorHandlingMiddleware', settings.MIDDLEWARE)
        with self.assertRaises(ImportError):
            import pedidos.middleware  # noqa: F401

    def test_pedido_inexistente_responde_404_con_su_plantilla(self):
        respuesta = self.client.get('/999999/')
        self.assertEqual(respuesta.status_code, 404)
        self.assertTemplateUsed(respuesta, 'pedidos/errors/404.html')

    def test_excepcion_en_vista_sin_decorador_responde_500_con_traza(self):
        with mock.patch('pedidos.views.Paginator', side_effect=RuntimeError('fallo forzado sin decorador')):
            with self.assertLogs('django.request', 'ERROR') as capturado:
                respuesta = self.client.get('/pagos/lista/')
        self.assertEqual(respuesta.status_code, 500)
        self.assertTemplateUsed(respuesta, 'pedidos/errors/500.html')
        registro = capturado.records[0]
        self.assertIsNotNone(registro.exc_info)
        linea = formatear_como_error_log(registro)
        self.assertIn('metodo=GET ruta=/pagos/lista/ usuario=', linea)
        self.assertIn('excepcion=RuntimeError', linea)
        self.assertIn('Traceback (most recent call last):', linea)
        self.assertIn('RuntimeError: fallo forzado sin decorador', linea)

    def test_excepcion_en_vista_con_transaccion_segura_registra_vista_y_traza(self):
        cliente = crear_cliente()
        with mock.patch('pedidos.views.ClienteForm', side_effect=RuntimeError('fallo forzado con decorador')):
            with self.assertLogs('django.request', 'ERROR'):  # el resumen «Internal Server Error»
                with self.assertLogs('pedidos.decorators', 'ERROR') as capturado:
                    respuesta = self.client.get(f'/clientes/editar/{cliente.pk}/')
        self.assertEqual(respuesta.status_code, 500)
        linea = formatear_como_error_log(capturado.records[0])
        self.assertIn('registrador=pedidos.decorators', linea)
        self.assertIn(f'ruta=/clientes/editar/{cliente.pk}/', linea)
        self.assertIn('excepcion=RuntimeError', linea)
        self.assertIn('editar_cliente', linea)
        self.assertIn('RuntimeError: fallo forzado con decorador', linea)

    def test_regresion_eliminar_pago_deja_tipo_y_traza(self):
        # Caso real del 2026-10-22 (AUD-02-002, la plantilla se corrige en 04-01). Esta prueba
        # no fija el defecto: comprueba que, mientras exista, deja su causa completa en el registro.
        pago = crear_pago()
        with self.assertLogs('django.request', 'ERROR'):
            with self.assertLogs('pedidos.decorators', 'ERROR') as capturado:
                respuesta = self.client.get(f'/pagos/eliminar/{pago.pk}/')
        self.assertEqual(respuesta.status_code, 500)
        linea = formatear_como_error_log(capturado.records[0])
        self.assertIn(f'metodo=GET ruta=/pagos/eliminar/{pago.pk}/', linea)
        self.assertIn('excepcion=TemplateDoesNotExist', linea)
        self.assertIn('eliminar_pago', linea)
        self.assertIn('Traceback (most recent call last):', linea)
        self.assertIn('TemplateDoesNotExist: pedidos/pago_confirm_delete.html', linea)

    def test_pagina_500_sin_detalles_tecnicos(self):
        with mock.patch('pedidos.views.Paginator', side_effect=RuntimeError('detalle-secreto-de-la-excepcion')):
            with self.assertLogs('django.request', 'ERROR'):
                respuesta = self.client.get('/pagos/lista/')
        html = respuesta.content.decode()
        self.assertEqual(respuesta.status_code, 500)
        self.assertIn('Algo salió mal', html)
        self.assertNotIn('detalle-secreto-de-la-excepcion', html)
        self.assertNotIn('Traceback', html)
        self.assertNotIn('RuntimeError', html)
        self.assertNotIn('correos', html)
        self.assertNotIn('ERROR</span>', html)  # sin el código «500 ERROR»


class PrintsDiagnosticoTests(TestCase):
    def test_borrado_de_respaldos_antiguos_se_registra(self):
        from pedidos import utils

        with mock.patch.object(utils.glob, 'glob', return_value=['a.sql', 'b.sql']), \
                mock.patch.object(utils.os.path, 'getmtime', side_effect=[1, 2]), \
                mock.patch.object(utils.os, 'remove', side_effect=[None]):
            with self.assertLogs('pedidos.utils', 'INFO') as capturado:
                utils.limpiar_backups_antiguos('respaldos', mantener=1)
        self.assertIn('Respaldo antiguo eliminado: a.sql', capturado.output[0])

    def test_creacion_de_pedido_invalida_registra_solo_nombres_de_campos(self):
        self.client.force_login(crear_usuario())
        with self.assertLogs('pedidos.views', 'INFO') as capturado:
            self.client.post('/pedidos/nuevo/', {'resumen_pedido': 'texto-del-usuario-123'})
        salida = '\n'.join(capturado.output)
        self.assertIn('Formulario de pedido inválido', salida)
        self.assertNotIn('texto-del-usuario-123', salida)
