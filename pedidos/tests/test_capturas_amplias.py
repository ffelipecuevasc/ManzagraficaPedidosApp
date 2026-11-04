"""Capturas amplias de views.py que incumplían la regla 4 (01-09).

Las de ítems (pedidos y cotizaciones) desaparecieron en la 03-02 y la 03-03: sus pruebas viven en
`test_pedidos.py` (`CrearPedidoItemFallidoTests`) y `test_fronteras_transaccionales.py`.
Quedan las de respaldo y restauración (04-04).

Cada prueba provoca el fallo con datos inválidos o con `mock` (sin ejecutar mysql ni
mysqldump) y comprueba que queda un ERROR de `pedidos.views` con traza y con la petición,
y que el usuario no ve el texto de la excepción.
"""
import os
import tempfile
from unittest import mock

from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from pedidos import views

from . import factorias

TEXTO_TECNICO = 'detalle-tecnico /ruta/secreta mysqldump: error 1045'


class CapturasBase(TestCase):
    def setUp(self):
        self.usuario = factorias.crear_superusuario()
        self.client.force_login(self.usuario)

    def assertErrorRegistrado(self, registros, texto):
        errores = [r for r in registros.records if r.levelname == 'ERROR']
        self.assertEqual(len(errores), 1, [r.getMessage() for r in registros.records])
        registro = errores[0]
        self.assertIn(texto, registro.getMessage())
        self.assertIsNotNone(registro.exc_info, 'el registro debe llevar la traza')
        self.assertEqual(registro.request.user, self.usuario)

    def mensajes(self, respuesta):
        return [str(m) for m in get_messages(respuesta.wsgi_request)]


class CapturasRespaldoTests(CapturasBase):
    """Opción C: se registra, el usuario ve un texto fijo y, en la restauración, el estado de la base."""

    def test_generar_respaldo_fallido_registra_y_muestra_texto_fijo(self):
        with mock.patch.object(views, 'generar_respaldo_mysql', side_effect=RuntimeError(TEXTO_TECNICO)), \
                self.assertLogs('pedidos.views', 'ERROR') as registros:
            respuesta = self.client.get('/base_datos/respaldar_bd/accion/')
        self.assertRedirects(respuesta, '/base_datos/respaldar_bd/', fetch_redirect_response=False)
        self.assertErrorRegistrado(registros, 'respaldo')
        self.assertEqual(self.mensajes(respuesta),
                         ['No se pudo generar el respaldo. El detalle quedó en el registro del servidor.'])

    def restaurar(self, carpeta, **parches):
        archivo = SimpleUploadedFile('ficticio.sql', b'-- volcado ficticio\n')
        with mock.patch.object(views.settings, 'BASE_DIR', carpeta), \
                mock.patch.object(views, 'generar_respaldo_mysql', **parches.get('respaldo', {})), \
                mock.patch.object(views, 'restaurar_bd_mysql', **parches.get('restaurar', {})), \
                self.assertLogs('pedidos.views', 'ERROR') as registros:
            respuesta = self.client.post('/base_datos/restaurar_bd/', {'archivo_sql': archivo})
        self.assertRedirects(respuesta, '/base_datos/restaurar_bd/', fetch_redirect_response=False)
        return respuesta, registros

    def test_respaldo_previo_fallido_registra_y_no_restaura(self):
        with tempfile.TemporaryDirectory() as carpeta:
            respuesta, registros = self.restaurar(carpeta, respaldo={'side_effect': RuntimeError(TEXTO_TECNICO)})
            self.assertEqual(os.listdir(os.path.join(carpeta, 'backups', 'tmp')), [])
        self.assertErrorRegistrado(registros, 'respaldo de seguridad previo')
        self.assertEqual(self.mensajes(respuesta), [
            'Operación cancelada: no se pudo crear el respaldo de seguridad previo, así que la base no se tocó.'])

    def test_restauracion_fallida_nombra_el_respaldo_previo(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = os.path.join(carpeta, 'backups', 'respaldo_01-01-2026_00-00-00.sql')
            respuesta, registros = self.restaurar(carpeta, respaldo={'return_value': ruta},
                                                  restaurar={'side_effect': RuntimeError(TEXTO_TECNICO)})
        self.assertErrorRegistrado(registros, 'restauración')
        self.assertEqual(self.mensajes(respuesta), [
            'La restauración falló. La base puede haber quedado restaurada en parte: revisa el registro '
            'del servidor antes de seguir. El respaldo de seguridad previo es '
            'respaldo_01-01-2026_00-00-00.sql. Está en la carpeta backups/ del servidor.'])

    def test_restauracion_fallida_antes_del_respaldo_previo_no_nombra_archivo(self):
        with tempfile.TemporaryDirectory() as carpeta, \
                mock.patch.object(views.FileSystemStorage, 'save', side_effect=OSError(TEXTO_TECNICO)):
            respuesta, registros = self.restaurar(carpeta)
        self.assertErrorRegistrado(registros, 'restauración')
        self.assertEqual(self.mensajes(respuesta), [
            'La restauración falló. La base puede haber quedado restaurada en parte: revisa el registro '
            'del servidor antes de seguir.'])
