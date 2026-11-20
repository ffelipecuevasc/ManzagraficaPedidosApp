"""Filtro `html_seguro` (iteración 04-07, D1, al mostrar).

Reemplaza a `|safe` en los tres campos del editor: sanitiza con la lista blanca y solo entonces
marca el resultado como seguro. Protege lo ya guardado, lo que entra por el admin y lo que copian
la duplicación y la conversión sin pasar por un formulario.
"""
from django import template
from django.utils.safestring import mark_safe

from pedidos.sanitizar import sanitizar_html

register = template.Library()


@register.filter(name='html_seguro')
def html_seguro(valor):
    if not valor:
        return ''
    return mark_safe(sanitizar_html(str(valor)))  # seguro: sale de la lista blanca sin atributos
