"""Paso único del folio de cotización (iteración 14-04, D4 y aviso 2, opción C).

El número inicial del negocio no está en el código: lo escribe el desarrollador en la consola, una
vez, durante el despliegue (`docs/operacion/despliegue.md`, sección de la 14-04):

    from pedidos.paso_unico_folio import fijar_inicio_folio
    ok, texto = fijar_inicio_folio(<inicio>)
    print(texto)

Fija el contador en `inicio - 1`, así que la próxima cotización recibe `inicio`. Se niega si alguna
cotización existente ya tiene un folio igual o mayor que `inicio`: la guarda mira las cotizaciones,
no el contador, para que se pueda volver a correr después de borrar una cotización de prueba.
Devuelve `(hecho, texto)`; solo informa números, nunca datos de clientes.
"""
from django.db import transaction
from django.db.models import Max

from .models import Cotizacion, SecuenciaFolio


def fijar_inicio_folio(inicio):
    if not isinstance(inicio, int) or isinstance(inicio, bool) or inicio < 1:
        return False, 'NEGADO: el inicio debe ser un número entero mayor que 0. Contador sin cambios.'
    with transaction.atomic():
        fila, _ = SecuenciaFolio.objects.select_for_update().get_or_create(
            nombre=SecuenciaFolio.COTIZACION,
            defaults={'ultimo_folio': Cotizacion.objects.aggregate(m=Max('folio'))['m'] or 0})
        antes = fila.ultimo_folio
        en_conflicto = Cotizacion.objects.filter(folio__gte=inicio).count()
        if en_conflicto:
            return False, (f'NEGADO: {en_conflicto} cotización(es) ya tienen folio {inicio} o mayor. '
                           f'Contador sin cambios (antes: {antes}; después: {antes}).')
        fila.ultimo_folio = inicio - 1
        fila.save(update_fields=['ultimo_folio'])
    return True, (f'HECHO: contador de folios de cotización, antes: {antes}; después: {inicio - 1}. '
                  f'La próxima cotización recibirá el folio {inicio}.')
