import sys

from django.contrib.auth import get_user_model
from django.test import TestCase


class RobotsTxtTests(TestCase):
    def test_responde_sin_sesion_en_texto_plano(self):
        respuesta = self.client.get('/robots.txt')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta['Content-Type'].startswith('text/plain'))
        self.assertIn('Disallow: /', respuesta.content.decode())

    def test_acepta_head(self):
        respuesta = self.client.head('/robots.txt')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta['Content-Type'].startswith('text/plain'))

    def test_rechaza_post(self):
        self.assertEqual(self.client.post('/robots.txt').status_code, 405)


class ListaPagosRutaTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user('prueba', password='clave-prueba-123')
        self.client.force_login(usuario)

    def test_ruta_con_barra_responde(self):
        self.assertEqual(self.client.get('/pagos/lista/').status_code, 200)

    def test_ruta_sin_barra_redirige(self):
        respuesta = self.client.get('/pagos/lista')
        self.assertRedirects(respuesta, '/pagos/lista/', status_code=301, fetch_redirect_response=False)


class CargaDiferidaWeasyprintTests(TestCase):
    def test_vistas_no_importan_weasyprint_al_cargar(self):
        import importlib
        import pedidos.views
        sys.modules.pop('weasyprint', None)
        importlib.reload(pedidos.views)
        self.assertNotIn('weasyprint', sys.modules)
