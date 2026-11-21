"""Señales de acceso que registran eventos de negocio (iteración 01-04) y alimentan el límite
de intentos (iteración 04-08).

Se conectan en `PedidosConfig.ready()`.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

from . import limite_acceso
from .eventos import registrar_evento


@receiver(user_logged_in, dispatch_uid='pedidos_acceso_exitoso')
def acceso_exitoso(sender, request, user, **kwargs):
    registrar_evento('acceso_exitoso', user, 'usuario', user.pk, f'Acceso de usuario #{user.pk}')


@receiver(user_login_failed, dispatch_uid='pedidos_acceso_fallido')
def acceso_fallido(sender, credentials, request=None, **kwargs):
    # Decisión del 2026-10-25: el nombre solo se guarda si existe como usuario, y se guarda el
    # registrado en la base, no lo escrito. Así una contraseña tecleada por error en el campo
    # de usuario nunca queda en la tabla ni en los respaldos. La contraseña nunca se usa.
    intentado = str(credentials.get('username', ''))[:150]
    existente = (get_user_model().objects.filter(username=intentado)
                 .values_list('username', flat=True).first() if intentado else None)
    resumen = f'Usuario intentado: {existente}' if existente else 'Usuario intentado: usuario desconocido'
    registrar_evento('acceso_fallido', None, 'usuario', None, resumen)


@receiver(user_login_failed, dispatch_uid='pedidos_limite_acceso_fallo')
def contar_fallo(sender, credentials, request=None, **kwargs):
    # 04-08 (D2): solo cuentan los intentos que llegan por un formulario web (con petición).
    # Un intento bloqueado no llega aquí: el formulario corta antes de authenticate().
    if request is None:
        return
    intentado = credentials.get('username', '')
    empezados = limite_acceso.registrar_fallo(request, intentado)
    if not empezados:
        return
    # Un evento por bloqueo, con usuario nulo y sin la dirección ni el nombre tecleado (D4).
    # Solo el identificador del usuario si existe y el bloqueo es por usuario.
    usuario_id = None
    if 'usuario' in empezados:
        usuario_id = (get_user_model().objects.filter(username=str(intentado)[:150])
                      .values_list('pk', flat=True).first())
    resumen = f'Bloqueo de {limite_acceso.BLOQUEO_SEGUNDOS // 60} minutos por {" y ".join(empezados)}'
    registrar_evento('acceso_bloqueado', None, 'usuario', usuario_id, resumen)


@receiver(user_logged_in, dispatch_uid='pedidos_limite_acceso_exito')
def reiniciar_contador(sender, request, user, **kwargs):
    # 04-08 (D2): un acceso correcto borra el contador del usuario, no el de la dirección.
    limite_acceso.reiniciar_usuario(user.get_username())
