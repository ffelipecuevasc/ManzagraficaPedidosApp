"""Señales de acceso que registran eventos de negocio (iteración 01-04).

Se conectan en `PedidosConfig.ready()`.
"""
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

from .eventos import registrar_evento


@receiver(user_logged_in, dispatch_uid='pedidos_acceso_exitoso')
def acceso_exitoso(sender, request, user, **kwargs):
    registrar_evento('acceso_exitoso', user, 'usuario', user.pk, f'Acceso de usuario #{user.pk}')


@receiver(user_login_failed, dispatch_uid='pedidos_acceso_fallido')
def acceso_fallido(sender, credentials, request=None, **kwargs):
    # Solo el nombre intentado; Django ya enmascara la contraseña y aquí no se usa.
    intentado = str(credentials.get('username', ''))[:150]
    registrar_evento('acceso_fallido', None, 'usuario', None, f'Usuario intentado: {intentado}')
