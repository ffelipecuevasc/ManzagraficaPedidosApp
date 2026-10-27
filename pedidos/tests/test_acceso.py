"""Control de acceso: pruebas de caracterización (iteración 02-05).

Fijan quién entra adónde HOY. Mecanismo encontrado: no hay `LoginRequiredMiddleware`; cada
vista lleva `@login_required` y las cuatro de la base de datos, además,
`@user_passes_test(es_superusuario)`. Una vista nueva sin decorador queda pública: la prueba
de inventario lo detecta.

Si una ruta resulta pública sin querer, la prueba NO se cambia para que pase: se registra
el hallazgo y una regresión en la 02-04 (decisión D2 del desarrollador, 2026-10-27).

Ninguna prueba ejecuta mysql ni mysqldump ni escribe en backups/ o media/ reales:
`generar_respaldo_mysql` y `restaurar_bd_mysql` se reemplazan donde las busca la vista, y
`BASE_DIR` apunta a una carpeta temporal.
"""
import os
import tempfile
from contextlib import contextmanager
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import URLPattern, reverse

from pedidos import urls as rutas_pedidos
from pedidos import views
from pedidos.models import (
    Cliente, Cotizacion, HistorialBD, ItemCotizacion, ItemPedido, Pago, Pedido, Producto,
    RegistroEvento,
)

from . import ayudas
from .factorias import (
    crear_cliente, crear_cotizacion, crear_pago, crear_pedido, crear_producto,
    crear_superusuario, crear_usuario,
)

LOGIN = '/accounts/login/'

# Decisión D1 del desarrollador (2026-10-27): las únicas rutas públicas de pedidos/urls.py.
# El acceso (`login`) vive en django.contrib.auth.urls y se prueba aparte.
RUTAS_PUBLICAS = {'robots_txt'}

# Argumentos ficticios para construir cada ruta con `reverse`.
ARGUMENTOS = {'pk': 1, 'pedido_id': 1, 'nuevo_estado': 'PENDIENTE'}

PK_INEXISTENTE = 999_999

MODELOS = (Cliente, Pedido, ItemPedido, Pago, Producto, Cotizacion, ItemCotizacion,
           HistorialBD, RegistroEvento)


def conteos():
    return {modelo.__name__: modelo.objects.count() for modelo in MODELOS}


def rutas_de_pedidos():
    """(nombre, ruta) de cada patrón de pedidos/urls.py, leídos del módulo, no a mano."""
    resultado = []
    for patron in rutas_pedidos.urlpatterns:
        assert isinstance(patron, URLPattern), patron  # Hoy no hay include() anidados.
        argumentos = {k: ARGUMENTOS[k] for k in patron.pattern.converters}
        resultado.append((patron.name, reverse(patron.name, kwargs=argumentos)))
    return resultado


@contextmanager
def absorber_errores(prueba, *registradores):
    """`assertLogs` de cada registrador, sin exigir que haya registros (igual que en la 02-04)."""
    contextos = [prueba.assertLogs(nombre, 'ERROR') for nombre in registradores or ('pedidos',)]
    for contexto in contextos:
        contexto.__enter__()
    try:
        yield
    finally:
        for contexto in reversed(contextos):
            try:
                contexto.__exit__(None, None, None)
            except AssertionError:
                pass


class CarpetaTemporalMixin:
    """`BASE_DIR` temporal: las vistas de la base leen y escriben en BASE_DIR/backups."""

    def setUp(self):
        super().setUp()
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        self.carpeta = carpeta.name
        parche = mock.patch.object(views.settings, 'BASE_DIR', carpeta.name)
        parche.start()
        self.addCleanup(parche.stop)


# ---------------------------------------------------------------------------
# Tarea 1 · Inventario de rutas
# ---------------------------------------------------------------------------
class InventarioRutasTests(TestCase):
    def test_el_inventario_sale_del_resolvedor(self):
        nombres = [nombre for nombre, _ in rutas_de_pedidos()]

        self.assertEqual(len(nombres), 40)
        self.assertEqual(len(set(nombres)), len(nombres))

    def test_anonimo_es_redirigido_al_acceso_salvo_rutas_publicas(self):
        for nombre, ruta in rutas_de_pedidos():
            with self.subTest(ruta=nombre):
                respuesta = self.client.get(ruta)

                if nombre in RUTAS_PUBLICAS:
                    self.assertEqual(respuesta.status_code, 200)
                else:
                    self.assertRedirects(respuesta, f'{LOGIN}?next={ruta}',
                                         fetch_redirect_response=False)

    def test_la_lista_publica_existe_en_las_rutas(self):
        # Si se renombra robots_txt, la lista no debe quedar apuntando a nada.
        nombres = {nombre for nombre, _ in rutas_de_pedidos()}

        self.assertLessEqual(RUTAS_PUBLICAS, nombres)

    def test_el_acceso_es_publico(self):
        respuesta = self.client.get(LOGIN)

        self.assertEqual(respuesta.status_code, 200)


# ---------------------------------------------------------------------------
# Tarea 2 · Un anónimo no escribe
# ---------------------------------------------------------------------------
class AnonimoNoEscribeTests(CarpetaTemporalMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.cliente = crear_cliente()
        self.producto = crear_producto()
        self.pedido = crear_pedido(cliente=self.cliente, valor_venta=10_000, estado='PENDIENTE',
                                   items=[{'producto': self.producto}])
        self.pago = crear_pago(self.pedido, monto=4_000)
        self.cotizacion = crear_cotizacion(cliente=self.cliente, estado='ENVIADA',
                                           items=[{'producto': self.producto}])

    def solicitudes(self):
        p, c, cot, prod, pago = (self.pedido.pk, self.cliente.pk, self.cotizacion.pk,
                                 self.producto.pk, self.pago.pk)
        pedido = {'cliente': c, 'resumen_pedido': 'Anónimo', 'valor_venta': 1_000}
        cotizacion = {'cliente': c, 'resumen': 'Anónima', 'valor_total': 1_000, 'validez': 15,
                      'fecha_emision': '2026-10-15'}
        producto = {'nombre': 'Anónimo', 'unidad': 'UNITARIO', 'valor_neto': 1_000}
        cliente = {'nombre': 'Anónimo', 'telefono': '+56 9 0000 0000'}
        pago_datos = {'pedido': p, 'monto': 1_000, 'metodo': 'EFECTIVO'}
        return [
            ('/pedidos/nuevo/', pedido), (f'/pedido/editar/{p}/', pedido),
            (f'/pedido/eliminar/{p}/', {}), (f'/pedido/{p}/cambiar/ENTREGADO/', {}),
            (f'/pedido/duplicar/{p}/', {}),
            ('/clientes/nuevo/', cliente), (f'/clientes/editar/{c}/', cliente),
            (f'/clientes/eliminar/{c}/', {}), ('/api/cliente/nuevo/', cliente),
            ('/cotizaciones/nueva/', cotizacion), (f'/cotizaciones/editar/{cot}/', cotizacion),
            (f'/cotizaciones/eliminar/{cot}/', {}),
            (f'/cotizaciones/convertir/{cot}/', {'fecha_entrega': '2026-10-30'}),
            ('/productos/nuevo/', producto), (f'/productos/editar/{prod}/', producto),
            (f'/productos/eliminar/{prod}/', {}), ('/api/producto/nuevo/', producto),
            ('/pagos/ingresar/', pago_datos), (f'/pagos/ingresar/{p}/', pago_datos),
            (f'/pagos/editar/{pago}/', pago_datos), (f'/pagos/eliminar/{pago}/', {}),
            ('/base_datos/respaldar_bd/accion/', {}), ('/base_datos/restaurar_bd/', {}),
            ('/base_datos/estadisticas_bd/', {}), ('/', {}),
        ]

    def test_post_anonimo_no_cambia_la_base(self):
        antes = conteos()

        with mock.patch.object(views, 'generar_respaldo_mysql') as generar, \
                mock.patch.object(views, 'restaurar_bd_mysql') as restaurar:
            for ruta, datos in self.solicitudes():
                with self.subTest(ruta=ruta):
                    respuesta = self.client.post(ruta, datos)

                    self.assertRedirects(respuesta, f'{LOGIN}?next={ruta}',
                                         fetch_redirect_response=False)

        self.assertEqual(conteos(), antes)
        self.pedido.refresh_from_db()
        self.cotizacion.refresh_from_db()
        self.assertEqual((self.pedido.estado, self.cotizacion.estado), ('PENDIENTE', 'ENVIADA'))
        generar.assert_not_called()
        restaurar.assert_not_called()


# ---------------------------------------------------------------------------
# Tarea 3 · Usuario sin permisos en la base de datos
# ---------------------------------------------------------------------------
class BaseDeDatosPermisosTests(CarpetaTemporalMixin, TestCase):
    RUTAS = ('respaldar_bd', 'generar_respaldo_bd', 'restaurar_bd', 'estadisticas_bd')

    def setUp(self):
        super().setUp()
        self.respaldo = os.path.join(self.carpeta, 'respaldo_prueba.sql')
        with open(self.respaldo, 'w', encoding='utf-8') as archivo:
            archivo.write('-- respaldo de prueba\n')
        self.generar = self.parchar('generar_respaldo_mysql', return_value=self.respaldo)
        self.restaurar = self.parchar('restaurar_bd_mysql')

    def parchar(self, nombre, **opciones):
        parche = mock.patch.object(views, nombre, **opciones)
        simulado = parche.start()
        self.addCleanup(parche.stop)
        return simulado

    def test_usuario_comun_es_redirigido_al_acceso_sin_efecto(self):
        self.client.force_login(crear_usuario())
        antes = conteos()

        for nombre in self.RUTAS:
            ruta = reverse(nombre)
            for metodo in ('get', 'post'):
                with self.subTest(ruta=nombre, metodo=metodo):
                    datos = {'archivo_sql': SimpleUploadedFile('r.sql', b'SELECT 1;')} \
                        if metodo == 'post' else {}
                    respuesta = getattr(self.client, metodo)(ruta, datos)

                    # user_passes_test redirige al acceso (302), no responde 403.
                    self.assertRedirects(respuesta, f'{LOGIN}?next={ruta}',
                                         fetch_redirect_response=False)

        self.generar.assert_not_called()
        self.restaurar.assert_not_called()
        self.assertEqual(conteos(), antes)  # estadisticas_bd no llegó a escribir HistorialBD
        self.assertFalse(os.path.exists(os.path.join(self.carpeta, 'backups')))

    def test_superusuario_entra(self):
        self.client.force_login(crear_superusuario())

        for nombre in ('respaldar_bd', 'restaurar_bd', 'estadisticas_bd'):
            with self.subTest(ruta=nombre):
                self.assertEqual(self.client.get(reverse(nombre)).status_code, 200)

        # POST: no depende de que la ruta acepte GET (la 04-01 la deja solo en POST).
        respuesta = self.client.post(reverse('generar_respaldo_bd'))
        ayudas.cerrar_respuesta(respuesta)  # Cierra el archivo sin romper la transacción.
        self.assertEqual(respuesta.status_code, 200)
        self.generar.assert_called_once_with()
        self.restaurar.assert_not_called()  # El GET de restaurar solo muestra el formulario.


# ---------------------------------------------------------------------------
# Tarea 4 · Puntos JSON
# ---------------------------------------------------------------------------
class PuntosJsonTests(TestCase):
    CLIENTE = {'nombre': 'Cliente rápido', 'telefono': '+56 9 1234 5678'}
    PRODUCTO = {'nombre': 'Producto rápido', 'unidad': 'UNITARIO', 'valor_neto': 10_000}

    def test_sin_sesion_redirigen_en_html_y_no_crean(self):
        # Hoy no responden JSON ni 401: @login_required redirige al acceso en HTML.
        for ruta, datos, modelo in (('/api/cliente/nuevo/', self.CLIENTE, Cliente),
                                    ('/api/producto/nuevo/', self.PRODUCTO, Producto)):
            with self.subTest(ruta=ruta):
                respuesta = self.client.post(ruta, datos)

                self.assertRedirects(respuesta, f'{LOGIN}?next={ruta}',
                                     fetch_redirect_response=False)
                self.assertTrue(respuesta['Content-Type'].startswith('text/html'))
                self.assertFalse(modelo.objects.exists())

    def test_con_sesion_crean_y_responden_json(self):
        self.client.force_login(crear_usuario())

        cliente = self.client.post('/api/cliente/nuevo/', self.CLIENTE).json()
        producto = self.client.post('/api/producto/nuevo/', self.PRODUCTO).json()

        self.assertEqual((cliente['success'], cliente['id']),
                         (True, Cliente.objects.get().pk))
        self.assertEqual((producto['success'], producto['precio']), (True, 11_900))

    def test_con_sesion_rechazan_get(self):
        self.client.force_login(crear_usuario())

        for ruta in ('/api/cliente/nuevo/', '/api/producto/nuevo/'):
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(ruta).status_code, 405)


# ---------------------------------------------------------------------------
# Tarea 5 · Rutas con un pk inexistente
# ---------------------------------------------------------------------------
class PkInexistenteTests(TestCase):
    # Vistas sin @transaccion_segura: el Http404 de get_object_or_404 llega como 404.
    CON_404 = (
        f'/{PK_INEXISTENTE}/', f'/cotizaciones/detalle/{PK_INEXISTENTE}/',
        f'/productos/{PK_INEXISTENTE}/', f'/pagos/detalle/{PK_INEXISTENTE}/',
        f'/pedido/{PK_INEXISTENTE}/cambiar/PENDIENTE/',  # GET: declara la ruta actual (04-01)
        f'/cotizaciones/{PK_INEXISTENTE}/pdf/',
    )
    # Vistas con @transaccion_segura: el decorador captura también el Http404 y responde 500.
    # AUD-02-029 (decisión del desarrollador, 2026-10-27): se fija el 500 de hoy. Se corresponde
    # con la regresión R20 (test_regresiones.PkInexistenteTests), que afirma 404 con estas
    # mismas rutas; al corregir (03-01), esta prueba pasa a 404. eliminar_pago queda fuera (R7).
    CON_500 = (
        f'/pedido/editar/{PK_INEXISTENTE}/', f'/pedido/eliminar/{PK_INEXISTENTE}/',
        f'/pedido/duplicar/{PK_INEXISTENTE}/',  # GET: declara la ruta actual (04-01)
        f'/clientes/editar/{PK_INEXISTENTE}/', f'/clientes/eliminar/{PK_INEXISTENTE}/',
        f'/cotizaciones/editar/{PK_INEXISTENTE}/', f'/cotizaciones/eliminar/{PK_INEXISTENTE}/',
        f'/cotizaciones/convertir/{PK_INEXISTENTE}/',
        f'/productos/editar/{PK_INEXISTENTE}/', f'/productos/eliminar/{PK_INEXISTENTE}/',
        f'/pagos/editar/{PK_INEXISTENTE}/', f'/pagos/ingresar/{PK_INEXISTENTE}/',
    )

    def setUp(self):
        self.client.force_login(crear_usuario())

    def test_vistas_sin_decorador_responden_404(self):
        for ruta in self.CON_404:
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(ruta).status_code, 404)

    def test_vistas_con_transaccion_segura_responden_500(self):
        for ruta in self.CON_500:
            with self.subTest(ruta=ruta):
                with absorber_errores(self, 'pedidos', 'django.request'):
                    respuesta = self.client.get(ruta)

                self.assertEqual(respuesta.status_code, 500)

    def test_cubre_todas_las_rutas_con_pk_salvo_eliminar_pago(self):
        con_pk = {ruta for _, ruta in rutas_de_pedidos()
                  if '/1/' in ruta and 'eliminar_pago' not in ruta and not ruta.startswith('/pagos/eliminar/')}
        probadas = {r.replace(str(PK_INEXISTENTE), '1') for r in self.CON_404 + self.CON_500}

        self.assertEqual(con_pk, probadas)
