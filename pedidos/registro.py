"""Servicio de registro de la aplicación (iteración 01-02, RDA-013).

Convención del proyecto: cada módulo usa su propio registrador,
    logger = logging.getLogger(__name__)
y, dentro de una vista, pasa la petición para que la línea lleve su contexto:
    logger.exception('No se pudo eliminar el pago', extra={'request': request})

El formato `clave=valor` está en `settings.LOGGING`. Este filtro agrega a cada registro
método, ruta, usuario, tipo de excepción y el mensaje entre comillas. Nunca lee el cuerpo,
las cookies ni los parámetros de la petición: solo identificadores.
"""
import logging
import sys

SIN_VALOR = '-'


def _mensaje_entre_comillas(texto):
    texto = str(texto).replace('\\', '\\\\').replace('"', '\\"')
    return '"' + texto.replace('\r', '\\r').replace('\n', '\\n') + '"'


def _usuario(request):
    usuario = getattr(request, 'user', None)
    if usuario is None or not usuario.is_authenticated:
        return 'anonimo'
    return str(usuario.pk)


class FiltroContextoPeticion(logging.Filter):
    """Agrega el contexto de la petición al registro. Nunca descarta ni hace fallar un registro."""

    def filter(self, record):
        record.metodo = record.ruta = record.usuario = SIN_VALOR
        record.excepcion = SIN_VALOR
        try:
            record.mensaje_cv = _mensaje_entre_comillas(record.getMessage())
            if record.exc_info and record.exc_info[0] is not None:
                record.excepcion = record.exc_info[0].__name__
            request = getattr(record, 'request', None)
            if request is not None and hasattr(request, 'method'):
                record.metodo = request.method
                record.ruta = request.path  # sin la cadena de consulta
                record.usuario = _usuario(request)
        except Exception as error:  # noqa: BLE001
            # Única captura amplia permitida (AGENTS.md, regla 4): el registrador nunca puede
            # hacer fallar una petición. Se emite el problema a stderr antes de absorberlo.
            sys.stderr.write(f'nivel=ERROR registrador=pedidos.registro mensaje="Fallo del filtro de contexto: '
                             f'{type(error).__name__}"\n')
            if not hasattr(record, 'mensaje_cv'):
                record.mensaje_cv = '"(mensaje no disponible)"'
        return True
