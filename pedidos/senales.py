"""Señales de acceso que registran eventos de negocio (iteración 01-04).

Se conectan en `PedidosConfig.ready()`.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

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
