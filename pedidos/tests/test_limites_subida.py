"""Límites de tamaño de las subidas (iteración 04-08, D5).

- La imagen de referencia se valida en `PedidoForm` con tope de 5 MB.
- El chequeo temprano de `CONTENT_LENGTH` rechaza el POST a `crear_pedido`, `editar_pedido` y
  `restaurar_bd` antes de que nadie lea el cuerpo: corre como middleware porque
  `CsrfViewMiddleware` lee `request.POST` antes de la vista (decisión del desarrollador, 2026-11-21).
- `DATA_UPLOAD_MAX_MEMORY_SIZE` no cuenta los archivos: un `.sql` de más de 2,5 MB llega a la vista.
"""
import io
from unittest import mock

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import QueryDict
from django.test import TestCase
from django.utils.datastructures import MultiValueDict
from PIL import Image

from pedidos.forms import PedidoForm
from pedidos.limite_acceso import TOPE_IMAGEN_BYTES
from pedidos.models import Pedido
from pedidos.utils import TOPE_VOLCADO_BYTES

from . import ayudas, factorias

DOS_MB_Y_MEDIO = 2_621_440
# Textos escritos por el agente en la 04-08 (no aprobados aún por el desarrollador).
TEXTO_IMAGEN_GRANDE = 'La imagen de referencia supera los 5 MB. Elige una imagen más liviana.'
TEXTO_CUERPO_GRANDE = 'El archivo supera el tamaño permitido y no se recibió. No se guardó nada.'


def png_de(tamano):
    """PNG válido de exactamente `tamano` bytes: una imagen mínima y relleno después de su fin."""
    salida = io.BytesIO()
    Image.new('RGB', (2, 2), 'white').save(salida, format='PNG')
    contenido = salida.getvalue()
    return SimpleUploadedFile('referencia.png', contenido + b'\0' * (tamano - len(contenido)),
                              content_type='image/png')


class ValoresExplicitosTests(TestCase):
    def test_los_dos_limites_de_django_valen_2_5_mb(self):
        self.assertEqual(settings.DATA_UPLOAD_MAX_MEMORY_SIZE, DOS_MB_Y_MEDIO)
        self.assertEqual(settings.FILE_UPLOAD_MAX_MEMORY_SIZE, DOS_MB_Y_MEDIO)


class ImagenReferenciaTests(TestCase):
    def setUp(self):
        self.cliente = factorias.crear_cliente()
        self.producto = factorias.crear_producto()

    def datos(self):
        return {'cliente': self.cliente.pk, 'resumen_pedido': 'Con imagen', 'valor_venta': 11_900,
                'abono_inicial': 0, 'items_json': ayudas.items_json((self.producto, '1', 11_900))}

    def test_imagen_del_tope_exacto_pasa(self):
        form = PedidoForm(self.datos(), {'imagen_referencia': png_de(TOPE_IMAGEN_BYTES)})
        form.is_valid()
        self.assertNotIn('imagen_referencia', form.errors)

    def test_un_byte_mas_se_rechaza_con_el_mensaje(self):
        form = PedidoForm(self.datos(), {'imagen_referencia': png_de(TOPE_IMAGEN_BYTES + 1)})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['imagen_referencia'], [TEXTO_IMAGEN_GRANDE])

    def test_la_vista_no_guarda_el_pedido_con_imagen_grande(self):
        self.client.force_login(factorias.crear_usuario())
        ruta = '/pedidos/nuevo/'
        datos = ayudas.con_token(self.client, ruta, {**self.datos(),
                                                     'imagen_referencia': png_de(TOPE_IMAGEN_BYTES + 1)})
        respuesta = self.client.post(ruta, datos)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, TEXTO_IMAGEN_GRANDE)
        self.assertFalse(Pedido.objects.exists())


class ChequeoTempranoTests(TestCase):
    def setUp(self):
        self.client.force_login(factorias.crear_superusuario())

    def post_declarando(self, ruta, declarado):
        vacio = (QueryDict(mutable=True), MultiValueDict())
        with mock.patch('django.http.multipartparser.MultiPartParser.parse', return_value=vacio) as leer:
            respuesta = self.client.post(ruta, {'campo': 'x'}, CONTENT_LENGTH=str(declarado))
        return respuesta, leer

    def assertRechazadoSinLeer(self, ruta, declarado, destino):
        respuesta, leer = self.post_declarando(ruta, declarado)
        leer.assert_not_called()
        self.assertRedirects(respuesta, destino, fetch_redirect_response=False)
        mensajes = [str(m) for m in respuesta.wsgi_request._messages]
        self.assertEqual(mensajes, [TEXTO_CUERPO_GRANDE])
        self.assertNotIn('Traceback', respuesta.content.decode())

    def test_crear_pedido_rechaza_un_cuerpo_mayor_que_imagen_mas_formulario(self):
        tope = TOPE_IMAGEN_BYTES + DOS_MB_Y_MEDIO
        self.assertRechazadoSinLeer('/pedidos/nuevo/', tope + 1, '/pedidos/nuevo/')

    def test_editar_pedido_rechaza_un_cuerpo_grande(self):
        pedido = factorias.crear_pedido()
        ruta = f'/pedido/editar/{pedido.pk}/'
        self.assertRechazadoSinLeer(ruta, TOPE_IMAGEN_BYTES + DOS_MB_Y_MEDIO + 1, ruta)

    def test_restaurar_rechaza_mas_de_20_mb_mas_1_mb(self):
        ruta = '/base_datos/restaurar_bd/'
        self.assertRechazadoSinLeer(ruta, TOPE_VOLCADO_BYTES + 1024 * 1024 + 1, ruta)

    def test_justo_en_el_tope_no_lo_rechaza_el_chequeo(self):
        respuesta, leer = self.post_declarando('/base_datos/restaurar_bd/', TOPE_VOLCADO_BYTES + 1024 * 1024)
        leer.assert_called()

    def test_otras_rutas_no_se_revisan(self):
        respuesta, leer = self.post_declarando('/clientes/nuevo/', 50 * 1024 * 1024)
        leer.assert_called()


class SqlNoLoFrenaDjangoTests(TestCase):
    def test_un_sql_de_3_mb_llega_a_la_vista(self):
        self.client.force_login(factorias.crear_superusuario())
        archivo = ayudas.volcado_subido(contenido=ayudas.VOLCADO_VALIDO + b'-- relleno\n' * 300_000)
        self.assertGreater(archivo.size, DOS_MB_Y_MEDIO)
        respuesta = self.client.post('/base_datos/restaurar_bd/',
                                     ayudas.datos_restaurar(archivo, confirmacion='no'), follow=True)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Para restaurar, escribe RESTAURAR')
