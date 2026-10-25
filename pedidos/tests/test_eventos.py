"""Registro de eventos de negocio: purga por retención y conservación al borrar usuarios (01-01)."""
from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from pedidos.eventos import purgar_eventos
from pedidos.models import RegistroEvento

from .factorias import crear_evento, crear_usuario


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
