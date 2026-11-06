"""Contrato de error hacia el usuario (iteración 03-04, RDA-013 y RDA-019).

Las pruebas de la 01-09 leen la cola de mensajes (`get_messages`): miden lo que la vista encoló,
no lo que el usuario ve. Estas **renderizan** la pantalla de destino y comprueban el HTML.
"""
import html
import json
import os
import re
import tempfile
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from pedidos import views

from . import ayudas, factorias

TEXTO_TECNICO = 'detalle-tecnico /ruta/secreta mysqldump: error 1045'
BASE_EXITO = 'Base de Datos Restaurada Exitosamente'


class MensajesBase(TestCase):
    def setUp(self):
        self.usuario = factorias.crear_superusuario()
        self.client.force_login(self.usuario)


class MensajesDeErrorSeVenTests(MensajesBase):
    """Decisiones 1 y 2 (A): un bloque común en base.html pinta los de error."""

    def test_el_error_del_respaldo_se_ve_en_la_pantalla_de_respaldos(self):
        with mock.patch.object(views, 'generar_respaldo_mysql', side_effect=RuntimeError(TEXTO_TECNICO)), \
                self.assertLogs('pedidos.views', 'ERROR'):
            respuesta = self.client.get('/base_datos/respaldar_bd/accion/', follow=True)

        self.assertContains(respuesta, 'No se pudo generar el respaldo. El detalle quedó en el registro del servidor.')
        self.assertContains(respuesta, 'role="alert"')
        self.assertNotContains(respuesta, 'secreta')
        self.assertNotContains(respuesta, 'mysqldump')

    def test_los_errores_de_la_restauracion_se_ven(self):
        sin_archivo = self.client.post('/base_datos/restaurar_bd/', {}, follow=True)
        self.assertContains(sin_archivo, 'No se seleccionó ningún archivo.')

        mala_extension = self.client.post(
            '/base_datos/restaurar_bd/', {'archivo_sql': SimpleUploadedFile('datos.txt', b'x')}, follow=True)
        self.assertContains(mala_extension, 'El archivo debe tener extensión .sql')

    def test_el_error_de_la_restauracion_fallida_se_ve_sin_detalles_tecnicos(self):
        archivo = SimpleUploadedFile('ficticio.sql', b'-- volcado ficticio\n')
        with tempfile.TemporaryDirectory() as carpeta, \
                mock.patch.object(views.settings, 'BASE_DIR', carpeta), \
                mock.patch.object(views, 'generar_respaldo_mysql', return_value=os.path.join(carpeta, 'respaldo_x.sql')), \
                mock.patch.object(views, 'restaurar_bd_mysql', side_effect=RuntimeError(TEXTO_TECNICO)), \
                self.assertLogs('pedidos.views', 'ERROR'):
            respuesta = self.client.post('/base_datos/restaurar_bd/', {'archivo_sql': archivo}, follow=True)

        self.assertContains(respuesta, 'La restauración falló.')
        self.assertNotContains(respuesta, 'secreta')
        self.assertNotContains(respuesta, 'mysqldump')
        self.assertNotContains(respuesta, 'backups/')  # decisión 9-A

    def test_la_restauracion_exitosa_dibuja_su_tarjeta_una_sola_vez(self):
        archivo = SimpleUploadedFile('ficticio.sql', b'-- volcado ficticio\n')
        with tempfile.TemporaryDirectory() as carpeta, \
                mock.patch.object(views.settings, 'BASE_DIR', carpeta), \
                mock.patch.object(views, 'generar_respaldo_mysql', return_value=os.path.join(carpeta, 'respaldo_x.sql')), \
                mock.patch.object(views, 'restaurar_bd_mysql'):
            respuesta = self.client.post('/base_datos/restaurar_bd/', {'archivo_sql': archivo}, follow=True)

        self.assertContains(respuesta, BASE_EXITO, count=1)


class AvisosQueNoSonDeErrorTests(MensajesBase):
    """Decisión 2 (A): se consumen sin mostrarse y no se acumulan hacia la restauración."""

    def registrar_pago(self):
        pedido = factorias.crear_pedido(valor_venta=10_000)
        datos = ayudas.con_token(self.client, '/pagos/ingresar/', {
            'pedido': pedido.pk, 'monto': 4_000, 'metodo': 'EFECTIVO', 'nota': ''})
        return self.client.post('/pagos/ingresar/', datos, follow=True), pedido

    def test_la_confirmacion_del_pago_no_se_muestra(self):
        respuesta, _ = self.registrar_pago()

        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, 'registrado correctamente')

    def test_un_pago_registrado_no_aparece_como_restauracion_exitosa(self):
        self.registrar_pago()

        respuesta = self.client.get('/base_datos/restaurar_bd/')

        self.assertNotContains(respuesta, BASE_EXITO)

    def test_ni_la_edicion_ni_la_eliminacion_de_un_pago_se_acumulan(self):
        _, pedido = self.registrar_pago()
        pago = pedido.pagos.get()
        self.client.post(f'/pagos/editar/{pago.pk}/', {
            'pedido': pedido.pk, 'monto': 5_000, 'metodo': 'EFECTIVO', 'nota': ''}, follow=True)
        self.client.post(f'/pagos/eliminar/{pago.pk}/', follow=True)

        respuesta = self.client.get('/base_datos/restaurar_bd/')

        self.assertNotContains(respuesta, BASE_EXITO)


# ---------------------------------------------------------------------------
# Decisión 4-A · Un error de validación devuelve el formulario con lo que escribió el usuario
# ---------------------------------------------------------------------------
ITEMS_DEL_USUARIO = '[{"producto_id":"1","nombre":"Lienzo <b>grande</b>","cantidad":3,"precio_unitario":4000}]'


class FormulariosConservanLoEscritoTests(TestCase):
    def setUp(self):
        self.client.force_login(factorias.crear_usuario())
        self.cliente = factorias.crear_cliente()

    def assertConservaItems(self, respuesta, plantilla, items_json=ITEMS_DEL_USUARIO):
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, plantilla)
        self.assertEqual(respuesta.context['items_json'], items_json)
        self.assertContains(respuesta, html.escape(items_json))
        self.assertNotContains(respuesta, '<b>grande</b>')  # el autoescape protege el HTML

    def test_crear_pedido_invalido_devuelve_items_y_metodo_de_pago(self):
        with self.assertLogs('pedidos.views', 'INFO'):
            respuesta = self.client.post('/pedidos/nuevo/', ayudas.con_token(self.client, '/pedidos/nuevo/', {
                'cliente': self.cliente.pk, 'resumen_pedido': '', 'valor_venta': 12_000,
                'abono_inicial': 4_000, 'metodo_pago': 'TRANSFERENCIA', 'items_json': ITEMS_DEL_USUARIO}))

        self.assertConservaItems(respuesta, 'pedidos/pedido_form.html')
        self.assertContains(respuesta, '<option value="TRANSFERENCIA" selected>Transferencia</option>', html=True)
        self.assertContains(respuesta, 'Crear Pedido')
        self.assertNotContains(respuesta, ayudas.TEXTO_IMAGEN)

    def assertConservaElAbono(self, respuesta, abono='5000', metodo='TRANSFERENCIA'):
        """El abono vuelve escrito en su campo y el método de pago vuelve habilitado y marcado.

        Un `<select>` deshabilitado no se envía: sin abono reescrito, el método se perdía y el pedido
        podía guardarse sin su pago inicial (hallazgo 1 de la revisión de servidor de la 03-04).
        """
        contenido = respuesta.content.decode()
        campo_abono = re.search(r'<input[^>]*name="abono_inicial"[^>]*>', contenido, re.S)
        select_metodo = re.search(r'<select[^>]*name="metodo_pago"[^>]*>', contenido, re.S)
        self.assertIsNotNone(campo_abono, 'no está el campo del abono')
        self.assertIsNotNone(select_metodo, 'no está el método de pago')
        self.assertRegex(campo_abono.group(0), rf'value="{abono}"')
        self.assertNotRegex(select_metodo.group(0), r'\bdisabled\b')
        self.assertContains(respuesta, f'<option value="{metodo}" selected>', html=False)
        self.assertNotRegex(contenido, r'id="container-metodo"[^>]*opacity-50')

    def test_crear_pedido_invalido_devuelve_el_abono_y_deja_habilitado_el_metodo_de_pago(self):
        with self.assertLogs('pedidos.views', 'INFO'):
            respuesta = self.client.post('/pedidos/nuevo/', ayudas.con_token(self.client, '/pedidos/nuevo/', {
                'cliente': self.cliente.pk, 'resumen_pedido': '', 'valor_venta': 12_000,
                'abono_inicial': 5_000, 'metodo_pago': 'TRANSFERENCIA', 'items_json': ITEMS_DEL_USUARIO}))

        self.assertEqual(respuesta.status_code, 200)
        self.assertConservaElAbono(respuesta)

    def test_crear_pedido_con_item_fallido_devuelve_el_abono_y_deja_habilitado_el_metodo_de_pago(self):
        item_inexistente = '[{"producto_id":"999999","cantidad":"1","precio_unitario":1000}]'

        with self.assertLogs('pedidos.views', 'ERROR'):
            respuesta = self.client.post('/pedidos/nuevo/', ayudas.con_token(self.client, '/pedidos/nuevo/', {
                'cliente': self.cliente.pk, 'resumen_pedido': 'Con ítem fallido', 'valor_venta': 12_000,
                'abono_inicial': 5_000, 'metodo_pago': 'TRANSFERENCIA', 'items_json': item_inexistente}))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, ayudas.TEXTO_ITEM_FALLIDO)
        self.assertConservaElAbono(respuesta)

    def test_crear_pedido_vencido_devuelve_el_abono_y_deja_habilitado_el_metodo_de_pago(self):
        with self.assertLogs('pedidos.views', 'INFO'):
            respuesta = self.client.post('/pedidos/nuevo/', {
                'cliente': self.cliente.pk, 'resumen_pedido': 'Vencido', 'valor_venta': 12_000,
                'abono_inicial': 5_000, 'metodo_pago': 'TRANSFERENCIA', 'items_json': ITEMS_DEL_USUARIO,
                'token_envio': ''})

        self.assertContains(respuesta, ayudas.TEXTO_FORMULARIO_VENCIDO)
        self.assertConservaElAbono(respuesta)

    def test_crear_pedido_sin_abono_deja_deshabilitado_el_metodo_de_pago(self):
        """Sin abono mayor que 0 el método sigue deshabilitado, como antes: no cambia el formulario nuevo."""
        for etiqueta, respuesta in (
                ('GET', self.client.get('/pedidos/nuevo/')),
                ('error sin abono', self.client.post('/pedidos/nuevo/', ayudas.con_token(
                    self.client, '/pedidos/nuevo/', {
                        'cliente': self.cliente.pk, 'resumen_pedido': '', 'valor_venta': 1, 'abono_inicial': ''}))),
                ('error con abono 0', self.client.post('/pedidos/nuevo/', ayudas.con_token(
                    self.client, '/pedidos/nuevo/', {
                        'cliente': self.cliente.pk, 'resumen_pedido': '', 'valor_venta': 1, 'abono_inicial': '0'}))),
        ):
            with self.subTest(etiqueta):
                contenido = respuesta.content.decode()
                self.assertRegex(re.search(r'<select[^>]*name="metodo_pago"[^>]*>', contenido, re.S).group(0),
                                 r'\bdisabled\b')
                self.assertNotRegex(re.search(r'<input[^>]*name="abono_inicial"[^>]*>', contenido, re.S).group(0),
                                    r'value=')

    def test_crear_pedido_sin_pasar_por_el_formulario_no_marca_ningun_metodo(self):
        respuesta = self.client.get('/pedidos/nuevo/')

        self.assertNotContains(respuesta, 'selected>Efectivo')
        self.assertEqual(respuesta.context.get('items_json', ''), '')

    def test_editar_pedido_invalido_devuelve_los_items_del_usuario_y_no_los_de_la_base(self):
        pedido = factorias.crear_pedido(valor_venta=10_000, items=[{'producto': factorias.crear_producto()}])

        respuesta = self.client.post(f'/pedido/editar/{pedido.pk}/', {
            'cliente': pedido.cliente.pk, 'resumen_pedido': '', 'valor_venta': 12_000,
            'items_json': ITEMS_DEL_USUARIO})

        self.assertConservaItems(respuesta, 'pedidos/pedido_form.html')
        self.assertEqual(pedido.items.count(), 1)

    def test_editar_pedido_invalido_sin_items_en_el_envio_muestra_los_de_la_base(self):
        pedido = factorias.crear_pedido(valor_venta=10_000, items=[{'producto': factorias.crear_producto()}])

        respuesta = self.client.post(f'/pedido/editar/{pedido.pk}/', {
            'cliente': pedido.cliente.pk, 'resumen_pedido': '', 'valor_venta': 12_000, 'items_json': ''})

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(json.loads(respuesta.context['items_json'])), 1)

    def test_crear_cotizacion_invalida_devuelve_los_items(self):
        respuesta = self.client.post('/cotizaciones/nueva/', ayudas.con_token(self.client, '/cotizaciones/nueva/', {
            'cliente': self.cliente.pk, 'resumen': '', 'detalles': 'd', 'valor_total': 12_000,
            'validez': 15, 'fecha_emision': '2026-10-15', 'items_json': ITEMS_DEL_USUARIO}))

        self.assertConservaItems(respuesta, 'pedidos/cotizacion_form.html')
        self.assertContains(respuesta, 'Crear Cotización')

    def test_editar_cotizacion_invalida_devuelve_los_items_del_usuario(self):
        cotizacion = factorias.crear_cotizacion(valor_total=10_000)

        respuesta = self.client.post(f'/cotizaciones/editar/{cotizacion.pk}/', {
            'cliente': cotizacion.cliente.pk, 'resumen': '', 'detalles': 'd', 'valor_total': 12_000,
            'validez': 15, 'fecha_emision': '2026-10-15', 'items_json': ITEMS_DEL_USUARIO})

        self.assertConservaItems(respuesta, 'pedidos/cotizacion_form.html')

    def test_el_aviso_de_la_imagen_solo_sale_si_el_formulario_traia_una(self):
        datos = {'cliente': self.cliente.pk, 'resumen_pedido': '', 'valor_venta': 12_000}

        sin_imagen = self.client.post('/pedidos/nuevo/', ayudas.con_token(self.client, '/pedidos/nuevo/', datos))
        con_imagen = self.client.post('/pedidos/nuevo/', ayudas.con_token(self.client, '/pedidos/nuevo/', {
            **datos, 'imagen_referencia': SimpleUploadedFile('ref.png', b'no-es-una-imagen')}))

        self.assertNotContains(sin_imagen, ayudas.TEXTO_IMAGEN)
        self.assertContains(con_imagen, ayudas.TEXTO_IMAGEN)
        self.assertContains(con_imagen, 'role="alert"')


# ---------------------------------------------------------------------------
# Paso 7 · Errores junto al campo accesibles (AGENTS.md 8.17, DESIGN.md 8)
# ---------------------------------------------------------------------------
class ErroresAccesiblesTests(TestCase):
    """Los errores de las plantillas tocadas usan text-red-600, role="alert", aria-invalid y
    aria-describedby, y el aviso general no se anima (patrón de la conversión de la 03-03)."""

    def setUp(self):
        self.client.force_login(factorias.crear_usuario())
        self.cliente = factorias.crear_cliente()

    def invalidas(self):
        pedido = factorias.crear_pedido()
        casos = {
            'pedido': ('/pedidos/nuevo/', {'cliente': self.cliente.pk, 'resumen_pedido': '', 'valor_venta': 1},
                       'resumen_pedido'),
            'cotización': ('/cotizaciones/nueva/', {'cliente': self.cliente.pk, 'resumen': '', 'detalles': 'd',
                                                    'valor_total': 1, 'validez': 15, 'fecha_emision': '2026-10-15'},
                           'resumen'),
            'pago': ('/pagos/ingresar/', {'pedido': pedido.pk, 'monto': -5, 'metodo': 'EFECTIVO'}, 'monto'),
            'cliente': ('/clientes/nuevo/', {'nombre': '', 'telefono': ''}, 'nombre'),
            'producto': ('/productos/nuevo/', {'nombre': '', 'unidad': 'UNITARIO', 'valor_neto': 1}, 'nombre'),
        }
        return casos

    def test_el_campo_con_error_queda_enlazado_a_su_mensaje(self):
        for nombre, (ruta, datos, campo) in self.invalidas().items():
            with self.subTest(nombre):
                with self.assertLogs('pedidos.views', 'INFO') if nombre == 'pedido' else mock.MagicMock():
                    respuesta = self.client.post(ruta, ayudas.con_token(self.client, ruta, datos))
                html_respuesta = respuesta.content.decode()

                self.assertEqual(respuesta.status_code, 200)
                self.assertIn(f'id="error-{campo}"', html_respuesta)
                self.assertRegex(html_respuesta, rf'id="error-{campo}"[^>]*role="alert"')
                self.assertIn(f'aria-describedby="error-{campo}"', html_respuesta)
                self.assertIn('aria-invalid="true"', html_respuesta)

    def test_ni_el_aviso_ni_los_errores_usan_pulso_ni_rojo_500_como_texto(self):
        for nombre, (ruta, datos, _) in self.invalidas().items():
            with self.subTest(nombre):
                with self.assertLogs('pedidos.views', 'INFO') if nombre == 'pedido' else mock.MagicMock():
                    html_respuesta = self.client.post(
                        ruta, ayudas.con_token(self.client, ruta, datos)).content.decode()

                self.assertNotIn('animate-pulse', html_respuesta)
                self.assertNotRegex(html_respuesta, r'(?<![\w:-])text-red-500')

    def test_un_formulario_sin_errores_no_marca_ningun_campo(self):
        html_respuesta = self.client.get('/pedidos/nuevo/').content.decode()

        self.assertNotIn('aria-invalid="true"', html_respuesta)
