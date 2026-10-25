"""Registro de eventos de negocio: purga y usuarios (01-01) y servicio de eventos (01-02)."""
from datetime import timedelta
from io import StringIO
from unittest import mock

from django.contrib.auth.models import AnonymousUser
from django.core.management import call_command
from django.db import transaction
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from pedidos.eventos import purgar_eventos, registrar_evento
from pedidos.models import RegistroEvento

from .factorias import crear_evento, crear_pago, crear_pedido, crear_usuario

# Consultas de /pagos/lista/ con 2 pagos, medidas en 01-02 antes de instalar el servicio.
# 01-04 no debe cambiar este número: el servicio nunca se llama en lecturas.
CONSULTAS_LISTA_PAGOS = 4


class ServicioEventosTests(TestCase):
    def test_registra_despues_de_confirmar(self):
        usuario = crear_usuario()
        with self.captureOnCommitCallbacks(execute=False) as pendientes:
            registrar_evento('pedido_creado', usuario, 'pedido', 7, 'Pedido #7 creado')
            self.assertEqual(RegistroEvento.objects.count(), 0)  # aún no se confirma
        self.assertEqual(len(pendientes), 1)
        pendientes[0]()
        evento = RegistroEvento.objects.get()
        self.assertEqual((evento.tipo, evento.usuario, evento.entidad, evento.entidad_id),
                         ('pedido_creado', usuario, 'pedido', 7))

    def test_anonimo_y_sistema_quedan_sin_usuario(self):
        with self.captureOnCommitCallbacks(execute=True):
            registrar_evento('acceso_fallido', AnonymousUser(), resumen='Usuario intentado: x')
            registrar_evento('respaldo_generado', None, resumen='Orden de mantención')
        self.assertEqual(list(RegistroEvento.objects.values_list('usuario', flat=True)), [None, None])

    def test_resumen_largo_se_recorta(self):
        with self.captureOnCommitCallbacks(execute=True):
            registrar_evento('pedido_modificado', resumen='x' * 400)
        self.assertEqual(len(RegistroEvento.objects.get().resumen), 255)

    def test_fallo_al_escribir_no_lanza_y_queda_en_el_registro(self):
        with mock.patch.object(RegistroEvento.objects, 'create', side_effect=RuntimeError('disco lleno')):
            with self.assertLogs('pedidos.eventos', 'ERROR') as capturado:
                with self.captureOnCommitCallbacks(execute=True):
                    resultado = registrar_evento('pago_registrado', entidad='pago', entidad_id=1)
        self.assertIsNone(resultado)
        self.assertIn('No se pudo escribir el evento pago_registrado', capturado.output[0])
        self.assertIsNotNone(capturado.records[0].exc_info)  # con traza
        self.assertEqual(RegistroEvento.objects.count(), 0)

    def test_fallo_al_programar_no_lanza(self):
        with mock.patch('pedidos.eventos.transaction.on_commit', side_effect=RuntimeError('sin conexión')):
            with self.assertLogs('pedidos.eventos', 'ERROR') as capturado:
                registrar_evento('pedido_eliminado', entidad='pedido', entidad_id=1)
        self.assertIn('No se pudo programar el evento pedido_eliminado', capturado.output[0])

    def test_listado_no_usa_el_servicio_ni_suma_consultas(self):
        pedido = crear_pedido()
        crear_pago(pedido)
        crear_pago(pedido)
        self.client.force_login(crear_usuario())
        with mock.patch('pedidos.eventos.registrar_evento') as servicio:
            with self.assertNumQueries(CONSULTAS_LISTA_PAGOS):
                self.assertEqual(self.client.get('/pagos/lista/').status_code, 200)
        servicio.assert_not_called()
        self.assertEqual(RegistroEvento.objects.count(), 0)


class ServicioEventosTransaccionTests(TransactionTestCase):
    """Con transacciones reales (sin la transacción envolvente de TestCase)."""

    def test_transaccion_revertida_no_deja_evento(self):
        with self.assertRaises(ValueError):
            with transaction.atomic():
                registrar_evento('pedido_creado', entidad='pedido', entidad_id=1)
                raise ValueError('la operación falló')
        self.assertEqual(RegistroEvento.objects.count(), 0)

    def test_transaccion_confirmada_deja_evento(self):
        with transaction.atomic():
            registrar_evento('pedido_creado', entidad='pedido', entidad_id=2)
            self.assertEqual(RegistroEvento.objects.count(), 0)
        self.assertEqual(RegistroEvento.objects.count(), 1)

    def test_error_real_de_la_base_no_corta_la_peticion(self):
        usuario_inexistente = crear_usuario()
        usuario_inexistente.delete()
        usuario_inexistente.pk = 999_999  # la clave foránea rechaza la fila
        with self.assertLogs('pedidos.eventos', 'ERROR') as capturado:
            registrar_evento('pedido_creado', usuario_inexistente, 'pedido', 3)
        self.assertIn('IntegrityError', capturado.output[0])
        self.assertEqual(RegistroEvento.objects.count(), 0)
        # La conexión sigue sana y la aplicación responde.
        self.assertEqual(self.client.get('/robots.txt').status_code, 200)


class RegistroEventoTests(TestCase):
    def test_purga_elimina_solo_los_antiguos(self):
        ahora = timezone.now()
        crear_evento(ahora - timedelta(days=400), entidad_id=1)
        crear_evento(ahora - timedelta(days=365, seconds=1), entidad_id=2)
        reciente = crear_evento(ahora - timedelta(days=364), entidad_id=3)
        de_hoy = crear_evento(ahora, entidad_id=4)

        self.assertEqual(purgar_eventos(dias=365, ahora=ahora), 2)
        restantes = set(RegistroEvento.objects.values_list('pk', flat=True))
        self.assertEqual(restantes, {reciente.pk, de_hoy.pk})

    def test_purga_rechaza_retencion_menor_a_un_dia(self):
        with self.assertRaises(ValueError):
            purgar_eventos(dias=0)

    def test_orden_purgar_registros_informa_las_filas_eliminadas(self):
        crear_evento(timezone.now() - timedelta(days=500))
        crear_evento(timezone.now())
        salida = StringIO()
        call_command('purgar_registros', stdout=salida)
        self.assertIn('Eventos eliminados: 1 ', salida.getvalue())
        self.assertEqual(RegistroEvento.objects.count(), 1)

    def test_eliminar_usuario_conserva_sus_eventos(self):
        usuario = crear_usuario('auditado')
        evento = crear_evento(usuario=usuario)
        usuario.delete()
        evento.refresh_from_db()
        self.assertIsNone(evento.usuario)
        self.assertEqual(RegistroEvento.objects.count(), 1)
