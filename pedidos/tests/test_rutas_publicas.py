"""Rutas que responden sin sesión (00-06)."""
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
