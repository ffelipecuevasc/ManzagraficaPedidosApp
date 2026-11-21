"""Protección del acceso y límites de entrada (iteración 04-08, AUD-03-004).

Contador propio en un alias de caché dedicado (D1), con dos contadores independientes: por
usuario y por dirección (D2). El bloqueo se revisa en el `clean()` del formulario, ANTES de
`authenticate()`: así un intento bloqueado no emite `user_login_failed` ni escribe otra fila de
`acceso_fallido`. La caché es local y de un solo proceso: recargar la web app la borra, y eso
desbloquea a todos (docs/operacion/desbloqueo-de-acceso.md).

Las claves no guardan texto del usuario: el nombre va como resumen SHA-256 corto; la dirección
va tal cual, solo en memoria, y nunca se escribe en eventos ni en registros.
"""
import hashlib
import ipaddress
import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import caches
from django.http import HttpResponseRedirect
from django.urls import Resolver404, resolve

from .utils import TOPE_VOLCADO_BYTES

logger = logging.getLogger(__name__)

ALIAS_CACHE = 'acceso'

# D2: 5 fallos por usuario y 20 por dirección en 15 minutos; bloqueo de 15 minutos.
FALLOS_POR_USUARIO = 5
FALLOS_POR_DIRECCION_DEFECTO = 20
VENTANA_SEGUNDOS = 15 * 60
BLOQUEO_SEGUNDOS = 15 * 60
TEXTO_BLOQUEO = 'Hubo demasiados intentos fallidos. Espera 15 minutos y vuelve a intentarlo.'

# D5: imagen de referencia de hasta 5 MB.
TOPE_IMAGEN_BYTES = 5 * 1024 * 1024
TEXTO_CUERPO_GRANDE = 'El archivo supera el tamaño permitido y no se recibió. No se guardó nada.'


# ------------------------------------------------------------------
# Dirección del cliente (D3)
# ------------------------------------------------------------------

def direccion_cliente(request):
    """Dirección del cliente según `ACCESO_PROXIES_CONFIABLES`.

    Con 0, `REMOTE_ADDR`. Con n > 0, el elemento n contando desde la derecha de
    `X-Forwarded-For`: es el que agregó el proxy propio; lo de la izquierda lo puede escribir el
    cliente. Si la cabecera trae menos elementos o el valor no es una dirección, `REMOTE_ADDR`.
    """
    remota = request.META.get('REMOTE_ADDR', '')
    proxies = settings.ACCESO_PROXIES_CONFIABLES
    if proxies <= 0:
        return remota
    partes = [parte.strip() for parte in request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')]
    partes = [parte for parte in partes if parte]
    if len(partes) < proxies:
        return remota
    candidata = partes[-proxies]
    try:
        ipaddress.ip_address(candidata)
    except ValueError:
        return remota
    return candidata


# ------------------------------------------------------------------
# Contadores y bloqueos
# ------------------------------------------------------------------

def normalizar_usuario(nombre):
    """`strip()` y `casefold()`: la colación de producción no distingue mayúsculas."""
    return str(nombre or '').strip().casefold()


def _resumen_usuario(nombre):
    return hashlib.sha256(normalizar_usuario(nombre).encode('utf-8')).hexdigest()[:32]


def _claves(request, nombre):
    """Pares (clave de fallos, clave de bloqueo, límite) que aplican a este intento."""
    usuario = _resumen_usuario(nombre)
    claves = [(f'fallos:u:{usuario}', f'bloqueo:u:{usuario}', FALLOS_POR_USUARIO)]
    limite_direccion = settings.ACCESO_FALLOS_POR_DIRECCION
    if limite_direccion > 0:
        direccion = direccion_cliente(request)
        claves.append((f'fallos:d:{direccion}', f'bloqueo:d:{direccion}', limite_direccion))
    return claves


def esta_bloqueado(request, nombre):
    cache = caches[ALIAS_CACHE]
    return any(cache.get(bloqueo) for _, bloqueo, _ in _claves(request, nombre))


def _sumar_fallo(cache, clave_fallos, clave_bloqueo, limite):
    """Suma uno; devuelve True solo si este fallo empezó el bloqueo (`add` es atómico)."""
    cache.add(clave_fallos, 0, VENTANA_SEGUNDOS)
    try:
        fallos = cache.incr(clave_fallos)
    except ValueError:  # la ventana venció entre add e incr: empieza otra
        cache.set(clave_fallos, 1, VENTANA_SEGUNDOS)
        fallos = 1
    if fallos < limite:
        return False
    cache.delete(clave_fallos)
    return cache.add(clave_bloqueo, True, BLOQUEO_SEGUNDOS)


def registrar_fallo(request, nombre):
    """Suma el fallo a cada contador. Devuelve qué bloqueos empezaron: 'usuario', 'dirección'."""
    cache = caches[ALIAS_CACHE]
    empezados = []
    for (clave_fallos, clave_bloqueo, limite), motivo in zip(_claves(request, nombre), ('usuario', 'dirección')):
        if _sumar_fallo(cache, clave_fallos, clave_bloqueo, limite):
            empezados.append(motivo)
    return empezados


def reiniciar_usuario(nombre):
    """Un acceso correcto borra el contador del usuario (no el de la dirección)."""
    caches[ALIAS_CACHE].delete(f'fallos:u:{_resumen_usuario(nombre)}')


# ------------------------------------------------------------------
# Chequeo temprano del tamaño del cuerpo (D5)
# ------------------------------------------------------------------

# Tope del cuerpo declarado por ruta: el archivo más un margen para el resto del formulario.
_TOPES_POR_RUTA = {
    'crear_pedido': TOPE_IMAGEN_BYTES + 2_621_440,
    'editar_pedido': TOPE_IMAGEN_BYTES + 2_621_440,
    'restaurar_bd': TOPE_VOLCADO_BYTES + 1024 * 1024,
}


class LimiteCuerpoMiddleware:
    """Rechaza un POST con `CONTENT_LENGTH` mayor que el tope de su ruta, sin leer el cuerpo.

    Va como middleware y no en la vista porque `CsrfViewMiddleware.process_view` lee
    `request.POST` (y con eso recibe el archivo) antes de llegar a la vista. Este código corre
    antes que cualquier `process_view`. Una cabecera ausente o falsa no es un tope duro: después
    siguen la validación de la imagen y el tope de 20 MB de la 04-04.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST':
            tope = self._tope(request)
            if tope is not None and self._declarado(request) > tope:
                logger.info('Cuerpo declarado mayor que el tope de la ruta; rechazado sin leerlo',
                            extra={'request': request})
                messages.error(request, TEXTO_CUERPO_GRANDE)
                return HttpResponseRedirect(request.path)
        return self.get_response(request)

    @staticmethod
    def _tope(request):
        try:
            return _TOPES_POR_RUTA.get(resolve(request.path_info).url_name)
        except Resolver404:
            return None

    @staticmethod
    def _declarado(request):
        try:
            return int(request.META.get('CONTENT_LENGTH') or 0)
        except ValueError:
            return 0
