# Iteración 01-03 · Retiro del middleware de captura global

- **Épica:** 01 · Observabilidad
- **Estado:** Pendiente
- **Subfase del plan:** 1.3
- **Depende de:** 01-02
- **RDA relacionadas:** RDA-005
- **Hallazgos que cierra:** AUD-01-004
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** Sí (se despliega en 01-06)

## Objetivo

Devolver el manejo de errores a Django: retirar `ErrorHandlingMiddleware`, que descarta la traza, y dejar que los manejadores 404 y 500 ya declarados en `PedidosApp/urls.py` produzcan las páginas, con el error registrado por el servicio de 01-02.

## Tareas

1. **Entender antes de borrar**: dejar en la bitácora una explicación breve de por qué el middleware es redundante (Django convierte la excepción de la vista en respuesta y llama a `handler500` cuando `DEBUG` es `False`) y qué se perdía con él (la traza, el registro `django.request`, el aviso a administradores).
2. **Retirar el middleware** de `MIDDLEWARE` en `settings.py` (requiere consulta) y eliminar `pedidos/middleware.py` (requiere consulta).
3. **Configurar `LOGGING`** (requiere consulta): el registro `django.request` en nivel `ERROR` dirige los errores al servicio de 01-02 y a la salida estándar.
4. **Página 500**: `error_500` muestra el identificador de correlación de la petición, sin detalles técnicos. Quitar el texto de broma sobre correos que no existen.
5. **Puente con `@transaccion_segura`**: mientras el decorador exista, captura las excepciones antes de que lleguen a Django. Reemplazar su `print` por una llamada al servicio de registro y hacer que la página que renderiza muestre el mismo identificador. No cambiar nada más del decorador: su rediseño es de la Épica 03.
6. **Pruebas** con `DEBUG=False` forzado en la prueba.

## Criterios de aceptación

- [ ] `pedidos.middleware.ErrorHandlingMiddleware` no aparece en `MIDDLEWARE` ni existe el archivo.
- [ ] Prueba: el detalle de un pedido inexistente responde 404 con la plantilla de error 404, no 500.
- [ ] Prueba: una excepción forzada en una vista sin decorador responde 500, crea una fila en la tabla de errores con traza completa, y el identificador de esa fila aparece en el HTML de la respuesta.
- [ ] Prueba: lo mismo para una vista con `@transaccion_segura`.
- [ ] La página 500 no contiene el mensaje de la excepción ni la traza.
- [ ] `python manage.py check` sin errores y `python manage.py test pedidos` en verde.

## Fuera de alcance

- Rediseñar o renombrar `@transaccion_segura` (va en 03-01).
- Cambiar el comportamiento de errores de validación de formularios (va en 03-04).

## Datos requeridos del cliente

- Ninguno.
