"""Límite de intentos de acceso (iteración 04-08, D1 a D4; AUD-03-004).

La caché local persiste entre pruebas (no la vacía la transacción de `TestCase`): cada prueba
la vacía en `setUp`. Los límites se leen de las constantes; los eventos se escriben con
`on_commit`, por eso los POST van dentro de `captureOnCommitCallbacks(execute=True)`.
"""
import time
from unittest import mock

from django.core.cache import caches
from django.test import RequestFactory, TestCase, override_settings

from pedidos import limite_acceso
from pedidos.limite_acceso import (
    BLOQUEO_SEGUNDOS, FALLOS_POR_DIRECCION_DEFECTO, FALLOS_POR_USUARIO,
)
from pedidos.models import RegistroEvento

from . import factorias

LOGIN = '/accounts/login/'
LOGIN_ADMIN = '/acceso-manzagrafica-admin/login/'
CLAVE = 'clave-correcta-123'
# Texto escrito por el agente en la 04-08 (no aprobado aún por el desarrollador): literal a propósito.
TEXTO_BLOQUEO = 'Hubo demasiados intentos fallidos. Espera 15 minutos y vuelve a intentarlo.'


class LimiteAccesoBase(TestCase):
    def setUp(self):
        caches['acceso'].clear()
        self.addCleanup(caches['acceso'].clear)
        self.usuario = factorias.crear_usuario('recepcion', password=CLAVE)

    def intentar(self, username='recepcion', password='equivocada', ruta=LOGIN, direccion='10.0.0.1', **extra):
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(ruta, {'username': username, 'password': password},
                                    REMOTE_ADDR=direccion, **extra)

    def fallar(self, veces, **kwargs):
        for _ in range(veces):
            self.intentar(**kwargs)

    def assertBloqueado(self, respuesta):
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, TEXTO_BLOQUEO)

    def assertNoBloqueado(self, respuesta):
        self.assertNotContains(respuesta, TEXTO_BLOQUEO, status_code=respuesta.status_code)


class BloqueoPorUsuarioTests(LimiteAccesoBase):
    def test_n_fallos_bloquean_y_el_siguiente_no_llama_a_authenticate(self):
        self.fallar(FALLOS_POR_USUARIO)
        with mock.patch('django.contrib.auth.forms.authenticate') as autenticar:
            respuesta = self.intentar(password=CLAVE)  # incluso con la contraseña correcta
        autenticar.assert_not_called()
        self.assertBloqueado(respuesta)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_n_menos_uno_fallos_no_bloquean(self):
        self.fallar(FALLOS_POR_USUARIO - 1)
        respuesta = self.intentar(password=CLAVE)
        self.assertEqual(respuesta.status_code, 302)

    def test_mayusculas_y_espacios_suman_al_mismo_contador(self):
        # La colación utf8mb4_unicode_ci no distingue mayúsculas: «RECEPCION» entra a la misma cuenta.
        variantes = ['recepcion', 'RECEPCION', ' Recepcion ', 'recepcioN', 'ReCePcIoN']
        for nombre in variantes[:FALLOS_POR_USUARIO]:
            self.intentar(username=nombre)
        self.assertBloqueado(self.intentar(username='recepcion', password=CLAVE))

    def test_el_bloqueo_por_usuario_vale_desde_otra_direccion(self):
        self.fallar(FALLOS_POR_USUARIO, direccion='10.0.0.1')
        self.assertBloqueado(self.intentar(password=CLAVE, direccion='10.0.0.2'))

    def test_acceso_correcto_reinicia_el_contador_del_usuario(self):
        self.fallar(FALLOS_POR_USUARIO - 1)
        self.assertEqual(self.intentar(password=CLAVE).status_code, 302)
        self.client.logout()
        self.fallar(FALLOS_POR_USUARIO - 1)
        self.assertEqual(self.intentar(password=CLAVE).status_code, 302)

    def test_sin_fuga_mismo_mensaje_con_usuario_inexistente(self):
        self.fallar(FALLOS_POR_USUARIO, username='nadie-con-este-nombre')
        con_inexistente = self.intentar(username='nadie-con-este-nombre')
        caches['acceso'].clear()
        self.fallar(FALLOS_POR_USUARIO)
        con_existente = self.intentar()
        self.assertBloqueado(con_inexistente)
        self.assertBloqueado(con_existente)


class EventoBloqueoTests(LimiteAccesoBase):
    def test_un_solo_evento_al_empezar_el_bloqueo_y_ninguno_despues(self):
        self.fallar(FALLOS_POR_USUARIO)
        bloqueos = RegistroEvento.objects.filter(tipo='acceso_bloqueado')
        self.assertEqual(bloqueos.count(), 1)
        total = RegistroEvento.objects.count()
        self.fallar(3)
        self.assertEqual(RegistroEvento.objects.count(), total)
        self.assertEqual(RegistroEvento.objects.filter(tipo='acceso_fallido').count(), FALLOS_POR_USUARIO)

    def test_el_evento_no_guarda_direccion_ni_nombre_tecleado(self):
        self.fallar(FALLOS_POR_USUARIO, username='Nombre-Tecleado', direccion='10.9.8.7')
        evento = RegistroEvento.objects.get(tipo='acceso_bloqueado')
        self.assertIsNone(evento.usuario)
        self.assertIsNone(evento.entidad_id)
        self.assertNotIn('10.9.8.7', evento.resumen)
        self.assertNotIn('Nombre-Tecleado', evento.resumen)
        self.assertNotIn('nombre-tecleado', evento.resumen)

    def test_el_evento_lleva_el_identificador_del_usuario_existente(self):
        self.fallar(FALLOS_POR_USUARIO)
        evento = RegistroEvento.objects.get(tipo='acceso_bloqueado')
        self.assertEqual((evento.usuario, evento.entidad, evento.entidad_id),
                         (None, 'usuario', self.usuario.pk))
        self.assertNotIn('recepcion', evento.resumen)


class BloqueoPorDireccionTests(LimiteAccesoBase):
    def test_nombres_distintos_desde_una_direccion_bloquean_la_direccion(self):
        for i in range(FALLOS_POR_DIRECCION_DEFECTO):
            self.intentar(username=f'inventado-{i}', direccion='10.0.0.5')
        self.assertBloqueado(self.intentar(password=CLAVE, direccion='10.0.0.5'))
        self.assertEqual(self.intentar(password=CLAVE, direccion='10.0.0.6').status_code, 302)

    @override_settings(ACCESO_FALLOS_POR_DIRECCION=0)
    def test_cero_apaga_solo_el_contador_por_direccion(self):
        for i in range(FALLOS_POR_DIRECCION_DEFECTO + 5):
            self.intentar(username=f'inventado-{i}', direccion='10.0.0.5')
        self.assertEqual(self.intentar(password=CLAVE, direccion='10.0.0.5').status_code, 302)
        self.client.logout()
        self.fallar(FALLOS_POR_USUARIO, direccion='10.0.0.5')
        self.assertBloqueado(self.intentar(password=CLAVE, direccion='10.0.0.5'))

    @override_settings(ACCESO_FALLOS_POR_DIRECCION=3)
    def test_un_valor_pequeno_bloquea_antes(self):
        for i in range(3):
            self.intentar(username=f'inventado-{i}', direccion='10.0.0.5')
        self.assertBloqueado(self.intentar(password=CLAVE, direccion='10.0.0.5'))


class VencimientoYRecargaTests(LimiteAccesoBase):
    def test_al_vencer_el_bloqueo_se_puede_entrar(self):
        self.fallar(FALLOS_POR_USUARIO)
        despues = time.time() + BLOQUEO_SEGUNDOS + 1
        with mock.patch('django.core.cache.backends.locmem.time') as reloj:
            reloj.time.return_value = despues
            respuesta = self.intentar(password=CLAVE)
        self.assertEqual(respuesta.status_code, 302)

    def test_vaciar_la_cache_equivale_a_recargar_y_desbloquea(self):
        self.fallar(FALLOS_POR_USUARIO)
        caches['acceso'].clear()
        self.assertEqual(self.intentar(password=CLAVE).status_code, 302)


class AdminTests(LimiteAccesoBase):
    def setUp(self):
        super().setUp()
        self.admin = factorias.crear_superusuario('jefatura', password=CLAVE)

    def test_el_admin_bloquea_igual(self):
        self.fallar(FALLOS_POR_USUARIO, username='jefatura', ruta=LOGIN_ADMIN)
        with mock.patch('django.contrib.auth.forms.authenticate') as autenticar:
            respuesta = self.intentar(username='jefatura', password=CLAVE, ruta=LOGIN_ADMIN)
        autenticar.assert_not_called()
        self.assertBloqueado(respuesta)

    def test_los_contadores_se_comparten_con_accounts(self):
        self.fallar(FALLOS_POR_USUARIO - 2, username='jefatura', ruta=LOGIN_ADMIN)
        self.fallar(2, username='jefatura', ruta=LOGIN)
        self.assertBloqueado(self.intentar(username='jefatura', password=CLAVE, ruta=LOGIN_ADMIN))


class DireccionRealTests(TestCase):
    def setUp(self):
        self.fabrica = RequestFactory()

    def peticion(self, xff=None, remota='10.0.0.1'):
        extra = {'REMOTE_ADDR': remota}
        if xff is not None:
            extra['HTTP_X_FORWARDED_FOR'] = xff
        return self.fabrica.get('/', **extra)

    @override_settings(ACCESO_PROXIES_CONFIABLES=0)
    def test_sin_proxies_usa_remote_addr_e_ignora_la_cabecera(self):
        self.assertEqual(limite_acceso.direccion_cliente(self.peticion('1.2.3.4')), '10.0.0.1')

    @override_settings(ACCESO_PROXIES_CONFIABLES=1)
    def test_con_un_proxy_usa_el_ultimo_elemento_e_ignora_lo_falsificado(self):
        self.assertEqual(limite_acceso.direccion_cliente(self.peticion('6.6.6.6, 203.0.113.9')), '203.0.113.9')

    @override_settings(ACCESO_PROXIES_CONFIABLES=2)
    def test_con_dos_proxies_usa_el_penultimo(self):
        self.assertEqual(
            limite_acceso.direccion_cliente(self.peticion('6.6.6.6, 203.0.113.9, 198.51.100.1')), '203.0.113.9')

    @override_settings(ACCESO_PROXIES_CONFIABLES=2)
    def test_cabecera_con_menos_elementos_vuelve_a_remote_addr(self):
        self.assertEqual(limite_acceso.direccion_cliente(self.peticion('203.0.113.9')), '10.0.0.1')

    @override_settings(ACCESO_PROXIES_CONFIABLES=1)
    def test_valor_invalido_o_ausente_vuelve_a_remote_addr(self):
        self.assertEqual(limite_acceso.direccion_cliente(self.peticion('no-es-una-ip')), '10.0.0.1')
        self.assertEqual(limite_acceso.direccion_cliente(self.peticion()), '10.0.0.1')

    @override_settings(ACCESO_PROXIES_CONFIABLES=1)
    def test_ipv6_valida(self):
        self.assertEqual(limite_acceso.direccion_cliente(self.peticion('2001:db8::1')), '2001:db8::1')


class FalsificacionTests(LimiteAccesoBase):
    @override_settings(ACCESO_PROXIES_CONFIABLES=1, ACCESO_FALLOS_POR_DIRECCION=3)
    def test_cambiar_la_cabecera_a_la_izquierda_no_evita_el_bloqueo(self):
        for i in range(3):
            self.intentar(username=f'inventado-{i}', direccion='10.0.0.1',
                          HTTP_X_FORWARDED_FOR=f'1.1.1.{i}, 203.0.113.9')
        self.assertBloqueado(self.intentar(password=CLAVE, HTTP_X_FORWARDED_FOR='9.9.9.9, 203.0.113.9'))


class RedireccionTests(TestCase):
    def test_con_sesion_redirige_al_panel(self):
        self.client.force_login(factorias.crear_usuario('recepcion'))
        respuesta = self.client.get(LOGIN)
        self.assertRedirects(respuesta, '/', fetch_redirect_response=False)

    def test_sin_sesion_muestra_el_formulario(self):
        respuesta = self.client.get(LOGIN)
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'id="form-acceso"')
