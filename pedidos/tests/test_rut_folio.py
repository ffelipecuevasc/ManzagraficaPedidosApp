"""RUT del cliente y folio de cotización (iteración 14-04, RDA-024).

Solo RUT sintéticos (`12.345.678-5`, `11.111.111-1`); nunca RUT reales. El «1000» del negocio no
aparece aquí: el salto es un paso manual del despliegue (D4) y su bloque se prueba con un número
cualquiera.
"""
from unittest import mock

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from pedidos.forms import ClienteForm
from pedidos.models import Cliente, Cotizacion, Pago, SecuenciaFolio
from pedidos.validadores import RUT_PROVISORIO, normalizar_rut, validar_rut

from . import ayudas
from .factorias import crear_cliente, crear_cotizacion, crear_producto, crear_usuario

RUT_A = '12.345.678-5'
RUT_B = '11.111.111-1'


# --------------------------------------------------------------------------------------------
# A. RUT
# --------------------------------------------------------------------------------------------
class ValidadorRutTests(TestCase):
    def test_acepta_formatos_validos(self):
        for valor in ('12.345.678-5', '12345678-5', '123456785', ' 12.345.678-5 ',
                      '11.111.111-1', '1.000.005-K', '1000005-k', '1.000.005-k'):
            with self.subTest(valor=valor):
                validar_rut(valor)  # no lanza

    def test_rechaza_digito_erroneo(self):
        with self.assertRaises(ValidationError) as error:
            validar_rut('12.345.678-4')
        self.assertEqual(error.exception.code, 'rut_digito')

    def test_rechaza_cuerpo_en_ceros_aunque_pase_el_modulo_11(self):
        for valor in (RUT_PROVISORIO, '00000000-0', '0.000.000-0'):
            with self.subTest(valor=valor), self.assertRaises(ValidationError) as error:
                validar_rut(valor)
            self.assertEqual(error.exception.code, 'rut_provisorio')

    def test_rechaza_formato_incorrecto(self):
        for valor in ('', '12.345.67A-5', '123-4', '12345-6', '123.456.789-0', 'abc', '12.345.678-55',
                      '12.345.678-X', '12..345.678-5'):
            with self.subTest(valor=valor), self.assertRaises(ValidationError) as error:
                validar_rut(valor)
            self.assertEqual(error.exception.code, 'rut_formato')

    def test_normaliza(self):
        casos = {
            '12345678-5': RUT_A, '123456785': RUT_A, RUT_A: RUT_A,
            '1000005-k': '1.000.005-K', ' 11111111-1 ': RUT_B,
        }
        for valor, esperado in casos.items():
            with self.subTest(valor=valor):
                self.assertEqual(normalizar_rut(valor), esperado)

    def test_normalizar_deja_igual_lo_que_no_entiende(self):
        self.assertEqual(normalizar_rut('abc'), 'abc')


class ClienteRutModeloTests(TestCase):
    def test_campo_obligatorio_de_12_sin_indice_unico(self):
        campo = Cliente._meta.get_field('rut')
        self.assertEqual(campo.max_length, 12)
        self.assertFalse(campo.blank)
        self.assertFalse(campo.null)
        self.assertFalse(campo.unique)
        self.assertIn(validar_rut, campo.validators)

    def test_dos_clientes_pueden_compartir_rut(self):
        crear_cliente(rut=RUT_PROVISORIO)
        crear_cliente(rut=RUT_PROVISORIO)
        self.assertEqual(Cliente.objects.filter(rut=RUT_PROVISORIO).count(), 2)

    def test_full_clean_normaliza(self):
        cliente = Cliente(nombre='Cliente sintético', telefono='+56 9 0000 0000', rut='12345678-5')
        cliente.full_clean()
        self.assertEqual(cliente.rut, RUT_A)

    def test_factoria_usa_rut_sintetico_valido(self):
        cliente = crear_cliente()
        validar_rut(cliente.rut)


class ClienteRutFormularioTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_usuario())

    def datos(self, **campos):
        datos = {'nombre': 'Cliente sintético', 'telefono': '+56 9 0000 0000', 'email': '', 'rut': '12345678-5'}
        datos.update(campos)
        return datos

    def test_formulario_normaliza_al_guardar(self):
        form = ClienteForm(self.datos())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().rut, RUT_A)

    def test_formulario_rechaza_sin_rut_y_provisorio(self):
        for valor in ('', RUT_PROVISORIO, '12.345.678-4'):
            with self.subTest(valor=valor):
                form = ClienteForm(self.datos(rut=valor))
                self.assertFalse(form.is_valid())
                self.assertIn('rut', form.errors)

    def test_crear_cliente_por_la_vista(self):
        respuesta = self.client.post('/clientes/nuevo/', self.datos(rut='111111111'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Cliente.objects.filter(rut=RUT_B).exists())

    def test_editar_cliente_con_rut_provisorio_exige_corregirlo(self):
        cliente = crear_cliente(rut=RUT_PROVISORIO)
        formulario = self.client.get(f'/clientes/editar/{cliente.pk}/')
        self.assertContains(formulario, RUT_PROVISORIO)
        respuesta = self.client.post(f'/clientes/editar/{cliente.pk}/', self.datos(nombre=cliente.nombre,
                                                                                 rut=RUT_PROVISORIO))
        self.assertEqual(respuesta.status_code, 200)
        cliente.refresh_from_db()
        self.assertEqual(cliente.rut, RUT_PROVISORIO)
        self.client.post(f'/clientes/editar/{cliente.pk}/', self.datos(nombre=cliente.nombre, rut='12345678-5'))
        cliente.refresh_from_db()
        self.assertEqual(cliente.rut, RUT_A)

    def test_modal_rapido_exige_rut_y_normaliza(self):
        sin_rut = self.client.post('/api/cliente/nuevo/', self.datos(rut='')).json()
        self.assertFalse(sin_rut['success'])
        self.assertIn('rut', sin_rut['errors'])
        provisorio = self.client.post('/api/cliente/nuevo/', self.datos(rut=RUT_PROVISORIO)).json()
        self.assertFalse(provisorio['success'])
        creado = self.client.post('/api/cliente/nuevo/', self.datos(rut='11111111-1')).json()
        self.assertTrue(creado['success'])
        self.assertEqual(Cliente.objects.get(pk=creado['id']).rut, RUT_B)

    def test_admin_normaliza_y_rechaza(self):
        self.client.force_login(crear_usuario(is_staff=True, is_superuser=True))
        ruta = reverse('admin:pedidos_cliente_add')
        respuesta = self.client.post(ruta, self.datos(rut=RUT_PROVISORIO))
        self.assertEqual(respuesta.status_code, 200)  # vuelve con el error
        self.assertFalse(Cliente.objects.filter(rut=RUT_PROVISORIO).exists())
        self.client.post(ruta, self.datos(rut='12345678-5'))
        self.assertTrue(Cliente.objects.filter(rut=RUT_A).exists())

    def test_formularios_con_modal_traen_el_campo_rut(self):
        for ruta in ('/pedidos/nuevo/', '/cotizaciones/nueva/'):
            with self.subTest(ruta=ruta):
                self.assertContains(self.client.get(ruta), 'id="new_client_rut"')


# --------------------------------------------------------------------------------------------
# B. Folio
# --------------------------------------------------------------------------------------------
class FolioModeloTests(TestCase):
    def test_campo_propio_no_editable_y_unico(self):
        campo = Cotizacion._meta.get_field('folio')
        self.assertFalse(campo.editable)
        self.assertTrue(campo.unique)

    def test_correlativo_desde_el_contador(self):
        SecuenciaFolio.objects.update_or_create(nombre=SecuenciaFolio.COTIZACION, defaults={'ultimo_folio': 41})
        primera = crear_cotizacion()
        segunda = crear_cotizacion()
        self.assertEqual((primera.folio, segunda.folio), (42, 43))
        self.assertNotEqual(primera.folio, primera.pk)

    def test_no_reutiliza_el_folio_de_la_ultima_borrada(self):
        crear_cotizacion()
        ultima = crear_cotizacion()
        folio_borrado = ultima.folio
        ultima.delete()
        self.assertEqual(crear_cotizacion().folio, folio_borrado + 1)

    def test_editar_no_cambia_el_folio(self):
        cotizacion = crear_cotizacion()
        folio = cotizacion.folio
        cotizacion.resumen = 'Otro'
        cotizacion.save()
        cotizacion.refresh_from_db()
        self.assertEqual(cotizacion.folio, folio)

    def test_transaccion_revertida_no_consume_folio(self):
        crear_cotizacion()
        antes = SecuenciaFolio.objects.get(nombre=SecuenciaFolio.COTIZACION).ultimo_folio
        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                crear_cotizacion()
                raise RuntimeError('reversa forzada')
        self.assertEqual(SecuenciaFolio.objects.get(nombre=SecuenciaFolio.COTIZACION).ultimo_folio, antes)
        self.assertEqual(crear_cotizacion().folio, antes + 1)

    def test_fallo_al_guardar_no_deja_folio_en_la_instancia(self):
        cotizacion = Cotizacion(cliente=crear_cliente(), resumen='x', detalles='x', valor_total=0)
        with mock.patch('django.db.models.Model.save', side_effect=IntegrityError('forzado')):
            with self.assertRaises(IntegrityError):
                cotizacion.save()
        self.assertIsNone(cotizacion.folio)

    def test_sin_fila_del_contador_parte_del_mayor_folio(self):
        crear_cotizacion()
        mayor = crear_cotizacion().folio
        SecuenciaFolio.objects.all().delete()
        self.assertEqual(crear_cotizacion().folio, mayor + 1)


class FolioCaminosTests(TestCase):
    """Todos los caminos que crean o editan una cotización (crear, editar, convertir)."""

    def setUp(self):
        self.usuario = crear_usuario()
        self.client.force_login(self.usuario)
        self.cliente = crear_cliente(rut=RUT_A)
        self.producto = crear_producto(valor_neto=10_000)
        SecuenciaFolio.objects.update_or_create(nombre=SecuenciaFolio.COTIZACION, defaults={'ultimo_folio': 1233})

    def post(self, ruta, datos):
        datos = ayudas.con_token(self.client, ruta, datos)
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(ruta, datos)

    def datos(self, **campos):
        datos = {
            'cliente': self.cliente.pk, 'resumen': 'Pendones', 'detalles': '<p>Detalle</p>',
            'valor_total': 10_000, 'validez': 15, 'fecha_emision': '2026-10-15',
            'items_json': ayudas.items_json((self.producto, '1', 10_000)),
        }
        datos.update(campos)
        return datos

    def test_crear_editar_y_convertir(self):
        self.post('/cotizaciones/nueva/', self.datos())
        cotizacion = Cotizacion.objects.get()
        self.assertEqual(cotizacion.folio, 1234)

        self.post(f'/cotizaciones/editar/{cotizacion.pk}/', self.datos(resumen='Otro'))
        cotizacion.refresh_from_db()
        self.assertEqual((cotizacion.resumen, cotizacion.folio), ('Otro', 1234))

        respuesta = self.post(f'/cotizaciones/convertir/{cotizacion.pk}/',
                              {'fecha_entrega': '2099-01-10', 'valor_abonado': 2_000, 'metodo_pago': 'EFECTIVO'})
        self.assertEqual(respuesta.status_code, 302)
        cotizacion.refresh_from_db()
        self.assertEqual((cotizacion.estado, cotizacion.folio), ('ACEPTADA', 1234))
        self.assertEqual(Pago.objects.get().nota, 'Abono inicial por conversión de la cotización folio 1234')

    def test_textos_visibles_con_folio_sin_separador(self):
        cotizacion = crear_cotizacion(cliente=self.cliente)
        self.assertEqual(cotizacion.folio, 1234)
        rutas = (
            '/cotizaciones/lista/',
            f'/cotizaciones/detalle/{cotizacion.pk}/',
            f'/cotizaciones/editar/{cotizacion.pk}/',
            f'/cotizaciones/eliminar/{cotizacion.pk}/',
            f'/cotizaciones/convertir/{cotizacion.pk}/',
        )
        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertContains(respuesta, '1234')
                self.assertNotContains(respuesta, '1\xa0234')
                self.assertNotContains(respuesta, '1 234')
                self.assertNotContains(respuesta, '1.234')

    def test_detalle_muestra_el_rut(self):
        cotizacion = crear_cotizacion(cliente=self.cliente)
        self.assertContains(self.client.get(f'/cotizaciones/detalle/{cotizacion.pk}/'), RUT_A)

    def test_plantilla_del_pdf_con_folio_y_rut(self):
        from django.template.loader import render_to_string
        cotizacion = crear_cotizacion(cliente=self.cliente)
        html = render_to_string('pedidos/cotizacion_pdf.html', {'cotizacion': cotizacion})
        self.assertIn('1234', html)
        self.assertNotIn('1\xa0234', html)
        self.assertIn(RUT_A, html)

    def test_nombre_del_pdf_usa_el_folio(self):
        cotizacion = crear_cotizacion(cliente=self.cliente)
        with mock.patch.dict('sys.modules', {'weasyprint': mock.MagicMock(**{
                'HTML.return_value.write_pdf.return_value': b'%PDF-ficticio'})}):
            respuesta = self.client.get(f'/cotizaciones/{cotizacion.pk}/pdf/')
        self.assertIn('filename="Cotizacion_1234.pdf"', respuesta['Content-Disposition'])

    def test_listado_busca_por_folio(self):
        buscada = crear_cotizacion(cliente=self.cliente, resumen='Buscada')
        crear_cotizacion(cliente=self.cliente, resumen='Otra')
        for termino in ('1234', '#1234', ' 1234 '):
            with self.subTest(termino=termino):
                respuesta = self.client.get('/cotizaciones/lista/', {'busqueda': termino})
                self.assertEqual([c.pk for c in respuesta.context['cotizaciones']], [buscada.pk])


class FolioConcurrenciaTests(TransactionTestCase):
    """Dos conexiones que asignan a la vez reciben folios distintos (select_for_update)."""

    def test_folios_distintos_en_hilos(self):
        import threading
        from django.db import connection
        cliente = crear_cliente()
        crear_cotizacion(cliente=cliente)
        folios, errores = [], []

        def crear():
            try:
                folios.append(crear_cotizacion(cliente=cliente).folio)
            except Exception as error:  # se informa abajo; la prueba falla si hubo alguno
                errores.append(repr(error))
            finally:
                connection.close()

        hilos = [threading.Thread(target=crear) for _ in range(4)]
        for hilo in hilos:
            hilo.start()
        for hilo in hilos:
            hilo.join()
        self.assertEqual(errores, [])
        self.assertEqual(len(set(folios)), 4)


# --------------------------------------------------------------------------------------------
# Paso único del folio (bloque de manage.py shell, D4)
# --------------------------------------------------------------------------------------------
class PasoUnicoFolioTests(TestCase):
    def correr(self, inicio):
        from pedidos.paso_unico_folio import fijar_inicio_folio
        return fijar_inicio_folio(inicio)

    def test_rechaza_inicio_invalido(self):
        for inicio in (0, -5, '500', True):
            with self.subTest(inicio=inicio):
                resultado, texto = self.correr(inicio)
                self.assertFalse(resultado)
                self.assertIn('NEGADO', texto)

    def test_fija_el_anterior_al_inicio_e_imprime(self):
        crear_cotizacion()
        resultado, texto = self.correr(500)
        self.assertTrue(resultado)
        self.assertEqual(SecuenciaFolio.objects.get(nombre=SecuenciaFolio.COTIZACION).ultimo_folio, 499)
        self.assertIn('antes: 1', texto)
        self.assertIn('después: 499', texto)
        self.assertEqual(crear_cotizacion().folio, 500)

    def test_se_niega_si_una_cotizacion_tiene_folio_igual_o_mayor(self):
        crear_cotizacion()
        self.correr(500)
        crear_cotizacion()  # folio 500
        resultado, texto = self.correr(500)
        self.assertFalse(resultado)
        self.assertIn('NEGADO', texto)
        self.assertEqual(SecuenciaFolio.objects.get(nombre=SecuenciaFolio.COTIZACION).ultimo_folio, 500)

    def test_se_puede_volver_a_correr_tras_borrar_la_de_prueba(self):
        """Aviso 2, opción C: mira las cotizaciones, no el contador."""
        self.correr(500)
        prueba = crear_cotizacion()
        self.assertEqual(prueba.folio, 500)
        prueba.delete()
        resultado, texto = self.correr(500)
        self.assertTrue(resultado)
        self.assertIn('antes: 500', texto)
        self.assertIn('después: 499', texto)
        self.assertEqual(crear_cotizacion().folio, 500)
