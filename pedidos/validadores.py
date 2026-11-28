"""Validadores de datos del negocio (iteración 14-04).

RUT chileno: cuerpo de 7 u 8 dígitos y dígito verificador por módulo 11 (`0`-`9` o `K`). Se acepta
con o sin puntos y guion, y con `k` minúscula. El RUT provisorio `00.000.000-0`, que reciben los
clientes anteriores a la 14-04, pasa el módulo 11: por eso el cuerpo en ceros se rechaza aparte
(D2). Ningún mensaje repite el valor escrito: el RUT es un dato personal y no va a registros.
"""
import re

from django.core.exceptions import ValidationError

RUT_PROVISORIO = '00.000.000-0'

# Con puntos bien puestos o sin ningún punto; guion opcional.
_PATRON_RUT = re.compile(r'^(\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-?([0-9K])$')


def _separar(valor):
    """Devuelve (cuerpo sin puntos, dígito verificador) o None si el formato no sirve."""
    if not isinstance(valor, str):
        return None
    coincidencia = _PATRON_RUT.match(valor.strip().upper())
    if coincidencia is None:
        return None
    cuerpo = coincidencia.group(1).replace('.', '')
    if len(cuerpo) not in (7, 8):
        return None
    return cuerpo, coincidencia.group(2)


def digito_verificador(cuerpo):
    """Módulo 11 sobre los dígitos del cuerpo, de derecha a izquierda con factores 2 a 7."""
    suma = sum(int(digito) * (2 + i % 6) for i, digito in enumerate(reversed(cuerpo)))
    resto = 11 - suma % 11
    return {11: '0', 10: 'K'}.get(resto, str(resto))


def validar_rut(valor):
    partes = _separar(valor)
    if partes is None:
        raise ValidationError(
            'Escribe el RUT con su dígito verificador, por ejemplo 12.345.678-5.', code='rut_formato')
    cuerpo, dv = partes
    if int(cuerpo) == 0:
        raise ValidationError(
            'Escribe el RUT real del cliente: 00.000.000-0 es un valor provisorio.', code='rut_provisorio')
    if digito_verificador(cuerpo) != dv:
        raise ValidationError(
            'El dígito verificador no corresponde a ese RUT. Revísalo.', code='rut_digito')


def normalizar_rut(valor):
    """Formato `12.345.678-5` con `K` mayúscula. Si el valor no se entiende, lo devuelve igual."""
    partes = _separar(valor)
    if partes is None or int(partes[0]) == 0:
        return valor
    cuerpo, dv = partes
    return f'{int(cuerpo):,}'.replace(',', '.') + f'-{dv}'
