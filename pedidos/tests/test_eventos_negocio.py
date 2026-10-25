"""Instrumentación de eventos de negocio: una prueba por evento del inventario (01-04).

TestCase envuelve cada prueba en una transacción que nunca se confirma, así que los
`on_commit` se ejecutan con `captureOnCommitCallbacks(execute=True)`.
"""
import os
import tempfile
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from pedidos import views
from pedidos.models import Pago, Pedido, RegistroEvento

from . import factorias


class EventosNegocioBase(TestCase):
    def setUp(self):
        self.usuario = factorias.crear_superusuario()
        self.client.force_login(self.usuario)  # sin ejecutar on_commit: no deja evento

    def ejecutar(self, metodo, ruta, datos=None, **extra):
        with self.captureOnCommitCallbacks(execute=True):
            return getattr(self.client, metodo)(ruta, datos or {}, **extra)

    def assertUnEvento(self, tipo, entidad, entidad_id, usuario='actual'):
        eventos = list(RegistroEvento.objects.all())
        self.assertEqual(len(eventos), 1, [e.tipo for e in eventos])
        evento = eventos[0]
        esperado = self.usuario if usuario == 'actual' else usuario
        self.assertEqual((evento.tipo, evento.usuario, evento.entidad, evento.entidad_id),
                         (tipo, esperado, entidad, entidad_id))
        return evento


class EventosPedidoTests(EventosNegocioBase):
    def test_pedido_creado_con_abono_deja_un_solo_evento(self):
        cliente = factorias.crear_cliente()
        respuesta = self.ejecutar('post', '/pedidos/nuevo/', {
            'cliente': cliente.pk, 'resumen_pedido': 'Pedido de prueba', 'valor_venta': 20_000,
            'abono_inicial': 5_000, 'metodo_pago': 'EFECTIVO',
        })
        self.assertEqual(respuesta.status_code, 302)
        pedido = Pedido.objects.get()
        self.assertEqual(Pago.objects.count(), 1)
        evento = self.assertUnEvento('pedido_creado', 'pedido', pedido.pk)
        self.assertEqual(evento.resumen, f'Pedido #{pedido.pk} creado con abono inicial')

    def test_pedido_modificado(self):
        pedido = factorias.crear_pedido()
        self.ejecutar('post', f'/pedido/editar/{pedido.pk}/', {
            'cliente': pedido.cliente.pk, 'resumen_pedido': 'Resumen nuevo', 'valor_venta': 1_000,
        })
        self.assertUnEvento('pedido_modificado', 'pedido', pedido.pk)

    def test_pedido_eliminado(self):
        pedido = factorias.crear_pedido()
        self.ejecutar('post', f'/pedido/eliminar/{pedido.pk}/')
        self.assertFalse(Pedido.objects.exists())
        self.assertUnEvento('pedido_eliminado', 'pedido', pedido.pk)

    def test_pedido_estado_cambiado_por_get(self):
        # La ruta escribe con GET (se corrige en 04-01); el evento se registra igual.
        pedido = factorias.crear_pedido()
        self.ejecutar('get', f'/pedido/{pedido.pk}/cambiar/EN_PROCESO/')
        evento = self.assertUnEvento('pedido_estado_cambiado', 'pedido', pedido.pk)
        self.assertEqual(evento.resumen, f'Pedido #{pedido.pk}: PENDIENTE -> EN_PROCESO')

    def test_estado_igual_o_invalido_no_deja_evento(self):
        pedido = factorias.crear_pedido()
        self.ejecutar('get', f'/pedido/{pedido.pk}/cambiar/PENDIENTE/')
        self.ejecutar('get', f'/pedido/{pedido.pk}/cambiar/INVENTADO/')
        self.assertFalse(RegistroEvento.objects.exists())

    def test_pedido_duplicado(self):
        original = factorias.crear_pedido()
        self.ejecutar('get', f'/pedido/duplicar/{original.pk}/')
        nuevo = Pedido.objects.exclude(pk=original.pk).get()
        evento = self.assertUnEvento('pedido_duplicado', 'pedido', nuevo.pk)
        self.assertIn(f'#{original.pk}', evento.resumen)


class EventosPagoTests(EventosNegocioBase):
    def test_pago_registrado(self):
        pedido = factorias.crear_pedido(valor_venta=10_000)
        self.ejecutar('post', '/pagos/ingresar/', {'pedido': pedido.pk, 'monto': 4_000, 'metodo': 'EFECTIVO'})
        pago = Pago.objects.get()
        evento = self.assertUnEvento('pago_registrado', 'pago', pago.pk)
        self.assertNotIn('4000', evento.resumen.replace('.', ''))  # sin montos en el resumen

    def test_pago_modificado(self):
        pago = factorias.crear_pago()
        self.ejecutar('post', f'/pagos/editar/{pago.pk}/', {'pedido': pago.pedido.pk, 'monto': 6_000, 'metodo': 'DEBITO'})
        self.assertUnEvento('pago_modificado', 'pago', pago.pk)

    def test_pago_eliminado(self):
        pago = factorias.crear_pago()
        self.ejecutar('post', f'/pagos/eliminar/{pago.pk}/')
        self.assertFalse(Pago.objects.exists())
        self.assertUnEvento('pago_eliminado', 'pago', pago.pk)


class EventosCotizacionClienteProductoTests(EventosNegocioBase):
    def test_cotizacion_convertida_deja_un_solo_evento(self):
        cotizacion = factorias.crear_cotizacion(items=[{}], valor_total=10_000)
        self.ejecutar('post', f'/cotizaciones/convertir/{cotizacion.pk}/', {
            'fecha_entrega': '2026-11-02', 'valor_abonado': 2_000, 'metodo_pago': 'EFECTIVO',
        })
        pedido = Pedido.objects.get()
        evento = self.assertUnEvento('cotizacion_convertida', 'cotizacion', cotizacion.pk)
        self.assertEqual(evento.resumen, f'Cotización #{cotizacion.pk} convertida en el pedido #{pedido.pk}')

    def test_cliente_eliminado(self):
        cliente = factorias.crear_cliente()
        self.ejecutar('post', f'/clientes/eliminar/{cliente.pk}/')
        self.assertUnEvento('cliente_eliminado', 'cliente', cliente.pk)

    def test_producto_eliminado(self):
        producto = factorias.crear_producto()
        self.ejecutar('post', f'/productos/eliminar/{producto.pk}/')
        self.assertUnEvento('producto_eliminado', 'producto', producto.pk)

    def test_producto_protegido_no_deja_evento(self):
        producto = factorias.crear_producto()
        factorias.crear_pedido(items=[{'producto': producto}])
        respuesta = self.ejecutar('post', f'/productos/eliminar/{producto.pk}/')
        self.assertEqual(respuesta.status_code, 200)  # muestra el aviso de que no se puede borrar
        self.assertFalse(RegistroEvento.objects.exists())


class EventosBaseDeDatosTests(EventosNegocioBase):
    def test_respaldo_generado_con_su_usuario(self):
        # No se llama a respuesta.close(): dispararía request_finished y cerraría la conexión
        # en medio de la transacción de la prueba. El archivo queda abierto hasta el final.
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as carpeta:
            ruta = os.path.join(carpeta, 'respaldo_prueba.sql')
            with open(ruta, 'w', encoding='utf-8') as archivo:
                archivo.write('-- volcado ficticio\n')
            with mock.patch.object(views, 'generar_respaldo_mysql', return_value=ruta):
                respuesta = self.ejecutar('get', '/base_datos/respaldar_bd/accion/')
            self.assertEqual(respuesta.status_code, 200)
        evento = self.assertUnEvento('respaldo_generado', 'respaldo', None)
        self.assertEqual(evento.resumen, 'Respaldo respaldo_prueba.sql generado')

    def test_restauracion_simulada_con_su_usuario(self):
        # Sin ejecutar mysql: se simulan el respaldo previo y la restauración.
        with tempfile.TemporaryDirectory() as carpeta, \
                mock.patch.object(views.settings, 'BASE_DIR', carpeta), \
                mock.patch.object(views, 'generar_respaldo_mysql') as respaldo, \
                mock.patch.object(views, 'restaurar_bd_mysql') as restaurar:
            archivo = SimpleUploadedFile('ficticio.sql', b'-- volcado ficticio\n')
            self.ejecutar('post', '/base_datos/restaurar_bd/', {'archivo_sql': archivo})
        respaldo.assert_called_once()
        restaurar.assert_called_once()
        self.assertUnEvento('restauracion_ejecutada', 'base_de_datos', None)

    def test_restauracion_fallida_no_deja_evento(self):
        with tempfile.TemporaryDirectory() as carpeta, \
                mock.patch.object(views.settings, 'BASE_DIR', carpeta), \
                mock.patch.object(views, 'generar_respaldo_mysql'), \
                mock.patch.object(views, 'restaurar_bd_mysql', side_effect=RuntimeError('mysql falló')):
            archivo = SimpleUploadedFile('ficticio.sql', b'-- volcado ficticio\n')
            self.ejecutar('post', '/base_datos/restaurar_bd/', {'archivo_sql': archivo})
        self.assertFalse(RegistroEvento.objects.exists())


class EventosAccesoTests(TestCase):
    def ejecutar_post(self, datos):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post('/accounts/login/', datos)

    def test_acceso_exitoso(self):
        usuario = factorias.crear_usuario('recepcion', password='clave-correcta-123')
        respuesta = self.ejecutar_post({'username': 'recepcion', 'password': 'clave-correcta-123'})
        self.assertEqual(respuesta.status_code, 302)
        evento = RegistroEvento.objects.get()
        self.assertEqual((evento.tipo, evento.usuario, evento.entidad, evento.entidad_id),
                         ('acceso_exitoso', usuario, 'usuario', usuario.pk))

    def assertAccesoFallido(self, resumen_esperado):
        evento = RegistroEvento.objects.get()
        self.assertEqual((evento.tipo, evento.usuario, evento.entidad, evento.entidad_id),
                         ('acceso_fallido', None, 'usuario', None))
        self.assertEqual(evento.resumen, resumen_esperado)
        return evento

    def test_acceso_fallido_usuario_existente_guarda_el_nombre_sin_la_contrasena(self):
        factorias.crear_usuario('recepcion', password='clave-correcta-123')
        respuesta = self.ejecutar_post({'username': 'recepcion', 'password': 'clave-equivocada-999'})
        self.assertEqual(respuesta.status_code, 200)
        evento = self.assertAccesoFallido('Usuario intentado: recepcion')
        self.assertNotIn('clave-equivocada-999', evento.resumen)

    def test_acceso_fallido_usuario_inexistente_no_guarda_lo_escrito(self):
        factorias.crear_usuario('recepcion', password='clave-correcta-123')
        self.ejecutar_post({'username': 'nombre-que-no-existe', 'password': 'otra-clave-456'})
        evento = self.assertAccesoFallido('Usuario intentado: usuario desconocido')
        self.assertNotIn('nombre-que-no-existe', evento.resumen)
        self.assertNotIn('otra-clave-456', evento.resumen)

    def test_acceso_fallido_contrasena_escrita_en_el_campo_usuario_no_queda(self):
        factorias.crear_usuario('recepcion', password='Clave#Secreta2026!')
        # Error típico: la contraseña se escribe en el campo de usuario.
        self.ejecutar_post({'username': 'Clave#Secreta2026!', 'password': ''})
        self.ejecutar_post({'username': 'Clave#Secreta2026!', 'password': 'x'})
        resumenes = list(RegistroEvento.objects.values_list('resumen', flat=True))
        self.assertTrue(resumenes)
        for resumen in resumenes:
            self.assertEqual(resumen, 'Usuario intentado: usuario desconocido')
            self.assertNotIn('Clave#Secreta2026!', resumen)


class LecturasSinEventosTests(EventosNegocioBase):
    def test_listados_detalles_y_estadisticas_no_crean_eventos(self):
        pedido = factorias.crear_pedido(items=[{}])
        pago = factorias.crear_pago(pedido)
        cotizacion = factorias.crear_cotizacion(items=[{}])
        producto = factorias.crear_producto()
        rutas = [
            '/', '/pedidos/lista/', f'/{pedido.pk}/', '/pedidos/trabajo-semanal/',
            '/pedidos/estadisticas/', '/clientes/lista/', '/cotizaciones/lista/',
            f'/cotizaciones/detalle/{cotizacion.pk}/', '/productos/lista/', f'/productos/{producto.pk}/',
            '/pagos/lista/', f'/pagos/detalle/{pago.pk}/', '/pagos/estadisticas/',
            '/base_datos/respaldar_bd/', '/base_datos/estadisticas_bd/',
        ]
        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.ejecutar('get', ruta)
                self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(RegistroEvento.objects.exists())
