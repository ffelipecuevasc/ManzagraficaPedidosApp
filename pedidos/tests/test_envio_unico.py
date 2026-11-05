"""Envío único: token en la sesión (iteración 03-04, AUD-04-001, decisiones 5-A, 6-A y 7-A).

Un formulario de creación (pedido, cotización o pago) trae un token. Un envío repetido con el mismo
token no crea un segundo registro y termina donde terminó el primero; un envío sin token válido no
crea nada y devuelve el formulario con lo escrito y un token nuevo. R21 vive en `test_regresiones.py`.
"""
import json
from unittest import mock

from django.test import TestCase, override_settings

from pedidos import envio_unico, views
from pedidos.models import Cotizacion, ItemPedido, Pago, Pedido

from . import ayudas, factorias


class EnvioBase(TestCase):
    def setUp(self):
        self.client.force_login(factorias.crear_usuario())
        self.cliente = factorias.crear_cliente()
        self.producto = factorias.crear_producto(valor_neto=10_000)
        self.pedido = factorias.crear_pedido(valor_venta=10_000)

    def items(self):
        return ayudas.items_json((self.producto, '2', 4_000))

    def datos_pedido(self, **campos):
        datos = {'cliente': self.cliente.pk, 'resumen_pedido': 'Envío único', 'valor_venta': 8_000,
                 'abono_inicial': 0, 'items_json': self.items()}
        datos.update(campos)
        return datos

    def datos_cotizacion(self, **campos):
        datos = {'cliente': self.cliente.pk, 'resumen': 'Envío único', 'detalles': 'd', 'valor_total': 8_000,
                 'validez': 15, 'fecha_emision': '2026-10-15', 'items_json': self.items()}
        datos.update(campos)
        return datos

    def datos_pago(self, **campos):
        datos = {'pedido': self.pedido.pk, 'monto': 3_000, 'metodo': 'EFECTIVO', 'nota': ''}
        datos.update(campos)
        return datos


class TokenEnLosFormulariosTests(EnvioBase):
    def test_los_formularios_de_creacion_traen_un_token_distinto_cada_vez(self):
        for ruta in ('/pedidos/nuevo/', '/cotizaciones/nueva/', '/pagos/ingresar/', f'/pagos/ingresar/{self.pedido.pk}/'):
            with self.subTest(ruta):
                primero = ayudas.token_de(self.client.get(ruta))
                segundo = ayudas.token_de(self.client.get(ruta))
                self.assertTrue(primero)
                self.assertNotEqual(primero, segundo)

    def test_los_formularios_de_edicion_no_llevan_token(self):
        pago = factorias.crear_pago(self.pedido)
        cotizacion = factorias.crear_cotizacion()
        rutas = (f'/pedido/editar/{self.pedido.pk}/', f'/cotizaciones/editar/{cotizacion.pk}/',
                 f'/pagos/editar/{pago.pk}/')
        for ruta in rutas:
            with self.subTest(ruta):
                self.assertEqual(ayudas.token_de(self.client.get(ruta)), '')


class EnvioRepetidoTests(EnvioBase):
    """Decisión 6-A: el envío repetido termina donde terminó el primero, sin mensaje."""

    def test_pedido_repetido_crea_uno_solo_y_redirige_al_ya_creado(self):
        datos = self.datos_pedido(token_envio=ayudas.token_de(self.client.get('/pedidos/nuevo/')))

        primero = self.client.post('/pedidos/nuevo/', datos)
        segundo = self.client.post('/pedidos/nuevo/', datos)

        creado = Pedido.objects.exclude(pk=self.pedido.pk).get()
        self.assertRedirects(primero, f'/{creado.pk}/', fetch_redirect_response=False)
        self.assertRedirects(segundo, f'/{creado.pk}/', fetch_redirect_response=False)
        self.assertEqual(ItemPedido.objects.filter(pedido=creado).count(), 1)

    def test_cotizacion_repetida_crea_una_sola(self):
        datos = self.datos_cotizacion(token_envio=ayudas.token_de(self.client.get('/cotizaciones/nueva/')))

        primero = self.client.post('/cotizaciones/nueva/', datos)
        segundo = self.client.post('/cotizaciones/nueva/', datos)

        creada = Cotizacion.objects.get()
        self.assertEqual(primero.url, segundo.url)
        self.assertEqual(primero.url, f'/cotizaciones/detalle/{creada.pk}/')

    def test_pago_repetido_crea_uno_solo(self):
        ruta = f'/pagos/ingresar/{self.pedido.pk}/'
        datos = self.datos_pago(token_envio=ayudas.token_de(self.client.get(ruta)))

        primero = self.client.post(ruta, datos)
        segundo = self.client.post(ruta, datos)

        self.assertEqual(Pago.objects.count(), 1)
        self.assertEqual(primero.url, segundo.url)

    def test_el_envio_repetido_no_agrega_mensajes(self):
        datos = self.datos_pedido(token_envio=ayudas.token_de(self.client.get('/pedidos/nuevo/')))
        self.client.post('/pedidos/nuevo/', datos)

        segundo = self.client.post('/pedidos/nuevo/', datos, follow=True)

        self.assertNotContains(segundo, 'role="alert"')
        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 1)

    def test_dos_formularios_abiertos_a_la_vez_crean_dos_pedidos(self):
        token_a = ayudas.token_de(self.client.get('/pedidos/nuevo/'))
        token_b = ayudas.token_de(self.client.get('/pedidos/nuevo/'))
        self.assertTrue(token_a and token_b and token_a != token_b)

        self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=token_a))
        self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=token_b))

        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 2)

    def test_un_formulario_nuevo_despues_de_guardar_puede_guardar_otro(self):
        primero = ayudas.token_de(self.client.get('/pedidos/nuevo/'))
        self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=primero))

        segundo = ayudas.token_de(self.client.get('/pedidos/nuevo/'))
        self.assertTrue(primero and segundo and primero != segundo)
        self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=segundo))

        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 2)


class EnvioSinTokenValidoTests(EnvioBase):
    """Decisión 7-A: no crea nada y devuelve el formulario con lo escrito y un token nuevo."""

    def assertRechazado(self, respuesta, plantilla, token_anterior):
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, plantilla)
        self.assertContains(respuesta, ayudas.TEXTO_FORMULARIO_VENCIDO)
        self.assertContains(respuesta, 'role="alert"')
        nuevo = ayudas.token_de(respuesta)
        self.assertTrue(nuevo)
        self.assertNotEqual(nuevo, token_anterior)

    def test_pedido_sin_token_no_crea_nada_y_conserva_lo_escrito(self):
        respuesta = self.client.post('/pedidos/nuevo/', self.datos_pedido(resumen_pedido='Lo que escribí'))

        self.assertRechazado(respuesta, 'pedidos/pedido_form.html', '')
        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 0)
        self.assertContains(respuesta, 'Lo que escribí')
        self.assertEqual(respuesta.context['items_json'], self.items())

    def test_el_rechazo_deja_una_linea_info_sin_el_contenido_del_formulario(self):
        with self.assertLogs('pedidos.views', 'INFO') as capturado:
            self.client.post('/pedidos/nuevo/', self.datos_pedido(resumen_pedido='texto-del-usuario-456'))

        self.assertEqual(len(capturado.records), 1)
        registro = capturado.records[0]
        self.assertIn('Envío sin token válido', registro.getMessage())
        self.assertEqual(registro.request.path, '/pedidos/nuevo/')
        self.assertNotIn('texto-del-usuario-456', registro.getMessage())

    def test_el_token_del_formulario_devuelto_sirve_para_guardar(self):
        rechazado = self.client.post('/pedidos/nuevo/', self.datos_pedido())

        self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=ayudas.token_de(rechazado)))

        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 1)

    def test_token_inventado_o_vacio_se_rechaza(self):
        for token in ('', 'inventado', 'x' * 32):
            with self.subTest(token=token):
                respuesta = self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=token))
                self.assertRechazado(respuesta, 'pedidos/pedido_form.html', token)
        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 0)

    def test_token_de_otro_formulario_se_rechaza(self):
        token_de_cotizacion = ayudas.token_de(self.client.get('/cotizaciones/nueva/'))

        respuesta = self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=token_de_cotizacion))

        self.assertRechazado(respuesta, 'pedidos/pedido_form.html', token_de_cotizacion)
        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 0)

    def test_token_de_otra_sesion_se_rechaza(self):
        token_ajeno = ayudas.token_de(self.client.get('/pedidos/nuevo/'))
        self.client.logout()
        self.client.force_login(factorias.crear_usuario())

        respuesta = self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=token_ajeno))

        self.assertRechazado(respuesta, 'pedidos/pedido_form.html', token_ajeno)

    def test_cotizacion_y_pago_sin_token_tambien_se_rechazan(self):
        cotizacion = self.client.post('/cotizaciones/nueva/', self.datos_cotizacion())
        pago = self.client.post(f'/pagos/ingresar/{self.pedido.pk}/', self.datos_pago())

        self.assertRechazado(cotizacion, 'pedidos/cotizacion_form.html', '')
        self.assertRechazado(pago, 'pedidos/pago_form.html', '')
        self.assertEqual((Cotizacion.objects.count(), Pago.objects.count()), (0, 0))

    def test_el_pago_rechazado_conserva_el_pedido_y_el_monto(self):
        respuesta = self.client.post(f'/pagos/ingresar/{self.pedido.pk}/', self.datos_pago(monto=3_333))

        self.assertContains(respuesta, '3333')

    def test_pasado_el_tope_el_token_mas_antiguo_deja_de_valer(self):
        primero = ayudas.token_de(self.client.get('/pedidos/nuevo/'))
        for _ in range(envio_unico.TOPE):
            self.client.get('/pedidos/nuevo/')

        respuesta = self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=primero))

        self.assertRechazado(respuesta, 'pedidos/pedido_form.html', primero)


class TokenNoSeGastaSiNoSeGuardaTests(EnvioBase):
    def test_formulario_invalido_conserva_el_mismo_token(self):
        token = ayudas.token_de(self.client.get('/pedidos/nuevo/'))
        self.assertTrue(token)

        with self.assertLogs('pedidos.views', 'INFO'):
            invalido = self.client.post('/pedidos/nuevo/', self.datos_pedido(resumen_pedido='', token_envio=token))

        self.assertEqual(ayudas.token_de(invalido), token)
        self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=token))
        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 1)

    def test_item_fallido_conserva_el_mismo_token(self):
        token = ayudas.token_de(self.client.get('/pedidos/nuevo/'))
        self.assertTrue(token)
        malos = json.dumps([{'producto_id': '999999', 'cantidad': '1', 'precio_unitario': 1}])

        with self.assertLogs('pedidos.views', 'ERROR'):
            fallido = self.client.post('/pedidos/nuevo/', self.datos_pedido(items_json=malos, token_envio=token))

        self.assertEqual(ayudas.token_de(fallido), token)
        self.client.post('/pedidos/nuevo/', self.datos_pedido(token_envio=token))
        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 1)

    @override_settings(DEBUG=False)
    def test_un_error_del_sistema_no_gasta_el_token(self):
        # El SessionMiddleware no guarda la sesión en una respuesta 5xx (verificado en Django 6.0.1).
        self.client.raise_request_exception = False
        token = ayudas.token_de(self.client.get('/pedidos/nuevo/'))
        self.assertTrue(token)
        datos = self.datos_pedido(token_envio=token)

        with mock.patch.object(views, 'registrar_evento', side_effect=RuntimeError('falla de prueba')), \
                self.assertLogs('django.request', 'ERROR'):
            roto = self.client.post('/pedidos/nuevo/', datos)
        self.assertEqual(roto.status_code, 500)
        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 0)

        self.client.post('/pedidos/nuevo/', datos)
        self.assertEqual(Pedido.objects.exclude(pk=self.pedido.pk).count(), 1)
