"""Credenciales y secretos (04-03): contraseña fuera de los argumentos y clave secreta obligatoria.

D1: `mysqldump` y `mysql` reciben la contraseña en un archivo temporal de opciones que se
borra siempre. Se reemplaza `subprocess.run` donde lo busca `utils.py`: nunca se ejecuta el
cliente de MySQL en la prueba. Ninguna prueba imprime ni compara contra la contraseña real:
se usa una contraseña de prueba con `override_settings`.

D2: la configuración se lee al importar `settings.py`, así que cada caso corre en un proceso
hijo, como en `test_seguridad_produccion.py`.
"""
import os
import subprocess
import sys
import tempfile
from unittest import mock

from django.conf import settings
from django.core.management.utils import get_random_secret_key
from django.test import SimpleTestCase, override_settings

from pedidos import utils

CLAVE_DE_PRUEBA = 'clave-de-prueba-"con\\comillas'
BASE_DE_PRUEBA = {
    'default': {
        **settings.DATABASES['default'],
        'NAME': 'base_de_prueba', 'USER': 'usuario_de_prueba',
        'PASSWORD': CLAVE_DE_PRUEBA, 'HOST': '127.0.0.1',
    }
}


@override_settings(DATABASES=BASE_DE_PRUEBA)
class ArchivoDeOpcionesTests(SimpleTestCase):
    """D1: sin contraseña en los argumentos y sin archivo de opciones huérfano."""

    databases = set()

    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(self.carpeta.cleanup)
        parche = mock.patch.object(utils.settings, 'BASE_DIR', self.carpeta.name)
        parche.start()
        self.addCleanup(parche.stop)
        self.sql = os.path.join(self.carpeta.name, 'entrada.sql')
        with open(self.sql, 'w', encoding='utf-8') as f:
            f.write('SELECT 1;\n')
        self.llamadas = []

    def espia(self, efecto=None):
        """Reemplazo de subprocess.run que anota los argumentos y el archivo de opciones."""
        def ejecutar(argumentos, **opciones):
            ruta = argumentos[1].split('=', 1)[1] if len(argumentos) > 1 else ''
            existe = os.path.exists(ruta)
            contenido = ''
            if existe:
                with open(ruta, encoding='utf-8') as f:
                    contenido = f.read()
            self.llamadas.append({'argumentos': list(argumentos), 'ruta': ruta,
                                  'existe': existe, 'contenido': contenido})
            if efecto:
                raise efecto
            return subprocess.CompletedProcess(argumentos, 0, b'', b'')
        return mock.patch.object(utils.subprocess, 'run', side_effect=ejecutar)

    def respaldar(self):
        return utils.generar_respaldo_mysql()

    def restaurar(self):
        return utils.restaurar_bd_mysql(self.sql)

    def revisar_llamada(self, programa):
        self.assertEqual(len(self.llamadas), 1)
        llamada = self.llamadas[0]
        argumentos = llamada['argumentos']
        self.assertEqual(argumentos[0], programa)
        self.assertTrue(argumentos[1].startswith('--defaults-extra-file='))
        texto = ' '.join(argumentos)
        self.assertNotIn(CLAVE_DE_PRUEBA, texto)
        self.assertNotIn('--password', texto)
        self.assertNotIn('-p', [a[:2] for a in argumentos if not a.startswith('--')])
        self.assertTrue(llamada['existe'], 'el archivo de opciones debe existir durante la llamada')
        self.assertIn('[client]', llamada['contenido'])
        self.assertIn('password=', llamada['contenido'])
        self.assertFalse(os.path.exists(llamada['ruta']), 'el archivo de opciones debe borrarse')
        # Fuera de backups/: nunca se descarga ni se lista junto a los respaldos.
        self.assertNotIn(os.path.join(self.carpeta.name, 'backups'), llamada['ruta'])

    def test_respaldo_sin_contrasena_en_argumentos(self):
        with self.espia():
            ruta = self.respaldar()
        self.revisar_llamada('mysqldump')
        self.assertTrue(ruta.endswith('.sql'))
        self.assertIn('--no-tablespaces', self.llamadas[0]['argumentos'])
        self.assertEqual(self.llamadas[0]['argumentos'][-1], 'base_de_prueba')

    def test_restauracion_sin_contrasena_en_argumentos(self):
        with self.espia():
            self.assertTrue(self.restaurar())
        self.revisar_llamada('mysql')
        self.assertEqual(self.llamadas[0]['argumentos'][-1], 'base_de_prueba')

    def test_contrasena_con_comillas_y_barras_queda_escapada(self):
        with self.espia():
            self.respaldar()
        self.assertIn('password="clave-de-prueba-\\"con\\\\comillas"', self.llamadas[0]['contenido'])

    def test_respaldo_fallido_borra_el_archivo_de_opciones(self):
        error = subprocess.CalledProcessError(2, 'mysqldump', stderr=b'acceso denegado')
        with self.espia(error), self.assertRaises(Exception):
            self.respaldar()
        self.assertTrue(self.llamadas[0]['existe'])
        self.assertFalse(os.path.exists(self.llamadas[0]['ruta']))

    def test_respaldo_sin_ejecutable_borra_el_archivo_de_opciones(self):
        with self.espia(FileNotFoundError('mysqldump')), self.assertRaises(Exception):
            self.respaldar()
        self.assertFalse(os.path.exists(self.llamadas[0]['ruta']))

    def test_restauracion_fallida_borra_el_archivo_de_opciones(self):
        error = subprocess.CalledProcessError(1, 'mysql')
        with self.espia(error), self.assertRaises(Exception):
            self.restaurar()
        self.assertFalse(os.path.exists(self.llamadas[0]['ruta']))

    def test_restauracion_sin_ejecutable_borra_el_archivo_de_opciones(self):
        with self.espia(FileNotFoundError('mysql')), self.assertRaises(Exception):
            self.restaurar()
        self.assertFalse(os.path.exists(self.llamadas[0]['ruta']))

    def test_el_error_del_respaldo_no_trae_la_contrasena(self):
        error = subprocess.CalledProcessError(2, 'mysqldump', stderr=b'acceso denegado')
        with self.espia(error), self.assertRaises(Exception) as captura:
            self.respaldar()
        self.assertNotIn(CLAVE_DE_PRUEBA, str(captura.exception))


CODIGO_HIJO = 'from django.conf import settings as s; s.INSTALLED_APPS; print(len(s.SECRET_KEY))'


def cargar_con_clave(clave, **variables):
    """Importa la configuración en un proceso hijo con esa SECRET_KEY (vacía = ausente)."""
    entorno = os.environ.copy()
    entorno.update({
        'DJANGO_SETTINGS_MODULE': 'PedidosApp.settings',
        'SEGURIDAD_PRODUCCION': 'False',
        'ALLOWED_HOSTS': 'localhost,127.0.0.1',
        # load_dotenv no pisa una variable que ya existe, aunque esté vacía.
        'SECRET_KEY': clave,
        # El mensaje lleva tildes: en Windows el hijo escribiría en cp1252 y no se leería.
        'PYTHONIOENCODING': 'utf-8',
    })
    entorno.update(variables)
    return subprocess.run(
        [sys.executable, '-c', CODIGO_HIJO], cwd=settings.BASE_DIR, env=entorno,
        capture_output=True, text=True, encoding='utf-8', timeout=60,
    )


class ClaveSecretaTests(SimpleTestCase):
    """D2: sin clave no arranca nunca; en producción, tampoco con una clave débil (como W009)."""

    def assertNoArranca(self, resultado, clave):
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn('ImproperlyConfigured', resultado.stderr)
        self.assertIn('SECRET_KEY', resultado.stderr)
        if clave:
            self.assertNotIn(clave, resultado.stderr, 'el mensaje nunca muestra la clave')

    def assertArranca(self, resultado):
        self.assertEqual(resultado.returncode, 0, resultado.stderr[-600:])

    def test_sin_clave_no_arranca_en_local(self):
        resultado = cargar_con_clave('')
        self.assertNoArranca(resultado, '')
        # El mensaje propio, no el genérico de Django al primer uso de la clave.
        self.assertIn('SECRET_KEY no está definida', resultado.stderr)

    def test_sin_clave_no_arranca_en_produccion(self):
        self.assertNoArranca(cargar_con_clave('', SEGURIDAD_PRODUCCION='True'), '')

    def test_clave_insegura_no_arranca_en_produccion(self):
        clave = 'django-insecure-' + get_random_secret_key()
        self.assertNoArranca(cargar_con_clave(clave, SEGURIDAD_PRODUCCION='True'), clave)

    def test_clave_corta_no_arranca_en_produccion(self):
        clave = get_random_secret_key()[:49]
        self.assertNoArranca(cargar_con_clave(clave, SEGURIDAD_PRODUCCION='True'), clave)

    def test_clave_con_pocos_caracteres_distintos_no_arranca_en_produccion(self):
        clave = 'abcd' * 20
        self.assertNoArranca(cargar_con_clave(clave, SEGURIDAD_PRODUCCION='True'), clave)

    def test_clave_valida_de_50_arranca_en_produccion(self):
        self.assertArranca(cargar_con_clave(get_random_secret_key()[:50], SEGURIDAD_PRODUCCION='True'))

    def test_clave_debil_arranca_en_local(self):
        # En local y en las pruebas solo se exige que exista (D2).
        self.assertArranca(cargar_con_clave('django-insecure-corta'))
