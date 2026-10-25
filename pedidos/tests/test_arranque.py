"""Arranque liviano: las bibliotecas pesadas no se importan al cargar las vistas (00-06)."""
import importlib
import sys

from django.test import TestCase


class CargaDiferidaWeasyprintTests(TestCase):
    def test_vistas_no_importan_weasyprint_al_cargar(self):
        import pedidos.views
        sys.modules.pop('weasyprint', None)
        importlib.reload(pedidos.views)
        self.assertNotIn('weasyprint', sys.modules)
