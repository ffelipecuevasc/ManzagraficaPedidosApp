"""Política de seguridad de contenido en observación (04-09).

La aplicación envía `Content-Security-Policy-Report-Only` con la política final (solo `'self'`,
D1): el navegador anota cada recurso externo y cada pieza en línea, pero no bloquea nada.
`SECURE_CSP`, el modo que bloquea, sigue vacío hasta la Épica 08 (08-08).

El interruptor `CSP_OBSERVACION` (D3) se lee al importar `settings.py`, así que cada valor se
prueba en un proceso hijo, como en `test_seguridad_produccion.py`. Solo el texto exacto
`False` apaga la observación; cualquier otro valor la deja activa y nunca detiene el arranque.
Las pruebas que usan el cliente suponen que el `.env` local no define `CSP_OBSERVACION=False`
(la observación va activa también en local, D3).
"""
import json
import os
import subprocess
import sys

from django.conf import settings
from django.core.management.utils import get_random_secret_key
from django.test import SimpleTestCase, TestCase, override_settings

from .factorias import crear_superusuario

CABECERA_OBSERVACION = 'Content-Security-Policy-Report-Only'
CABECERA_BLOQUEO = 'Content-Security-Policy'
MIDDLEWARE_CSP = 'django.middleware.csp.ContentSecurityPolicyMiddleware'
MIDDLEWARE_SEGURIDAD = 'django.middleware.security.SecurityMiddleware'

# Política D1: la que se querrá al final, sin servidores externos.
POLITICA_ESPERADA = {
    'default-src': ["'self'"],
    'script-src': ["'self'"],
    'style-src': ["'self'"],
    'img-src': ["'self'", 'data:'],
    'font-src': ["'self'"],
    'connect-src': ["'self'"],
    'object-src': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"],
}
SERVIDORES_EXTERNOS = (
    'fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.tailwindcss.com',
    'cdn.jsdelivr.net', 'code.jquery.com',
)

CODIGO_HIJO = (
    'import json; from django.conf import settings as s; s.INSTALLED_APPS; '
    'print(json.dumps({"CSP_OBSERVACION": s.CSP_OBSERVACION, '
    '"SECURE_CSP_REPORT_ONLY": s.SECURE_CSP_REPORT_ONLY, "SECURE_CSP": s.SECURE_CSP}))'
)


def directivas(valor):
    """Convierte el texto de la cabecera en {directiva: [valores]}."""
    resultado = {}
    for parte in valor.split(';'):
        piezas = parte.split()
        if piezas:
            resultado[piezas[0]] = piezas[1:]
    return resultado


def cargar_configuracion(**variables):
    """Importa la configuración en un proceso hijo con esas variables de entorno."""
    entorno = os.environ.copy()
    entorno.update({
        'DJANGO_SETTINGS_MODULE': 'PedidosApp.settings',
        'SEGURIDAD_PRODUCCION': 'False',
        'ALLOWED_HOSTS': 'localhost,127.0.0.1',
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


class CabeceraPresenteTests(TestCase):
    """La cabecera de observación llega en páginas públicas, autenticadas y de error."""

    def setUp(self):
        self.usuario = crear_superusuario()

    def comprobar(self, respuesta):
        self.assertIn(CABECERA_OBSERVACION, respuesta.headers)
        self.assertEqual(directivas(respuesta.headers[CABECERA_OBSERVACION]), POLITICA_ESPERADA)
        # Nunca bloquea: no hay cabecera de bloqueo.
        self.assertNotIn(CABECERA_BLOQUEO, respuesta.headers)

    def test_acceso_publico(self):
        respuesta = self.client.get('/accounts/login/')
        self.assertEqual(respuesta.status_code, 200)
        self.comprobar(respuesta)

    def test_panel_autenticado(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get('/')
        self.assertEqual(respuesta.status_code, 200)
        self.comprobar(respuesta)

    def test_pagina_404(self):
        self.client.force_login(self.usuario)
        respuesta = self.client.get('/ruta-que-no-existe-0409/')
        self.assertEqual(respuesta.status_code, 404)
        self.comprobar(respuesta)

    def test_admin(self):
        respuesta = self.client.get('/acceso-manzagrafica-admin/login/')
        self.assertEqual(respuesta.status_code, 200)
        self.comprobar(respuesta)


class NuncaBloqueaTests(SimpleTestCase):
    """Nada se aplica hasta la Épica 08: el modo que bloquea queda vacío."""

    def test_secure_csp_vacio(self):
        self.assertEqual(settings.SECURE_CSP, {})

    def test_observacion_activa_por_defecto_en_la_suite(self):
        self.assertTrue(settings.CSP_OBSERVACION)
        self.assertEqual(settings.SECURE_CSP_REPORT_ONLY, POLITICA_ESPERADA)


class SinReporteExternoTests(SimpleTestCase):
    """Sin punto de recepción (D4) y sin servidores externos en la política (D1)."""

    def test_sin_report_uri_ni_report_to(self):
        self.assertNotIn('report-uri', settings.SECURE_CSP_REPORT_ONLY)
        self.assertNotIn('report-to', settings.SECURE_CSP_REPORT_ONLY)

    def test_sin_servidores_externos(self):
        texto = json.dumps(settings.SECURE_CSP_REPORT_ONLY)
        self.assertNotIn('http', texto)
        for servidor in SERVIDORES_EXTERNOS:
            self.assertNotIn(servidor, texto)


class SinDuplicadosTests(TestCase):
    """No repite lo que ya cubren la 04-02 y X-Frame-Options."""

    def test_sin_upgrade_ni_frame_ancestors(self):
        self.assertNotIn('upgrade-insecure-requests', settings.SECURE_CSP_REPORT_ONLY)
        self.assertNotIn('frame-ancestors', settings.SECURE_CSP_REPORT_ONLY)

    def test_x_frame_options_sigue_en_deny(self):
        respuesta = self.client.get('/accounts/login/')
        self.assertEqual(respuesta.headers.get('X-Frame-Options'), 'DENY')


class OrdenMiddlewareTests(SimpleTestCase):
    """El middleware está una sola vez, justo después de SecurityMiddleware."""

    def test_una_vez_y_despues_de_security(self):
        self.assertEqual(settings.MIDDLEWARE.count(MIDDLEWARE_CSP), 1)
        posicion = settings.MIDDLEWARE.index(MIDDLEWARE_CSP)
        self.assertEqual(settings.MIDDLEWARE[posicion - 1], MIDDLEWARE_SEGURIDAD)


class InterruptorTests(SimpleTestCase):
    """D3 y C2: solo el texto exacto «False» apaga; nada detiene el arranque."""

    def test_false_apaga(self):
        datos = valores(CSP_OBSERVACION='False')
        self.assertFalse(datos['CSP_OBSERVACION'])
        self.assertEqual(datos['SECURE_CSP_REPORT_ONLY'], {})
        self.assertEqual(datos['SECURE_CSP'], {})

    def test_true_y_vacia_dejan_activa(self):
        # Vacía equivale a sin definir: load_dotenv no pisa una variable ya presente.
        for valor in ('True', ''):
            with self.subTest(valor=valor):
                datos = valores(CSP_OBSERVACION=valor)
                self.assertTrue(datos['CSP_OBSERVACION'])
                self.assertEqual(datos['SECURE_CSP_REPORT_ONLY'], POLITICA_ESPERADA)

    def test_otros_valores_dejan_activa_y_arrancan(self):
        for valor in ('false', '0', 'no', 'FALSE', ' False'):
            with self.subTest(valor=valor):
                resultado = cargar_configuracion(CSP_OBSERVACION=valor)
                self.assertEqual(resultado.returncode, 0, resultado.stderr[-600:])
                self.assertNotIn('ImproperlyConfigured', resultado.stderr)
                datos = json.loads(resultado.stdout.strip().splitlines()[-1])
                self.assertTrue(datos['CSP_OBSERVACION'])
                self.assertEqual(datos['SECURE_CSP_REPORT_ONLY'], POLITICA_ESPERADA)
                self.assertEqual(datos['SECURE_CSP'], {})


@override_settings(SECURE_CSP_REPORT_ONLY={})
class ApagadoEnRespuestaTests(TestCase):
    """Con la política vacía (lo que deja CSP_OBSERVACION=False) no sale ninguna cabecera."""

    def test_sin_cabeceras(self):
        respuesta = self.client.get('/accounts/login/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn(CABECERA_OBSERVACION, respuesta.headers)
        self.assertNotIn(CABECERA_BLOQUEO, respuesta.headers)
