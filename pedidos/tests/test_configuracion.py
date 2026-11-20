"""Correcciones de configuración (04-05): lectura de settings, salud de la conexión y plantillas.

La configuración de producción depende de DATABASE_URL al importar `settings.py`, así que se
prueba en un proceso hijo con una URL de ejemplo, sin credenciales reales ni conexión.
"""
import json
import os
import subprocess
import sys

from django.conf import settings
from django.core.management.utils import get_random_secret_key
from django.test import SimpleTestCase

from pedidos import views

URL_DE_EJEMPLO = 'mysql://usuario:clave_de_ejemplo@127.0.0.1:3306/base_de_ejemplo'
CODIGO_HIJO = (
    # connections.settings completa los valores por defecto de Django (CONN_MAX_AGE=0, etc.).
    'import json, django; django.setup(); from django.conf import settings as s; '
    'from django.db import connections; d = connections.settings["default"]; '
    'print(json.dumps({"CONN_MAX_AGE": d.get("CONN_MAX_AGE"), '
    '"CONN_HEALTH_CHECKS": d.get("CONN_HEALTH_CHECKS"), "DIRS": [str(x) for x in s.TEMPLATES[0]["DIRS"]]}))'
)


def configuracion_de_base(**variables):
    entorno = os.environ.copy()
    entorno.pop('DATABASE_URL', None)
    entorno.update({
        'DJANGO_SETTINGS_MODULE': 'PedidosApp.settings',
        'SEGURIDAD_PRODUCCION': 'False',
        'ALLOWED_HOSTS': 'localhost,127.0.0.1',
        'SECRET_KEY': get_random_secret_key(),
    })
    entorno.update(variables)
    resultado = subprocess.run(
        [sys.executable, '-c', CODIGO_HIJO], cwd=settings.BASE_DIR, env=entorno,
        capture_output=True, text=True, encoding='utf-8', timeout=60,
    )
    if resultado.returncode != 0:
        raise AssertionError(f'La configuración no cargó: {resultado.stderr[-600:]}')
    return json.loads(resultado.stdout.strip().splitlines()[-1])


class LecturaDeConfiguracionTests(SimpleTestCase):
    def test_las_vistas_leen_la_configuracion_de_django(self):
        # AUD-01-009: nada de `from PedidosApp import settings`.
        self.assertIs(views.settings, settings)

    def test_dirs_de_plantillas_vacio_hasta_la_08_02(self):
        # AUD-02-016, D1: las plantillas viven en pedidos/templates (APP_DIRS).
        self.assertEqual(settings.TEMPLATES[0]['DIRS'], [])
        self.assertTrue(settings.TEMPLATES[0]['APP_DIRS'])


class SaludDeLaConexionTests(SimpleTestCase):
    def test_produccion_revisa_la_conexion_y_mantiene_60_segundos(self):
        # AUD-01-016, D3.
        valores = configuracion_de_base(DATABASE_URL=URL_DE_EJEMPLO)
        self.assertEqual(valores['CONN_MAX_AGE'], 60)
        self.assertIs(valores['CONN_HEALTH_CHECKS'], True)

    def test_local_no_cambia(self):
        valores = configuracion_de_base()
        self.assertEqual(valores['CONN_MAX_AGE'], 0)
        self.assertIs(valores['CONN_HEALTH_CHECKS'], False)
