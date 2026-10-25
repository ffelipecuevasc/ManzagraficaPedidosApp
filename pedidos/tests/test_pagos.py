"""Pagos (00-06; 02-02 y 02-03 agregan la lógica de dinero y los flujos)."""
from django.test import TestCase

from .factorias import crear_usuario


class ListaPagosRutaTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_usuario('prueba'))

    def test_ruta_con_barra_responde(self):
        self.assertEqual(self.client.get('/pagos/lista/').status_code, 200)

    def test_ruta_sin_barra_redirige(self):
        respuesta = self.client.get('/pagos/lista')
        self.assertRedirects(respuesta, '/pagos/lista/', status_code=301, fetch_redirect_response=False)
