import sys

from django.contrib.auth import get_user_model
from django.test import TestCase


class RobotsTxtTests(TestCase):
    def test_responde_sin_sesion_en_texto_plano(self):
        respuesta = self.client.get('/robots.txt')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta['Content-Type'].startswith('text/plain'))
        self.assertIn('Disallow: /', respuesta.content.decode())

    def test_acepta_head(self):
        respuesta = self.client.head('/robots.txt')
        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta['Content-Type'].startswith('text/plain'))

    def test_rechaza_post(self):
        self.assertEqual(self.client.post('/robots.txt').status_code, 405)


class ListaPagosRutaTests(TestCase):
    def setUp(self):
        usuario = get_user_model().objects.create_user('prueba', password='clave-prueba-123')
        self.client.force_login(usuario)

    def test_ruta_con_barra_responde(self):
        self.assertEqual(self.client.get('/pagos/lista/').status_code, 200)

    def test_ruta_sin_barra_redirige(self):
        respuesta = self.client.get('/pagos/lista')
        self.assertRedirects(respuesta, '/pagos/lista/', status_code=301, fetch_redirect_response=False)


class CargaDiferidaWeasyprintTests(TestCase):
    def test_vistas_no_importan_weasyprint_al_cargar(self):
        import importlib
        import pedidos.views
        sys.modules.pop('weasyprint', None)
        importlib.reload(pedidos.views)
        self.assertNotIn('weasyprint', sys.modules)


class RegistroEventoTests(TestCase):
    """Iteración 01-01: purga por retención y conservación de eventos al borrar usuarios."""

    def crear_evento(self, momento, usuario=None, entidad_id=1):
        from pedidos.models import RegistroEvento
        return RegistroEvento.objects.create(
            momento=momento, tipo='pedido_creado', usuario=usuario,
            entidad='pedido', entidad_id=entidad_id, resumen=f'Pedido #{entidad_id} creado',
        )

    def test_purga_elimina_solo_los_antiguos(self):
        from datetime import timedelta
        from django.utils import timezone
        from pedidos.eventos import purgar_eventos
        from pedidos.models import RegistroEvento

        ahora = timezone.now()
        self.crear_evento(ahora - timedelta(days=400), entidad_id=1)
        self.crear_evento(ahora - timedelta(days=365, seconds=1), entidad_id=2)
        reciente = self.crear_evento(ahora - timedelta(days=364), entidad_id=3)
        de_hoy = self.crear_evento(ahora, entidad_id=4)

        self.assertEqual(purgar_eventos(dias=365, ahora=ahora), 2)
        restantes = set(RegistroEvento.objects.values_list('pk', flat=True))
        self.assertEqual(restantes, {reciente.pk, de_hoy.pk})

    def test_purga_rechaza_retencion_menor_a_un_dia(self):
        from pedidos.eventos import purgar_eventos
        with self.assertRaises(ValueError):
            purgar_eventos(dias=0)

    def test_orden_purgar_registros_informa_las_filas_eliminadas(self):
        from datetime import timedelta
        from io import StringIO
        from django.core.management import call_command
        from django.utils import timezone
        from pedidos.models import RegistroEvento

        self.crear_evento(timezone.now() - timedelta(days=500))
        self.crear_evento(timezone.now())
        salida = StringIO()
        call_command('purgar_registros', stdout=salida)
        self.assertIn('Eventos eliminados: 1 ', salida.getvalue())
        self.assertEqual(RegistroEvento.objects.count(), 1)

    def test_eliminar_usuario_conserva_sus_eventos(self):
        from django.utils import timezone
        from pedidos.models import RegistroEvento

        usuario = get_user_model().objects.create_user('auditado', password='clave-prueba-123')
        evento = self.crear_evento(timezone.now(), usuario=usuario)
        usuario.delete()
        evento.refresh_from_db()
        self.assertIsNone(evento.usuario)
        self.assertEqual(RegistroEvento.objects.count(), 1)
