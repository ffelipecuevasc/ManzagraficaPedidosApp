# Iteración 01-03 · Retiro del middleware y trazas completas

- **Épica:** 01 · Observabilidad
- **Estado:** En revisión (2026-10-25; se despliega en 01-06)
- **Subfase del plan:** 1.3
- **Depende de:** 01-02
- **RDA relacionadas:** RDA-013
- **Hallazgos que cierra:** AUD-01-004
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** Sí (se despliega en 01-06)

## Objetivo

Que ninguna excepción se pierda: retirar `ErrorHandlingMiddleware`, que descarta la traza, devolver el manejo de errores a Django con los manejadores 404 y 500 ya declarados en `PedidosApp/urls.py`, y cambiar el `print` de `@transaccion_segura` por `logger.exception`, para que todo error llegue a `error.log` con la configuración de 01-02.

## Tareas

1. **Entender antes de borrar**: dejar en la bitácora una explicación breve de por qué el middleware es redundante (Django convierte la excepción de la vista en respuesta y llama a `handler500` cuando `DEBUG` es `False`) y qué se pierde con él (la traza y el registro `django.request`). Usar como ejemplo el caso real del 2026-10-22: `/pagos/eliminar/1056/` dejó solo `Internal Server Error` en `error.log` y un `print` truncado en `server.log`.
2. **Retirar el middleware** de `MIDDLEWARE` en `settings.py` (requiere consulta) y eliminar `pedidos/middleware.py` (requiere consulta).
3. **Puente con `@transaccion_segura`**: reemplazar su `print` por `logger.exception(...)` con el contexto de la petición (vista, método, ruta, usuario), para que la traza completa quede en `error.log`. No cambiar nada más del decorador: su rediseño es de la Épica 03.
4. **Otros `print` de diagnóstico** en `pedidos/` (por ejemplo, «Respaldo antiguo eliminado» en `server.log`): inventariarlos en la bitácora y pasarlos al registrador de la aplicación con el nivel que corresponda.
5. **Página 500**: `error_500` muestra un mensaje simple y comprensible, sin detalles técnicos y sin código de error. Quitar el texto de broma sobre correos que no existen.
6. **Propuesta de texto para `AGENTS.md`, regla 4** (si hace falta precisarla), escrita en la bitácora para que el desarrollador decida y edite (`PENDIENTE_DESARROLLADOR`; propuesta en bitacora-01-03).
7. **Pruebas** con `DEBUG=False` forzado en la prueba.

## Criterios de aceptación

- [x] `pedidos.middleware.ErrorHandlingMiddleware` no aparece en `MIDDLEWARE` ni existe el archivo. También lo comprueba una prueba.
- [x] Prueba: el detalle de un pedido inexistente responde 404 con la plantilla de error 404, no 500.
- [x] Prueba: una excepción forzada en una vista sin decorador responde 500 y deja un registro de nivel `ERROR` con la traza completa (`assertLogs`).
- [x] Prueba: lo mismo para una vista con `@transaccion_segura`, con el nombre de la vista en el registro.
- [x] Prueba de regresión del caso real: abrir la eliminación de un pago (AUD-02-002) deja en el registro el tipo de excepción y la traza completa, no solo el nombre de la plantilla. `test_regresion_eliminar_pago_deja_tipo_y_traza`.
- [x] La página 500 no contiene el mensaje de la excepción, la traza ni la broma de los correos.
- [x] No quedan `print` de diagnóstico en `pedidos/` (búsqueda pegada en la bitácora).
- [x] `python manage.py check` sin errores y `python manage.py test pedidos` en verde. 42 pruebas, tres veces.

## Fuera de alcance

- Corregir la plantilla de eliminar pago (AUD-02-002, va en 04-01).
- Rediseñar o renombrar `@transaccion_segura` (va en 03-01).
- Cambiar el comportamiento de errores de validación de formularios (va en 03-04).

## Datos requeridos del cliente

- Ninguno.