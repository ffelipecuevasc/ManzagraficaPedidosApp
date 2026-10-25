"""Registro de eventos de negocio: servicio (01-02), retención y purga (01-01).

Diseño (RDA-013, bitacora-01-02):
- Solo se llama desde los puntos del inventario de 01-04, nunca en lecturas ordinarias.
- El evento se escribe con `transaction.on_commit`: si la operación se revierte, no queda.
- `registrar_evento` nunca lanza una excepción hacia quien lo llama.
- Un evento por acción del usuario (01-04): una operación compuesta (pedido con abono,
  conversión, restauración con respaldo previo) deja una sola fila y lo dice en el resumen.
- Eventos del sistema (por ejemplo, la orden de mantención de 06-02): usuario nulo y resumen
  que empieza con «Origen: <orden o proceso> ·». Un acceso fallido también lleva usuario nulo,
  pero su origen lo identifica el tipo `acceso_fallido`.

La purga la ejecuta a mano la orden `purgar_registros` hasta que la orden de mantención
diaria (06-02) la absorba.
"""
import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import RegistroEvento

logger = logging.getLogger(__name__)
_LARGO_RESUMEN = RegistroEvento._meta.get_field('resumen').max_length


def registrar_evento(tipo, usuario=None, entidad='', entidad_id=None, resumen=''):
    """Programa el registro de un evento para cuando la transacción en curso se confirme.

    Sin transacción abierta (modo autocommit) se escribe de inmediato. `usuario` puede ser
    nulo (eventos del sistema) o anónimo (se guarda como nulo). El resumen lleva solo
    identificadores: nada de nombres, teléfonos, montos ni contraseñas.
    """
    try:
        datos = {
            'tipo': tipo,
            'usuario_id': usuario.pk if usuario is not None and usuario.is_authenticated else None,
            'entidad': entidad,
            'entidad_id': entidad_id,
            'resumen': str(resumen)[:_LARGO_RESUMEN],
            'momento': timezone.now(),
        }
        transaction.on_commit(lambda: _escribir_evento(datos))
    except Exception:  # noqa: BLE001
        # Captura amplia permitida (AGENTS.md, regla 4): el servicio de registro nunca puede
        # hacer fallar una petición. El problema queda en error.log con su traza.
        logger.exception('No se pudo programar el evento %s', tipo)


def _escribir_evento(datos):
    try:
        RegistroEvento.objects.create(**datos)
    except Exception:  # noqa: BLE001
        # Captura amplia permitida (AGENTS.md, regla 4): la escritura del evento ocurre después
        # de confirmar la operación y su fallo no puede afectar la respuesta al usuario.
        logger.exception('No se pudo escribir el evento %s', datos.get('tipo'))

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
