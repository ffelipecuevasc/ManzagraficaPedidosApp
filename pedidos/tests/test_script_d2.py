"""Script versionado `scripts/diagnostico/revisar_volcado_d2.py` (04-06).

Solo volcados ficticios (`ayudas.VOLCADO_VALIDO` y variantes) en una carpeta temporal; nunca
un respaldo real. Comprueba el resultado, el código de salida y que no imprime el contenido.
"""
import contextlib
import importlib.util
import io
import os
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from pedidos.tests.ayudas import VOLCADO_VALIDO

RUTA_SCRIPT = Path(__file__).resolve().parents[2] / 'scripts' / 'diagnostico' / 'revisar_volcado_d2.py'


def cargar_script():
    spec = importlib.util.spec_from_file_location('revisar_volcado_d2', RUTA_SCRIPT)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


class ScriptD2Tests(SimpleTestCase):
    def setUp(self):
        self.script = cargar_script()
        self.carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(self.carpeta.cleanup)

    def ejecutar(self, contenido=None, argv=None):
        if argv is None:
            ruta = os.path.join(self.carpeta.name, 'ficticio.sql')
            with open(ruta, 'wb') as archivo:
                archivo.write(contenido)
            argv = [ruta]
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = self.script.main(argv)
        return codigo, salida.getvalue()

    def test_volcado_valido_cumple(self):
        codigo, salida = self.ejecutar(VOLCADO_VALIDO)
        self.assertEqual(codigo, 0)
        self.assertIn('RESULTADO: CUMPLE D2', salida)

    def test_volcado_cortado_no_cumple(self):
        codigo, salida = self.ejecutar(VOLCADO_VALIDO.replace(b'-- Dump completed', b'-- Cortado'))
        self.assertEqual(codigo, 1)
        self.assertIn('linea_de_cierre: False', salida)
        self.assertIn('RESULTADO: NO CUMPLE D2', salida)

    def test_volcado_vacio_no_cumple(self):
        codigo, salida = self.ejecutar(b'')
        self.assertEqual(codigo, 1)
        self.assertIn('no_vacio: False', salida)

    def test_no_imprime_el_contenido(self):
        _, salida = self.ejecutar(VOLCADO_VALIDO)
        self.assertNotIn('MySQL dump', salida)
        self.assertNotIn('pedidos_pedido`', salida)

    def test_sin_argumento_o_archivo_inexistente_no_se_ejecuta(self):
        self.assertEqual(self.ejecutar(argv=[])[0], 2)
        codigo, salida = self.ejecutar(argv=[os.path.join(self.carpeta.name, 'no_existe.sql')])
        self.assertEqual(codigo, 2)
        self.assertIn('NO SE EJECUTA', salida)
