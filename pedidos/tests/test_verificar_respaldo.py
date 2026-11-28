"""Script versionado `scripts/verificar_respaldo.py` con 20 tablas (iteración 14-04).

Solo volcados ficticios armados aquí, en una carpeta temporal; nunca un respaldo real. Un volcado
de 19 tablas (anterior a la `0010`) da NO VÁLIDO con una faltante, `pedidos_secuenciafolio`: el
mismo trato que reciben hoy los de 18 (anteriores a la `0007`), que se verifican con la versión
del script de su época (`docs/operacion/respaldo.md`).
"""
import contextlib
import importlib.util
import io
import os
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

RUTA_SCRIPT = Path(__file__).resolve().parents[2] / 'scripts' / 'verificar_respaldo.py'

TABLAS_19 = (
    'pedidos_cliente', 'pedidos_producto', 'pedidos_cotizacion', 'pedidos_itemcotizacion',
    'pedidos_pedido', 'pedidos_itempedido', 'pedidos_pago', 'pedidos_historialbd',
    'pedidos_registroevento', 'auth_group', 'auth_group_permissions', 'auth_permission', 'auth_user',
    'auth_user_groups', 'auth_user_user_permissions', 'django_admin_log', 'django_content_type',
    'django_migrations', 'django_session',
)
TABLAS_20 = TABLAS_19 + ('pedidos_secuenciafolio',)


def volcado(tablas):
    cuerpo = b''.join(f'CREATE TABLE `{t}` (\n  `id` int\n);\n'.encode() for t in tablas)
    return b'-- MySQL dump ficticio\n' + cuerpo + b'\n-- Dump completed on 2026-11-27 10:00:00\n'


def cargar_script():
    spec = importlib.util.spec_from_file_location('verificar_respaldo', RUTA_SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class VerificarRespaldoTests(SimpleTestCase):
    def setUp(self):
        self.script = cargar_script()
        self.carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(self.carpeta.cleanup)

    def ejecutar(self, contenido):
        ruta = os.path.join(self.carpeta.name, 'ficticio.sql')
        with open(ruta, 'wb') as archivo:
            archivo.write(contenido)
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = self.script.main([ruta, '--min-bytes', '1'])
        return codigo, salida.getvalue()

    def test_espera_20_tablas(self):
        self.assertEqual(len(self.script.TABLAS_ESPERADAS), 20)
        self.assertIn('pedidos_secuenciafolio', self.script.TABLAS_ESPERADAS)

    def test_volcado_de_20_tablas_es_valido(self):
        codigo, texto = self.ejecutar(volcado(TABLAS_20))
        self.assertEqual(codigo, 0)
        self.assertIn('Tablas esperadas encontradas: 20 de 20', texto)
        self.assertIn('Resultado: VÁLIDO', texto)

    def test_volcado_de_19_tablas_falta_la_secuencia(self):
        codigo, texto = self.ejecutar(volcado(TABLAS_19))
        self.assertEqual(codigo, 1)
        self.assertIn('Tablas esperadas encontradas: 19 de 20', texto)
        self.assertIn('Tablas faltantes: pedidos_secuenciafolio', texto)
        self.assertIn('Resultado: NO VÁLIDO (1 tabla(s) faltante(s))', texto)

    def test_no_imprime_el_contenido(self):
        _, texto = self.ejecutar(volcado(TABLAS_20))
        self.assertNotIn('`id` int', texto)
