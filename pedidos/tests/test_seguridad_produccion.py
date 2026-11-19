"""Configuración de producción: cookies seguras, HTTPS, HSTS y arranque que falla (04-02).

La configuración se lee al importar `settings.py`, así que cada combinación de variables se
prueba en un proceso hijo. Las variables del hijo ganan al `.env` local porque `load_dotenv`
no pisa las que ya existen. La suite corre con `SEGURIDAD_PRODUCCION` apagada.
"""
import json
import os
import subprocess
import sys

from django.conf import settings
from django.core.management.utils import get_random_secret_key
from django.test import SimpleTestCase, override_settings

DOMINIO_PRODUCCION = 'manzagrafica.pythonanywhere.com'
NOMBRES = [
    'SEGURIDAD_PRODUCCION', 'SESSION_COOKIE_SECURE', 'CSRF_COOKIE_SECURE',
    'SECURE_SSL_REDIRECT', 'SECURE_HSTS_SECONDS', 'SECURE_HSTS_INCLUDE_SUBDOMAINS',
    'SECURE_HSTS_PRELOAD', 'CSRF_TRUSTED_ORIGINS',
]
CODIGO_HIJO = (
    # Se lee a través de django.conf para obtener también los valores por defecto de Django.
    'import json; from django.conf import settings as s; s.INSTALLED_APPS; '
    f'print(json.dumps({{n: getattr(s, n, None) for n in {NOMBRES!r}}}))'
)


def cargar_configuracion(**variables):
    """Importa la configuración en un proceso hijo con esas variables de entorno."""
    entorno = os.environ.copy()
    entorno.pop('CSRF_TRUSTED_ORIGINS', None)
    entorno.update({
        'DJANGO_SETTINGS_MODULE': 'PedidosApp.settings',
        'SEGURIDAD_PRODUCCION': 'False',
        'ALLOWED_HOSTS': 'localhost,127.0.0.1',
        # Clave válida para la regla de la 04-03 (D2): estas pruebas no dependen de la del .env local.
        'SECRET_KEY': get_random_secret_key(),
    })
    entorno.update(variables)
    return subprocess.run(
        [sys.executable, '-c', CODIGO_HIJO], cwd=settings.BASE_DIR, env=entorno,
        capture_output=True, text=True, encoding='utf-8', timeout=60,
    )


def valores(**variables):
    resultado = cargar_configuracion(**variables)
    if resultado.returncode != 0:
        raise AssertionError(f'La configuración no cargó: {resultado.stderr[-600:]}')
    return json.loads(resultado.stdout.strip().splitlines()[-1])


class ArranqueInseguroTests(SimpleTestCase):
    """D5: con el dominio de producción y la variable apagada, Django no arranca."""

    def test_dominio_de_produccion_sin_la_variable_no_arranca(self):
        resultado = cargar_configuracion(ALLOWED_HOSTS=DOMINIO_PRODUCCION)
        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn('ImproperlyConfigured', resultado.stderr)
        self.assertIn('SEGURIDAD_PRODUCCION', resultado.stderr)

    def test_dominio_de_produccion_con_la_variable_arranca(self):
        datos = valores(ALLOWED_HOSTS=DOMINIO_PRODUCCION, SEGURIDAD_PRODUCCION='True')
        self.assertTrue(datos['SEGURIDAD_PRODUCCION'])

    def test_valores_locales_sin_la_variable_arrancan(self):
        datos = valores()
        self.assertFalse(datos['SEGURIDAD_PRODUCCION'])


class ValoresPorEntornoTests(SimpleTestCase):
    """D3, D1 y D4: qué activa la variable y de dónde salen los orígenes de confianza."""

    def test_con_la_variable_activa(self):
        datos = valores(SEGURIDAD_PRODUCCION='True')
        self.assertTrue(datos['SESSION_COOKIE_SECURE'])
        self.assertTrue(datos['CSRF_COOKIE_SECURE'])
        self.assertTrue(datos['SECURE_SSL_REDIRECT'])
        # Escalón 2 de HSTS (D1): una semana, sin subdominios ni preload.
        self.assertEqual(datos['SECURE_HSTS_SECONDS'], 604800)
        self.assertFalse(datos['SECURE_HSTS_INCLUDE_SUBDOMAINS'])
        self.assertFalse(datos['SECURE_HSTS_PRELOAD'])

    def test_con_la_variable_apagada(self):
        datos = valores()
        self.assertFalse(datos['SESSION_COOKIE_SECURE'])
        self.assertFalse(datos['CSRF_COOKIE_SECURE'])
        self.assertFalse(datos['SECURE_SSL_REDIRECT'])
        self.assertEqual(datos['SECURE_HSTS_SECONDS'], 0)

    def test_variable_que_no_es_true_queda_apagada(self):
        self.assertFalse(valores(SEGURIDAD_PRODUCCION='1')['SECURE_SSL_REDIRECT'])

    def test_origenes_de_confianza_locales_por_defecto(self):
        self.assertEqual(
            valores()['CSRF_TRUSTED_ORIGINS'],
            ['http://localhost:8000', 'http://127.0.0.1:8000'],
        )

    def test_origenes_de_confianza_desde_el_entorno(self):
        datos = valores(CSRF_TRUSTED_ORIGINS=f' https://{DOMINIO_PRODUCCION} ,')
        self.assertEqual(datos['CSRF_TRUSTED_ORIGINS'], [f'https://{DOMINIO_PRODUCCION}'])

    def test_la_suite_corre_con_la_variable_apagada(self):
        self.assertFalse(settings.SEGURIDAD_PRODUCCION)
        self.assertFalse(settings.SECURE_SSL_REDIRECT)


class RedireccionHttpsTests(SimpleTestCase):
    """D2: con los valores que entrega la variable activa, HTTP redirige y HTTPS lleva HSTS."""

    def setUp(self):
        datos = valores(SEGURIDAD_PRODUCCION='True')
        seguridad = {n: datos[n] for n in NOMBRES if n.startswith('SECURE_')}
        sobrescribir = override_settings(**seguridad)
        sobrescribir.enable()
        self.addCleanup(sobrescribir.disable)

    def test_peticion_http_redirige_con_301_a_https(self):
        respuesta = self.client.get('/accounts/login/')
        self.assertEqual(respuesta.status_code, 301)
        self.assertEqual(respuesta['Location'], 'https://testserver/accounts/login/')

    def test_peticion_https_no_redirige_y_lleva_hsts(self):
        respuesta = self.client.get('/accounts/login/', secure=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta['Strict-Transport-Security'], 'max-age=604800')
