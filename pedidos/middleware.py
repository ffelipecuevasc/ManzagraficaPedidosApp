from django.shortcuts import render


class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Aquí capturamos cualquier error que ocurra en las vistas
            print(f"🔴 Error capturado por Middleware: {str(e)}")  # Log en consola para ti

            # Delegamos el manejo a nuestra función personalizada
            return self.handle_exception(request, e)

    def handle_exception(self, request, exception):
        """
        Renderiza la página de error 500 amigable en lugar de dejar que Django explote.
        """
        # Podemos pasar el error al template si quisiéramos mostrar detalles (opcional)
        context = {
            'error_message': str(exception)
        }
        return render(request, 'pedidos/errors/500.html', context, status=500)