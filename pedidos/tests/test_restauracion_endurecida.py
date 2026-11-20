"""Restauración endurecida (04-04): validación del volcado, confirmación, constancia y emergencia.

Ninguna prueba ejecuta `mysqldump` ni `mysql`: se reemplazan `generar_respaldo_mysql`,
`restaurar_bd_mysql` o `subprocess.run` donde los busca el código. Los volcados son de prueba
(`ayudas.VOLCADO_VALIDO` y variantes), nunca de la base real.
"""
import os
import subprocess
import tempfile
import time
from unittest import mock

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase

from pedidos import utils, views
from pedidos.models import RegistroEvento
from pedidos.tests import ayudas, factorias
from pedidos.tests.ayudas import VOLCADO_VALIDO

RUTA = '/base_datos/restaurar_bd/'


def escribir(carpeta, nombre, contenido):
    ruta = os.path.join(carpeta, nombre)
    with open(ruta, 'wb') as archivo:
        archivo.write(contenido)
    return ruta


# ---------------------------------------------------------------------------
# D2 · Qué es un volcado válido (función de utils.py)
# ---------------------------------------------------------------------------
class RevisarVolcadoTests(SimpleTestCase):
    def setUp(self):
        self.carpeta = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.carpeta, ignore_errors=True))

    def revisar(self, contenido):
        return utils.revisar_volcado(escribir(self.carpeta, 'v.sql', contenido))

    def test_volcado_valido_cumple_todas_las_reglas(self):
        reglas = self.revisar(VOLCADO_VALIDO)
        self.assertTrue(all(reglas.values()), reglas)
        self.assertTrue(utils.volcado_valido(os.path.join(self.carpeta, 'v.sql')))

    def test_reglas_nombradas(self):
        self.assertEqual(set(self.revisar(VOLCADO_VALIDO)), {
            'no_vacio', 'dentro_del_tope', 'texto_utf8', 'cabecera_mysql_dump', 'linea_de_cierre',
            'tabla_pedidos_pedido', 'tabla_django_migrations', 'sin_sentencias_prohibidas',
        })

    def test_vacio(self):
        reglas = self.revisar(b'')
        self.assertFalse(reglas['no_vacio'])
        self.assertFalse(utils.volcado_valido(os.path.join(self.carpeta, 'v.sql')))

    def test_sin_cabecera(self):
        self.assertFalse(self.revisar(VOLCADO_VALIDO.replace(b'-- MySQL dump', b'-- Otro'))['cabecera_mysql_dump'])

    def test_sin_cierre(self):
        self.assertFalse(self.revisar(VOLCADO_VALIDO.replace(b'-- Dump completed', b'-- Cortado'))['linea_de_cierre'])

    def test_sin_tablas_propias(self):
        reglas = self.revisar(VOLCADO_VALIDO.replace(b'`pedidos_pedido`', b'`otra`')
                              .replace(b'`django_migrations`', b'`otra2`'))
        self.assertFalse(reglas['tabla_pedidos_pedido'])
        self.assertFalse(reglas['tabla_django_migrations'])

    def test_no_es_utf8(self):
        self.assertFalse(self.revisar(VOLCADO_VALIDO + b'\xff\xfe\n')['texto_utf8'])

    def test_sentencias_prohibidas(self):
        for sentencia in (b'CREATE DATABASE x;', b'drop database x;', b'USE otra;', b'GRANT ALL ON *.* TO a;',
                          b'CREATE USER a;', b'/*!40000 DROP DATABASE x */;', b'  Use otra;'):
            with self.subTest(sentencia=sentencia):
                contenido = VOLCADO_VALIDO.replace(b'/*!40101 SET NAMES utf8mb4 */;\n',
                                                   sentencia + b'\n')
                self.assertFalse(self.revisar(contenido)['sin_sentencias_prohibidas'])

    def test_palabras_dentro_de_datos_no_cuentan(self):
        contenido = VOLCADO_VALIDO.replace(
            b'/*!40101 SET NAMES utf8mb4 */;\n',
            b"INSERT INTO `pedidos_pedido` VALUES (1,'USE la tinta; DROP DATABASE no');\n")
        self.assertTrue(self.revisar(contenido)['sin_sentencias_prohibidas'])

    def test_sobre_el_tope_no_se_lee(self):
        ruta = escribir(self.carpeta, 'v.sql', VOLCADO_VALIDO)
        with mock.patch.object(utils, 'TOPE_VOLCADO_BYTES', len(VOLCADO_VALIDO) - 1):
            reglas = utils.revisar_volcado(ruta)
        self.assertFalse(reglas['dentro_del_tope'])
        self.assertFalse(all(reglas.values()))

    def test_tope_es_20_mb(self):
        self.assertEqual(utils.TOPE_VOLCADO_BYTES, 20 * 1024 * 1024)


# ---------------------------------------------------------------------------
# Punto 5 y D5 · generar_respaldo_mysql: .sql vacío y respaldo de emergencia
# ---------------------------------------------------------------------------
class GenerarRespaldoTests(SimpleTestCase):
    def setUp(self):
        self.carpeta = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.carpeta, ignore_errors=True))
        parche = mock.patch.object(utils.settings, 'BASE_DIR', self.carpeta)
        parche.start()
        self.addCleanup(parche.stop)
        self.backups = os.path.join(self.carpeta, 'backups')

    def sql_en_backups(self):
        return sorted(n for n in os.listdir(self.backups) if n.endswith('.sql')) if os.path.isdir(self.backups) else []

    def test_sin_mysqldump_no_deja_sql_vacio(self):
        with mock.patch.object(utils.subprocess, 'run', side_effect=FileNotFoundError('mysqldump')), \
                self.assertRaises(FileNotFoundError):
            utils.generar_respaldo_mysql()
        self.assertEqual(self.sql_en_backups(), [])

    def test_otro_fallo_no_deja_sql_vacio(self):
        with mock.patch.object(utils.subprocess, 'run', side_effect=OSError('disco')), \
                self.assertRaises(OSError):
            utils.generar_respaldo_mysql()
        self.assertEqual(self.sql_en_backups(), [])

    def test_fallo_de_mysqldump_sigue_sin_dejar_archivo(self):
        error = subprocess.CalledProcessError(2, 'mysqldump', stderr=b'acceso denegado')
        with mock.patch.object(utils.subprocess, 'run', side_effect=error), self.assertRaises(Exception):
            utils.generar_respaldo_mysql()
        self.assertEqual(self.sql_en_backups(), [])

    def test_prefijo_de_emergencia(self):
        with mock.patch.object(utils.subprocess, 'run'):
            ruta = utils.generar_respaldo_mysql(prefijo='emergencia')
        self.assertTrue(os.path.basename(ruta).startswith('emergencia_'))
        with mock.patch.object(utils.subprocess, 'run'):
            normal = utils.generar_respaldo_mysql()
        self.assertTrue(os.path.basename(normal).startswith('respaldo_'))

    def test_emergencia_fuera_de_la_rotacion_y_solo_el_ultimo(self):
        os.makedirs(self.backups)
        viejo = escribir(self.backups, 'emergencia_01-01-2026_00-00-00.sql', b'x')
        antiguo = time.time() - 3600
        os.utime(viejo, (antiguo, antiguo))
        for i in range(6):
            ruta = escribir(self.backups, f'respaldo_0{i}-01-2026_00-00-00.sql', b'x')
            os.utime(ruta, (antiguo + i + 1, antiguo + i + 1))
        utils.limpiar_backups_antiguos(self.backups, mantener=5)
        nombres = self.sql_en_backups()
        self.assertIn('emergencia_01-01-2026_00-00-00.sql', nombres)  # no lo borra la rotación
        self.assertEqual(len([n for n in nombres if n.startswith('respaldo_')]), 5)

        with mock.patch.object(utils.subprocess, 'run'):
            nuevo = utils.generar_respaldo_mysql(prefijo='emergencia')
        emergencias = [n for n in self.sql_en_backups() if n.startswith('emergencia_')]
        self.assertEqual(emergencias, [os.path.basename(nuevo)])  # el anterior se borra


# ---------------------------------------------------------------------------
# Vista restaurar_bd: puntos 1 a 4 y 6 del alcance
# ---------------------------------------------------------------------------
class RestaurarVistaBase(TestCase):
    def setUp(self):
        self.usuario = factorias.crear_usuario('administracion', is_superuser=True, is_staff=True)
        self.client.force_login(self.usuario)
        self.carpeta = tempfile.mkdtemp()
        self.addCleanup(lambda: __import__('shutil').rmtree(self.carpeta, ignore_errors=True))
        ajuste = self.settings(BASE_DIR=self.carpeta)  # 04-05, D2
        ajuste.enable()
        self.addCleanup(ajuste.disable)
        for objetivo, nombre, opciones in (
                (views,'generar_respaldo_mysql', {'side_effect': ayudas.respaldo_de_emergencia(self.carpeta)}),
                (views, 'restaurar_bd_mysql', {})):
            parche = mock.patch.object(objetivo, nombre, **opciones)
            simulado = parche.start()
            self.addCleanup(parche.stop)
            if nombre == 'generar_respaldo_mysql':
                self.generar = simulado
            elif nombre == 'restaurar_bd_mysql':
                self.restaurar = simulado

    def enviar(self, datos):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(RUTA, datos)

    def mensajes(self, respuesta):
        from django.contrib.messages import get_messages
        return [str(m) for m in get_messages(respuesta.wsgi_request)]

    def subidas(self):
        tmp = os.path.join(self.carpeta, 'backups', 'tmp')
        return os.listdir(tmp) if os.path.isdir(tmp) else []

    def assertNoSeTocoNada(self):
        self.generar.assert_not_called()
        self.restaurar.assert_not_called()
        self.assertEqual(self.subidas(), [])


class ValidacionDelVolcadoTests(RestaurarVistaBase):
    """Punto 1: extensión, tamaño y estructura, antes del respaldo de emergencia."""

    def test_extension_en_mayusculas_pasa(self):
        self.enviar(ayudas.datos_restaurar(ayudas.volcado_subido('RESPALDO.SQL')))
        self.restaurar.assert_called_once()

    def test_txt_se_rechaza(self):
        respuesta = self.enviar(ayudas.datos_restaurar(ayudas.volcado_subido('datos.txt')))
        self.assertNoSeTocoNada()
        self.assertIn('Error: El archivo debe tener extensión .sql', self.mensajes(respuesta))

    def test_sobre_20_mb_se_rechaza_sin_guardarse(self):
        with mock.patch.object(views, 'TOPE_VOLCADO_BYTES', len(VOLCADO_VALIDO) - 1):
            respuesta = self.enviar(ayudas.datos_restaurar())
        self.assertNoSeTocoNada()
        self.assertEqual(self.mensajes(respuesta), [views.TEXTO_VOLCADO_INVALIDO])

    def test_estructura_invalida_se_rechaza(self):
        for nombre, contenido in (
                ('sin_cabecera', VOLCADO_VALIDO.replace(b'-- MySQL dump', b'-- Otro')),
                ('sin_cierre', VOLCADO_VALIDO.replace(b'-- Dump completed', b'-- Cortado')),
                ('drop_database', VOLCADO_VALIDO + b'DROP DATABASE x;\n'),
                ('vacio', b'')):
            with self.subTest(caso=nombre):
                respuesta = self.enviar(ayudas.datos_restaurar(ayudas.volcado_subido('v.sql', contenido)))
                self.assertNoSeTocoNada()
                # Sin seguir la redirección, los mensajes de los subcasos anteriores se acumulan.
                self.assertEqual(self.mensajes(respuesta)[-1], views.TEXTO_VOLCADO_INVALIDO)

    def test_el_mensaje_no_trae_detalles_tecnicos(self):
        self.assertNotIn('mysql', views.TEXTO_VOLCADO_INVALIDO.lower())
        self.assertNotIn('backups', views.TEXTO_VOLCADO_INVALIDO)


class ConfirmacionTests(RestaurarVistaBase):
    """Punto 3 (D3): RESTAURAR exacto, sensible a mayúsculas, con strip() como ELIMINAR (04-10)."""

    def test_sin_confirmacion_no_se_toca_nada(self):
        for valor in (None, '', 'restaurar', 'Restaurar', 'SI', 'RESTAURAR.'):
            with self.subTest(valor=valor):
                datos = ayudas.datos_restaurar()
                if valor is None:
                    datos.pop('confirmacion')
                else:
                    datos['confirmacion'] = valor
                respuesta = self.enviar(datos)
                self.assertNoSeTocoNada()
                self.assertEqual(self.mensajes(respuesta)[-1], views.TEXTO_CONFIRMACION)

    def test_con_espacios_pasa(self):
        self.enviar(ayudas.datos_restaurar(confirmacion='  RESTAURAR '))
        self.restaurar.assert_called_once()

    def test_la_pantalla_pide_escribir_restaurar(self):
        html = self.client.get(RUTA).content.decode()
        self.assertIn('name="confirmacion"', html)
        self.assertIn('<strong>RESTAURAR</strong>', html)
        self.assertIn('for="confirmacion"', html)


class AbortoTests(RestaurarVistaBase):
    """Punto 2: no se restaura si el respaldo de emergencia falla o sale incompleto."""

    def test_respaldo_de_emergencia_vacio_o_sin_cierre_no_restaura(self):
        for contenido in (b'', VOLCADO_VALIDO.replace(b'-- Dump completed', b'-- Cortado')):
            with self.subTest(largo=len(contenido)):
                self.generar.side_effect = ayudas.respaldo_de_emergencia(self.carpeta, contenido)
                with self.assertLogs('pedidos.views', 'ERROR'):
                    respuesta = self.enviar(ayudas.datos_restaurar())
                self.restaurar.assert_not_called()
                self.assertEqual(self.subidas(), [])
                self.assertEqual(self.mensajes(respuesta)[-1],
                                 'Operación cancelada: no se pudo crear el respaldo de seguridad previo, '
                                 'así que la base no se tocó.')

    def test_el_respaldo_de_emergencia_se_pide_con_su_prefijo(self):
        self.enviar(ayudas.datos_restaurar())
        self.generar.assert_called_once_with(prefijo='emergencia')


class ConstanciaTests(RestaurarVistaBase):
    """Punto 4 (D4): server.log antes y después; evento después, con usuario nulo si no existe."""

    def test_lineas_antes_y_despues(self):
        with self.assertLogs('pedidos.views', 'INFO') as registros:
            respuesta = self.enviar(ayudas.datos_restaurar())
        texto = '\n'.join(registros.output)
        self.assertIn('Restauración iniciada', texto)
        self.assertIn('usuario=administracion', texto)
        self.assertIn('archivo=ficticio.sql', texto)
        self.assertIn('emergencia=emergencia_01-01-2026_00-00-00.sql', texto)
        self.assertIn('Restauración terminada: resultado=correcta', texto)
        mensaje = self.mensajes(respuesta)[0]
        self.assertIn('emergencia_01-01-2026_00-00-00.sql', mensaje)  # D5: el mensaje lo nombra

    def test_falla_deja_linea_de_resultado(self):
        self.restaurar.side_effect = RuntimeError('mysql falló')
        with self.assertLogs('pedidos.views', 'INFO') as registros:
            self.enviar(ayudas.datos_restaurar())
        self.assertIn('Restauración terminada: resultado=fallida', '\n'.join(registros.output))

    def test_evento_con_su_usuario(self):
        self.enviar(ayudas.datos_restaurar())
        evento = RegistroEvento.objects.get(tipo='restauracion_ejecutada')
        self.assertEqual(evento.usuario_id, self.usuario.pk)

    def test_evento_con_usuario_nulo_si_el_volcado_no_lo_trae(self):
        def restaurar_sin_el_usuario(ruta):
            User.objects.filter(pk=self.usuario.pk).delete()
        self.restaurar.side_effect = restaurar_sin_el_usuario
        self.enviar(ayudas.datos_restaurar())
        evento = RegistroEvento.objects.get(tipo='restauracion_ejecutada')
        self.assertIsNone(evento.usuario_id)


class SubidaHuerfanaTests(RestaurarVistaBase):
    """Punto 6: la subida de backups/tmp/ se borra siempre."""

    def test_restauracion_fallida_no_deja_la_subida(self):
        self.restaurar.side_effect = RuntimeError('mysql falló')
        with self.assertLogs('pedidos.views', 'ERROR'):
            self.enviar(ayudas.datos_restaurar())
        self.assertEqual(self.subidas(), [])

    def test_restauracion_correcta_no_deja_la_subida(self):
        self.enviar(ayudas.datos_restaurar())
        self.assertEqual(self.subidas(), [])


class PantallaDeRespaldosTests(RestaurarVistaBase):
    """D5: la pantalla de respaldos marca el de emergencia."""

    def test_marca_el_respaldo_de_emergencia(self):
        ayudas.respaldo_de_emergencia(self.carpeta)()
        html = self.client.get('/base_datos/respaldar_bd/').content.decode()
        self.assertIn('emergencia_01-01-2026_00-00-00.sql', html)
        self.assertIn('Emergencia', html)
