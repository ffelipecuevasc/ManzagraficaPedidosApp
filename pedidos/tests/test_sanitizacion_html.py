"""Sanitización del HTML enriquecido y guardia de inyección SQL (iteración 04-07, AUD-03-001).

D1: se sanitiza al guardar y al mostrar. D3: lista blanca exacta de la barra del editor, sin
atributos. D4: no se limpian datos ya guardados; la guardia de SQL usa ``ast``.

Las pruebas «al mostrar» guardan el HTML **directo en la base** (sin formulario), como lo dejaría
el admin, la duplicación, la conversión o un dato anterior a esta iteración.
"""
import ast
from pathlib import Path

from django.test import TestCase

from pedidos.models import Cotizacion, Pedido, Producto
from pedidos.sanitizar import sanitizar_html

from . import ayudas
from .factorias import crear_cotizacion, crear_pedido, crear_producto, crear_usuario

PELIGROSO = '<p>a</p><script>alert(1)</script>'
FORMATO = '<p><b>a</b> <i>b</i></p><ul><li>c</li></ul>'
IMAGEN_INCRUSTADA = '<p>Ver imagen</p><img src="data:image/png;base64,iVBORw0KGgo=" style="width:50%">'

VARIANTES = {
    'SCRIPT en mayúsculas': '<p>a</p><SCRIPT>alert(1)</SCRIPT>',
    'svg con onload': '<p>a</p><svg onload="alert(1)"></svg>',
    'iframe': '<p>a</p><iframe src="https://ejemplo.invalid/"></iframe>',
    'style': '<p>a</p><style>.marca-oculta{display:none}</style>',
    'comentario': '<p>a</p><!-- comentario-oculto -->',
}
# Marcas únicas de las variantes: la página completa (base.html) trae sus propios <svg>, <style> y
# comentarios, así que en las respuestas se buscan las marcas, no las etiquetas.
PROHIBIDOS = ('alert(1)', 'ejemplo.invalid', 'marca-oculta', 'comentario-oculto')


class SanitizarHtmlTests(TestCase):
    """La función de `pedidos/sanitizar.py`, sin pasar por vistas."""

    def test_script_se_elimina_con_su_contenido(self):
        self.assertEqual(sanitizar_html(PELIGROSO), '<p>a</p>')

    def test_variantes_no_sobreviven(self):
        for nombre, texto in VARIANTES.items():
            with self.subTest(nombre):
                limpio = sanitizar_html(texto)
                self.assertEqual(limpio, '<p>a</p>')

    def test_atributos_se_eliminan_y_el_texto_se_conserva(self):
        self.assertEqual(sanitizar_html('<img src=x onerror=alert(1)>'), '')
        self.assertEqual(sanitizar_html('<a href="javascript:alert(1)">x</a>'), 'x')
        self.assertEqual(sanitizar_html('<p class="a" style="color:red">t</p>'), '<p>t</p>')

    def test_div_y_span_se_quitan_conservando_el_texto(self):
        self.assertEqual(sanitizar_html('<div><span style="font-weight:bold">t</span></div>'), 't')

    def test_formato_permitido_sale_identico(self):
        self.assertEqual(sanitizar_html(FORMATO), FORMATO)
        self.assertEqual(sanitizar_html('<p>a<br>b</p><ol><li><strong>c</strong> <em>d</em></li></ol>'),
                         '<p>a<br>b</p><ol><li><strong>c</strong> <em>d</em></li></ol>')

    def test_es_idempotente(self):
        for texto in (PELIGROSO, FORMATO, IMAGEN_INCRUSTADA, *VARIANTES.values()):
            with self.subTest(texto=texto):
                una = sanitizar_html(texto)
                self.assertEqual(sanitizar_html(una), una)

    def test_nulo_y_vacio_se_devuelven_tal_cual(self):
        self.assertIsNone(sanitizar_html(None))
        self.assertEqual(sanitizar_html(''), '')


class AlMostrarTests(TestCase):
    """Filtro `html_seguro` en las tres plantillas de detalle (D1, al mostrar)."""

    def setUp(self):
        self.client.force_login(crear_usuario())

    def detalles(self, texto):
        pedido = crear_pedido(detalles_pedido=texto)
        cotizacion = crear_cotizacion(detalles=texto)
        producto = crear_producto(descripcion=texto)
        return {
            'pedido': f'/{pedido.pk}/',
            'cotización': f'/cotizaciones/detalle/{cotizacion.pk}/',
            'producto': f'/productos/{producto.pk}/',
        }

    def test_script_guardado_directo_no_llega_al_navegador(self):
        for nombre, ruta in self.detalles(PELIGROSO).items():
            with self.subTest(nombre):
                respuesta = self.client.get(ruta)
                self.assertContains(respuesta, '<p>a</p>')
                self.assertNotContains(respuesta, 'alert(1)')

    def test_variantes_guardadas_directo_no_llegan(self):
        for variante, texto in VARIANTES.items():
            for nombre, ruta in self.detalles(texto).items():
                with self.subTest(variante=variante, pantalla=nombre):
                    contenido = self.client.get(ruta).content.decode()
                    for prohibido in PROHIBIDOS:
                        self.assertNotIn(prohibido, contenido)

    def test_atributos_guardados_directo_no_llegan(self):
        texto = '<img src=x onerror=alert(1)><a href="javascript:alert(2)">x</a><p class="a" style="color:red">t</p>'
        for nombre, ruta in self.detalles(texto).items():
            with self.subTest(nombre):
                respuesta = self.client.get(ruta)
                contenido = respuesta.content.decode()
                self.assertNotIn('onerror', contenido)
                self.assertNotIn('javascript:alert', contenido)
                self.assertNotIn('color:red', contenido)
                self.assertContains(respuesta, '<p>t</p>')

    def test_formato_permitido_se_muestra_igual(self):
        for nombre, ruta in self.detalles(FORMATO).items():
            with self.subTest(nombre):
                self.assertContains(self.client.get(ruta), FORMATO)

    def test_detalle_vacio_tras_sanitizar_muestra_el_texto_por_defecto(self):
        for texto in ('', '<script>alert(1)</script>'):
            with self.subTest(texto=texto):
                pedido = crear_pedido(detalles_pedido=texto)
                respuesta = self.client.get(f'/{pedido.pk}/')
                self.assertContains(respuesta, 'Sin especificaciones adicionales.')
                self.assertNotContains(respuesta, 'alert(1)')


class AlGuardarTests(TestCase):
    """`clean_<campo>` de PedidoForm, CotizacionForm y ProductoForm (D1, al guardar)."""

    def setUp(self):
        self.client.force_login(crear_usuario())
        self.producto = crear_producto(valor_neto=10_000)

    def post(self, ruta, datos):
        datos = ayudas.con_token(self.client, ruta, datos)
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(ruta, datos)

    def datos_pedido(self, cliente_pk, texto):
        return {'cliente': cliente_pk, 'resumen_pedido': 'Con HTML', 'valor_venta': 11_900,
                'detalles_pedido': texto,
                'items_json': ayudas.items_json((self.producto, '1', 11_900))}

    def datos_cotizacion(self, cliente_pk, texto):
        return {'cliente': cliente_pk, 'resumen': 'Con HTML', 'detalles': texto,
                'valor_total': 10_000, 'validez': 15, 'fecha_emision': '2026-10-15',
                'items_json': ayudas.items_json((self.producto, '1', 10_000))}

    @staticmethod
    def datos_producto(texto):
        return {'nombre': 'Producto con HTML', 'unidad': 'UNITARIO', 'valor_neto': 10_000,
                'descripcion': texto}

    def test_crear_pedido_guarda_sin_script(self):
        cliente = crear_pedido().cliente
        self.post('/pedidos/nuevo/', self.datos_pedido(cliente.pk, PELIGROSO))
        self.assertEqual(Pedido.objects.latest('pk').detalles_pedido, '<p>a</p>')

    def test_editar_pedido_guarda_sin_script(self):
        pedido = crear_pedido()
        self.post(f'/pedido/editar/{pedido.pk}/', self.datos_pedido(pedido.cliente.pk, PELIGROSO))
        pedido.refresh_from_db()
        self.assertEqual(pedido.detalles_pedido, '<p>a</p>')

    def test_crear_y_editar_cotizacion_guardan_sin_script(self):
        cliente = crear_pedido().cliente
        self.post('/cotizaciones/nueva/', self.datos_cotizacion(cliente.pk, PELIGROSO))
        cotizacion = Cotizacion.objects.get()
        self.assertEqual(cotizacion.detalles, '<p>a</p>')

        self.post(f'/cotizaciones/editar/{cotizacion.pk}/',
                  self.datos_cotizacion(cliente.pk, '<p>b</p><script>alert(2)</script>'))
        cotizacion.refresh_from_db()
        self.assertEqual(cotizacion.detalles, '<p>b</p>')

    def test_crear_y_editar_producto_guardan_sin_script(self):
        self.post('/productos/nuevo/', self.datos_producto(PELIGROSO))
        producto = Producto.objects.get(nombre='Producto con HTML')
        self.assertEqual(producto.descripcion, '<p>a</p>')

        self.post(f'/productos/editar/{producto.pk}/', self.datos_producto('<p>b</p><script>x</script>'))
        producto.refresh_from_db()
        self.assertEqual(producto.descripcion, '<p>b</p>')

    def test_creacion_rapida_de_producto_guarda_sin_script(self):
        respuesta = self.client.post('/api/producto/nuevo/', self.datos_producto(PELIGROSO))
        self.assertTrue(respuesta.json()['success'])
        self.assertEqual(Producto.objects.get(nombre='Producto con HTML').descripcion, '<p>a</p>')

    def test_guardar_elimina_una_imagen_incrustada(self):
        # Decisión del 2026-11-20: los pedidos 46 y 56 de la réplica traen <img> con data:. Si se
        # editan y guardan, D1 borra la imagen de la base. Esta prueba fija esa consecuencia.
        pedido = crear_pedido(detalles_pedido=IMAGEN_INCRUSTADA)
        self.post(f'/pedido/editar/{pedido.pk}/', self.datos_pedido(pedido.cliente.pk, IMAGEN_INCRUSTADA))
        pedido.refresh_from_db()
        self.assertEqual(pedido.detalles_pedido, '<p>Ver imagen</p>')


class CopiasTests(TestCase):
    """Duplicar y convertir copian el texto sin formulario: lo cubre el filtro al mostrar."""

    def setUp(self):
        self.client.force_login(crear_usuario())

    def test_pedido_duplicado_no_entrega_el_script(self):
        original = crear_pedido(detalles_pedido=PELIGROSO)
        ayudas.duplicar(self.client, original)
        copia = Pedido.objects.exclude(pk=original.pk).get()

        respuesta = self.client.get(f'/{copia.pk}/')
        self.assertContains(respuesta, '<p>a</p>')
        self.assertNotContains(respuesta, 'alert(1)')

    def test_pedido_convertido_no_entrega_el_script(self):
        producto = crear_producto()
        cotizacion = crear_cotizacion(detalles=PELIGROSO, estado='ENVIADA', valor_total=10_000, items=[
            {'producto': producto, 'cantidad': '1', 'precio_unitario': 10_000}])
        ruta = f'/cotizaciones/convertir/{cotizacion.pk}/'
        datos = ayudas.con_token(self.client, ruta, {**ayudas.datos_reabrir(), 'valor_abonado': '0'})
        with self.captureOnCommitCallbacks(execute=True):
            self.client.post(ruta, datos)
        pedido = Pedido.objects.get()

        respuesta = self.client.get(f'/{pedido.pk}/')
        self.assertContains(respuesta, '<p>a</p>')
        self.assertNotContains(respuesta, 'alert(1)')


# ---------------------------------------------------------------------------
# Guardia de inyección SQL (D4)
# ---------------------------------------------------------------------------
CARPETA_PEDIDOS = Path(__file__).resolve().parent.parent
METODOS_PROHIBIDOS = {'raw', 'extra'}


def _es_texto_armado(nodo):
    """f-string, concatenación, `%` o `.format(...)`: SQL armado con texto."""
    if isinstance(nodo, ast.JoinedStr):
        return True
    if isinstance(nodo, ast.BinOp) and isinstance(nodo.op, (ast.Add, ast.Mod)):
        return True
    return (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute)
            and nodo.func.attr == 'format')


def hallazgos_sql(codigo, nombre='<texto>'):
    """Lista de usos peligrosos en `codigo`: (archivo, línea, motivo)."""
    hallazgos = []
    for nodo in ast.walk(ast.parse(codigo, filename=nombre)):
        if not isinstance(nodo, ast.Call):
            continue
        funcion = nodo.func
        nombre_funcion = funcion.attr if isinstance(funcion, ast.Attribute) else getattr(funcion, 'id', None)
        if isinstance(funcion, ast.Attribute) and nombre_funcion in METODOS_PROHIBIDOS:
            hallazgos.append((nombre, nodo.lineno, f'.{nombre_funcion}('))
        elif nombre_funcion == 'RawSQL':
            hallazgos.append((nombre, nodo.lineno, 'RawSQL('))
        elif nombre_funcion in ('execute', 'executemany') and nodo.args and _es_texto_armado(nodo.args[0]):
            hallazgos.append((nombre, nodo.lineno, f'{nombre_funcion}( con SQL armado con texto'))
    return hallazgos


def archivos_de_aplicacion():
    for ruta in sorted(CARPETA_PEDIDOS.rglob('*.py')):
        partes = ruta.relative_to(CARPETA_PEDIDOS).parts
        if partes[0] in ('tests', 'migrations'):
            continue
        yield ruta


class GuardiaSqlTests(TestCase):
    def test_el_codigo_de_la_aplicacion_no_arma_sql_con_texto(self):
        archivos = list(archivos_de_aplicacion())
        self.assertIn('utils.py', {ruta.name for ruta in archivos})  # la guardia ve el único execute

        hallazgos = []
        for ruta in archivos:
            hallazgos += hallazgos_sql(ruta.read_text(encoding='utf-8'), str(ruta.relative_to(CARPETA_PEDIDOS)))
        self.assertEqual(hallazgos, [])

    def test_la_guardia_detecta_los_casos_prohibidos(self):
        casos = {
            'f-string': 'cursor.execute(f"SELECT * FROM t WHERE id = {x}")',
            'concatenación': 'cursor.execute("SELECT * FROM t WHERE id = " + x)',
            'porcentaje': 'cursor.execute("SELECT * FROM t WHERE id = %s" % x)',
            'format': 'cursor.execute("SELECT * FROM t WHERE id = {}".format(x))',
            'raw': 'Pedido.objects.raw("SELECT 1")',
            'extra': 'Pedido.objects.extra(where=["1=1"])',
            'RawSQL': 'Pedido.objects.annotate(x=RawSQL("SELECT 1", []))',
        }
        for nombre, codigo in casos.items():
            with self.subTest(nombre):
                self.assertEqual(len(hallazgos_sql(codigo)), 1)

    def test_la_guardia_acepta_sql_fijo_con_parametros(self):
        codigo = 'sql = "SELECT 1 WHERE a = %s"\ncursor.execute(sql, [valor])\ncursor.execute("SELECT 1")'
        self.assertEqual(hallazgos_sql(codigo), [])
