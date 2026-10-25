"""Retención y purga del registro de eventos de negocio (iteración 01-01).

El servicio que escribe eventos llega en 01-02. La purga la ejecuta a mano la orden
`purgar_registros` hasta que la orden de mantención diaria (06-02) la absorba.
"""
from datetime import timedelta

from django.utils import timezone

from .models import RegistroEvento

# Días de retención: 365, confirmados por el desarrollador el 2026-10-25 (bitacora-01-01).
RETENCION_EVENTOS_DIAS = 365


def limite_retencion(dias=None, ahora=None):
    """Instante desde el cual los eventos se conservan; los anteriores se purgan."""
    dias = RETENCION_EVENTOS_DIAS if dias is None else dias
    if dias < 1:
        raise ValueError('La retención debe ser de al menos 1 día.')
    return (ahora or timezone.now()) - timedelta(days=dias)


def purgar_eventos(dias=None, ahora=None):
    """Elimina los eventos más antiguos que la retención y devuelve cuántos eliminó."""
    limite = limite_retencion(dias, ahora)
    eliminados, _ = RegistroEvento.objects.filter(momento__lt=limite).delete()
    return eliminados
