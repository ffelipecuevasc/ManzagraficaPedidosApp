import logging
from functools import wraps

from django.shortcuts import render
import sys

logger = logging.getLogger(__name__)

def transaccion_segura(view_func):
    """
    Decorador que envuelve una vista en un bloque try-except.
    Si ocurre un error, evita que la app explote y muestra la página 500.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            # Intentamos ejecutar la vista normal (ej: crear pedido)
            return view_func(request, *args, **kwargs)
        except Exception as e:
            # Si algo falla, capturamos el error aquí mismo
            # Traza completa a error.log con el contexto de la petición (01-03). El rediseño
            # del decorador es de la Épica 03.
            logger.exception('Error capturado por decorador en %s', view_func.__name__,
                             extra={'request': request})

            # Opcional: Podríamos pasar un mensaje específico al template
            context = {
                'mensaje_tecnico': f"Error en {view_func.__name__}: {str(e)}"
            }
            return render(request, 'pedidos/errors/500.html', context, status=500)

    return _wrapped_view