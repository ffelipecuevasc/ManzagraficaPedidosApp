from functools import wraps
from django.shortcuts import render
import sys


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
            print(f"⚠️ Error capturado por decorador en {view_func.__name__}: {e}")

            # Opcional: Podríamos pasar un mensaje específico al template
            context = {
                'mensaje_tecnico': f"Error en {view_func.__name__}: {str(e)}"
            }
            return render(request, 'pedidos/errors/500.html', context, status=500)

    return _wrapped_view