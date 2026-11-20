"""Sanitización del HTML enriquecido (iteración 04-07, RDA-020, AUD-03-001).

Una sola función para los tres campos que escribe el editor (detalles del pedido, detalles de la
cotización y descripción del producto). Se aplica al guardar (``clean_<campo>`` de los
formularios) y al mostrar (filtro ``html_seguro``).

Lista blanca (D3): exactamente lo que ofrece la barra del editor, sin atributos. Las etiquetas
desconocidas y los comentarios se eliminan conservando su texto; ``script`` y ``style`` se
eliminan con su contenido.

Si ``nh3`` falla, la excepción no se captura (``AGENTS.md``, regla 8.4): mejor un error 500 visible
que HTML sin limpiar.
"""

ETIQUETAS_PERMITIDAS = frozenset({'p', 'br', 'b', 'strong', 'i', 'em', 'ul', 'ol', 'li'})
ETIQUETAS_CON_CONTENIDO_ELIMINADO = frozenset({'script', 'style'})


def sanitizar_html(texto):
    """Devuelve ``texto`` con solo las etiquetas de la lista blanca y sin atributos.

    ``None`` y la cadena vacía se devuelven tal cual (los campos admiten nulo). La función es
    idempotente: sanitizar lo ya sanitizado da lo mismo.
    """
    if not texto:
        return texto
    # Importación diferida (regla 8.9): solo se paga al sanitizar, no en cada arranque en frío.
    import nh3

    return nh3.clean(
        texto,
        tags=set(ETIQUETAS_PERMITIDAS),
        clean_content_tags=set(ETIQUETAS_CON_CONTENIDO_ELIMINADO),
        attributes={},
        strip_comments=True,
        link_rel=None,
    )
