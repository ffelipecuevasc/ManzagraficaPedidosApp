"""Consulta de eventos en el admin de Django: solo lectura y solo superusuarios (01-05)."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth.models import Permission
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from pedidos.models import RegistroEvento

from . import factorias

LISTADO = reverse('admin:pedidos_registroevento_changelist')  # el admin no vive en /admin/


def ids_en_listado(respuesta):
    return sorted(evento.pk for evento in respuesta.context['cl'].result_list)


class AdminEventosSuperusuarioTests(TestCase):
    def setUp(self):
        self.admin = factorias.crear_superusuario()
        self.client.force_login(self.admin)

    def test_listado_y_busqueda_por_identificador_de_entidad(self):
        e1 = factorias.crear_evento(entidad='pedido', entidad_id=12)
        e2 = factorias.crear_evento(tipo='pedido_modificado', entidad='pedido', entidad_id=12)
        factorias.crear_evento(entidad='pedido', entidad_id=120)  # contiene «12», no debe salir
        factorias.crear_evento(entidad='pago', entidad_id=7)
        respuesta = self.client.get(LISTADO)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.context['cl'].result_list), 4)

        respuesta = self.client.get(LISTADO, {'q': '12'})
        self.assertEqual(ids_en_listado(respuesta), sorted([e1.pk, e2.pk]))

    def test_busqueda_no_numerica_no_falla(self):
        factorias.crear_evento(entidad_id=5)
        respuesta = self.client.get(LISTADO, {'q': 'abc'})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(ids_en_listado(respuesta), [])

    def test_filtros_por_tipo_y_por_usuario(self):
        otro = factorias.crear_usuario()
        creado = factorias.crear_evento(tipo='pedido_creado', usuario=self.admin)
        pago = factorias.crear_evento(tipo='pago_registrado', usuario=otro)
        factorias.crear_evento(tipo='respaldo_generado', usuario=None)

        respuesta = self.client.get(LISTADO, {'tipo__exact': 'pago_registrado'})
        self.assertEqual(ids_en_listado(respuesta), [pago.pk])

        respuesta = self.client.get(LISTADO, {'usuario__id__exact': self.admin.pk})
        self.assertEqual(ids_en_listado(respuesta), [creado.pk])

    def test_filtro_por_fecha_usa_el_dia_de_chile(self):
        # 23:30 de Chile del día anterior es «hoy» en UTC durante 3 horas: no debe contarse como hoy.
        hoy_chile = timezone.localdate()
        anoche = datetime.combine(hoy_chile - timedelta(days=1), datetime.min.time().replace(hour=23, minute=30),
                                  tzinfo=ZoneInfo('America/Santiago'))
        de_anoche = factorias.crear_evento(momento=anoche)
        de_hoy = factorias.crear_evento(momento=timezone.now())
        inicio = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
        respuesta = self.client.get(LISTADO, {
            'momento__gte': inicio.strftime('%Y-%m-%d %H:%M:%S%z'),
            'momento__lt': (inicio + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S%z'),
        })
        self.assertIn(de_hoy.pk, ids_en_listado(respuesta))
        self.assertNotIn(de_anoche.pk, ids_en_listado(respuesta))

    def test_fecha_en_hora_de_chile_con_su_zona(self):
        momento = datetime(2026, 7, 15, 18, 5, 9, tzinfo=ZoneInfo('UTC'))  # invierno: UTC-4
        evento = factorias.crear_evento(momento=momento)
        respuesta = self.client.get(f'{LISTADO}{evento.pk}/change/')
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, '15-07-2026 14:05:09 (UTC-0400)')
        respuesta = self.client.get(LISTADO)
        self.assertContains(respuesta, '15-07-2026 14:05:09 (UTC-0400)')

    def test_sin_agregar_modificar_ni_eliminar(self):
        evento = factorias.crear_evento()
        self.assertEqual(self.client.get(f'{LISTADO}add/').status_code, 403)
        self.assertEqual(self.client.get(f'{LISTADO}{evento.pk}/delete/').status_code, 403)

        detalle = self.client.get(f'{LISTADO}{evento.pk}/change/')
        self.assertEqual(detalle.status_code, 200)
        self.assertNotContains(detalle, 'name="_save"')
        self.assertNotContains(detalle, '/delete/')
        # Un POST al detalle no cambia nada.
        self.client.post(f'{LISTADO}{evento.pk}/change/', {'resumen': 'alterado'})
        evento.refresh_from_db()
        self.assertNotEqual(evento.resumen, 'alterado')

        listado = self.client.get(LISTADO)
        self.assertIsNone(listado.context['action_form'])  # sin acciones: tampoco «eliminar seleccionados»
        self.assertNotContains(listado, 'delete_selected')
        self.assertNotContains(listado, f'{LISTADO}add/')

    def test_consultas_no_crecen_con_las_filas(self):
        usuarios = [factorias.crear_usuario() for _ in range(3)]
        factorias.crear_evento(usuario=usuarios[0])

        def contar():
            with CaptureQueriesContext(connection) as consultas:
                self.assertEqual(self.client.get(LISTADO).status_code, 200)
            return len(consultas)

        con_una = contar()
        for i in range(19):
            factorias.crear_evento(usuario=usuarios[i % 3], entidad_id=i + 2)
        self.assertEqual(RegistroEvento.objects.count(), 20)
        with self.assertNumQueries(con_una):
            self.assertEqual(len(self.client.get(LISTADO).context['cl'].result_list), 20)


class AdminEventosSinSuperusuarioTests(TestCase):
    def test_staff_sin_superusuario_no_ve_el_modelo_aunque_tenga_permisos(self):
        staff = factorias.crear_usuario(is_staff=True)
        staff.user_permissions.set(Permission.objects.filter(codename__endswith='_registroevento'))
        evento = factorias.crear_evento()
        self.client.force_login(staff)

        indice = self.client.get(reverse('admin:index'))
        self.assertEqual(indice.status_code, 200)
        self.assertNotContains(indice, 'registroevento')
        self.assertEqual(self.client.get(LISTADO).status_code, 403)
        self.assertEqual(self.client.get(f'{LISTADO}{evento.pk}/change/').status_code, 403)

    def test_usuario_sin_staff_es_enviado_al_acceso(self):
        self.client.force_login(factorias.crear_usuario())
        respuesta = self.client.get(LISTADO)
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta['Location'].startswith(reverse('admin:login')))
