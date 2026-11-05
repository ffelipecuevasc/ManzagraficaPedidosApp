"""Bloqueo del botón al enviar (iteración 03-04, decisión 8-C, DESIGN.md 5.1).

El comportamiento vive en JavaScript (`bloquearBoton` e `initBloqueoEnvio`, en `index.js`) y se revisa
a mano. Aquí se comprueba lo que sí se puede automatizar: que cada formulario de escritura lo declare
con `data-bloquear-envio`, que `pedido_form.html` conserve su propio script de la 00-07 (decisión 8-C:
no se toca lo que la medición del 2026-11-11 sigue vigilando) y que el JavaScript tenga las funciones.
"""
import re

from django.conf import settings
from django.test import TestCase

from . import factorias

FORMULARIO_BLOQUEADO = re.compile(r'<form[^>]*method="post"[^>]*data-bloquear-envio[^>]*>', re.S)
FORMULARIO_POST = re.compile(r'<form[^>]*method="post"[^>]*>', re.S)


class FormulariosDeEscrituraTests(TestCase):
    def setUp(self):
        self.client.force_login(factorias.crear_superusuario())

    def rutas(self):
        cliente = factorias.crear_cliente()
        cotizacion = factorias.crear_cotizacion()
        return {
            'cliente nuevo': '/clientes/nuevo/',
            'cliente editar': f'/clientes/editar/{cliente.pk}/',
            'producto nuevo': '/productos/nuevo/',
            'producto editar': f'/productos/editar/{factorias.crear_producto().pk}/',
            'cotización nueva': '/cotizaciones/nueva/',
            'cotización editar': f'/cotizaciones/editar/{cotizacion.pk}/',
            'conversión': f'/cotizaciones/convertir/{cotizacion.pk}/',
            'pago nuevo': '/pagos/ingresar/',
            'pago editar': f'/pagos/editar/{factorias.crear_pago().pk}/',
            'eliminar cliente': f'/clientes/eliminar/{factorias.crear_cliente().pk}/',
            'eliminar cotización': f'/cotizaciones/eliminar/{factorias.crear_cotizacion().pk}/',
            'eliminar pedido': f'/pedido/eliminar/{factorias.crear_pedido().pk}/',
            'eliminar producto': f'/productos/eliminar/{factorias.crear_producto().pk}/',
        }

    def test_cada_formulario_de_escritura_declara_el_bloqueo(self):
        for nombre, ruta in self.rutas().items():
            with self.subTest(nombre):
                respuesta = self.client.get(ruta)
                self.assertEqual(respuesta.status_code, 200)
                self.assertRegex(respuesta.content.decode(), FORMULARIO_BLOQUEADO)

    def test_pedido_conserva_su_script_de_la_00_07_y_no_usa_el_atributo(self):
        for ruta in ('/pedidos/nuevo/', f'/pedido/editar/{factorias.crear_pedido().pk}/'):
            with self.subTest(ruta):
                html = self.client.get(ruta).content.decode()
                self.assertIn('id="btn-confirmar-pedido"', html)
                self.assertIn("document.getElementById('btn-confirmar-pedido')", html)
                self.assertNotRegex(html, FORMULARIO_BLOQUEADO)

    def test_la_restauracion_bloquea_su_boton_despues_de_confirmar(self):
        html = self.client.get('/base_datos/restaurar_bd/').content.decode()

        self.assertIn("bloquearBoton(document.getElementById('btn-alerta-restaurar')", html)

    def test_el_javascript_define_el_bloqueo_y_lo_inicia(self):
        ruta = settings.BASE_DIR / 'pedidos' / 'static' / 'pedidos' / 'js' / 'index.js'
        codigo = ruta.read_text(encoding='utf-8')

        self.assertIn('function bloquearBoton(', codigo)
        self.assertIn('function desbloquearBoton(', codigo)
        self.assertIn('function initBloqueoEnvio(', codigo)
        self.assertRegex(codigo, r"initBloqueoEnvio\(\);")
        self.assertIn("form[data-bloquear-envio]", codigo)
        self.assertIn("'pageshow'", codigo)  # se recupera al volver con «atrás»
