"""Configuración del registro de la aplicación: formato, contexto y ruido (01-02)."""
import io
import logging
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from .factorias import crear_usuario


def formatear_como_error_log(record):
    """Aplica el filtro y el formato del manejador real (el de la raíz, a stderr)."""
    manejador = next(h for h in logging.getLogger().handlers if h.name == 'stderr')
    manejador.filter(record)
    return manejador.format(record)


class FormatoRegistroTests(TestCase):
    def setUp(self):
        self.fabrica = RequestFactory()

    def test_error_en_peticion_lleva_contexto_y_traza_completa(self):
        request = self.fabrica.get('/pagos/eliminar/1056/?orden=fecha')
        request.user = crear_usuario()
        logger = logging.getLogger('pedidos.views')
        with self.assertLogs('pedidos', 'ERROR') as capturado:
            try:
                raise LookupError('plantilla de prueba')
            except LookupError:
                logger.exception('No se pudo eliminar el pago', extra={'request': request})
        linea = formatear_como_error_log(capturado.records[0])
        cabecera = linea.splitlines()[0]
        self.assertEqual(
            cabecera,
            f'nivel=ERROR registrador=pedidos.views metodo=GET ruta=/pagos/eliminar/1056/ '
            f'usuario={request.user.pk} excepcion=LookupError mensaje="No se pudo eliminar el pago"',
        )
        self.assertIn('Traceback (most recent call last):', linea)
        self.assertIn('LookupError: plantilla de prueba', linea)
        self.assertNotIn('orden=fecha', linea)  # sin cadena de consulta

    def test_anonimo_y_sin_datos_del_formulario(self):
        request = self.fabrica.post('/accounts/login/', {'username': 'alguien', 'password': 'secreto-123'})
        request.user = AnonymousUser()
        with self.assertLogs('pedidos', 'WARNING') as capturado:
            logging.getLogger('pedidos.views').warning('Acceso rechazado', extra={'request': request})
        linea = formatear_como_error_log(capturado.records[0])
        self.assertIn('metodo=POST ruta=/accounts/login/ usuario=anonimo excepcion=-', linea)
        self.assertNotIn('secreto-123', linea)
        self.assertNotIn('alguien', linea)

    def test_sin_peticion_usa_guiones(self):
        with self.assertLogs('pedidos', 'INFO') as capturado:
            logging.getLogger('pedidos.eventos').info('Mensaje "con comillas"\nen dos líneas')
        linea = formatear_como_error_log(capturado.records[0])
        self.assertEqual(
            linea,
            'nivel=INFO registrador=pedidos.eventos metodo=- ruta=- usuario=- excepcion=- '
            'mensaje="Mensaje \\"con comillas\\"\\nen dos líneas"',
        )

    def test_filtro_no_falla_con_usuario_roto(self):
        class UsuarioRoto:
            @property
            def is_authenticated(self):
                raise RuntimeError('sesión dañada')

        request = self.fabrica.get('/')
        request.user = UsuarioRoto()
        record = logging.LogRecord('pedidos.views', logging.ERROR, __file__, 1, 'Error', None, None)
        record.request = request
        with mock.patch('sys.stderr', new_callable=io.StringIO) as salida_error:
            linea = formatear_como_error_log(record)
        self.assertTrue(linea.startswith('nivel=ERROR registrador=pedidos.views'))
        self.assertIn('Fallo del filtro de contexto: RuntimeError', salida_error.getvalue())


class NivelesRegistradoresTests(TestCase):
    def test_fonttools_y_weasyprint_solo_desde_warning(self):
        for nombre in ('fontTools', 'fontTools.subset', 'weasyprint'):
            with self.subTest(registrador=nombre):
                logger = logging.getLogger(nombre)
                self.assertFalse(logger.isEnabledFor(logging.INFO))
                with self.assertLogs(nombre, 'WARNING') as capturado:
                    logger.warning('aviso de prueba')
                self.assertEqual(len(capturado.records), 1)

    def test_recorte_de_fuentes_de_weasyprint_no_llega_a_la_raiz(self):
        # Reproduce weasyprint.logger.capture_logs: baja fontTools a DEBUG temporalmente.
        from weasyprint.logger import capture_logs

        raiz = logging.getLogger()
        with mock.patch.object(raiz.handlers[0], 'emit') as emitir_raiz:
            with capture_logs('fontTools', level=logging.WARNING) as capturados:
                logging.getLogger('fontTools.subset').info('name pruned')
                logging.getLogger('fontTools.ttLib.ttFont').debug("Reading 'meta' table")
        emitir_raiz.assert_not_called()
        self.assertEqual(capturados, [])
        self.assertFalse(logging.getLogger('fontTools').isEnabledFor(logging.INFO))  # nivel restaurado

    def test_niveles_de_django_y_de_la_aplicacion(self):
        self.assertFalse(logging.getLogger('django.request').isEnabledFor(logging.WARNING))
        self.assertTrue(logging.getLogger('django.request').isEnabledFor(logging.ERROR))
        self.assertTrue(logging.getLogger('django.security').isEnabledFor(logging.WARNING))
        self.assertTrue(logging.getLogger('pedidos.views').isEnabledFor(logging.INFO))
        self.assertFalse(logging.getLogger('pedidos.views').isEnabledFor(logging.DEBUG))

    def test_un_solo_manejador_en_la_raiz(self):
        nombres = [h.name for h in logging.getLogger().handlers]
        self.assertEqual(nombres, ['stderr'])
        self.assertEqual(logging.getLogger('django').handlers, [])
