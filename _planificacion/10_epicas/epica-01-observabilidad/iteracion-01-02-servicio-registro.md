# Iteración 01-02 · Configuración del registro y servicio de eventos

- **Épica:** 01 · Observabilidad
- **Estado:** En revisión (2026-10-25; se despliega en 01-06)
- **Subfase del plan:** 1.2
- **Depende de:** 01-01, 02-01
- **RDA relacionadas:** RDA-008, RDA-013
- **Hallazgos que cierra:** ninguno por sí sola. Avanza AUD-01-005.
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** Sí (se despliega en 01-06)

## Objetivo

Dos piezas independientes: **(a)** una configuración de `logging` que deja cada error en `error.log` de PythonAnywhere ordenado, completo y sin ruido; **(b)** un servicio que registra eventos de negocio solo cuando la operación se confirmó y que nunca hace fallar una petición.

## Tareas

### A. Configuración del registro (`LOGGING`, requiere consulta)

1. **Entender el estado actual** y dejarlo en la bitácora: cómo llegan hoy las líneas a `error.log` (por ejemplo, `Internal Server Error: …` del registrador `django.request`) y a `server.log` (los `print`), y la fecha que PythonAnywhere antepone a cada línea de `error.log` (UTC).
2. **Destino:** un manejador a la salida de error (`stderr`), que PythonAnywhere guarda en `error.log`. Sin archivos de registro propios en el disco de la cuenta.
3. **Formato de línea** `clave=valor`, una línea de cabecera por registro y la traza completa debajo. Campos mínimos: nivel, registrador, método, ruta, id de usuario (o `anonimo`), tipo de excepción y mensaje. Si PythonAnywhere ya antepone la fecha, el formato no la repite; si se incluye, va con zona horaria explícita. Ejemplo orientativo: `nivel=ERROR registrador=pedidos.views metodo=GET ruta=/pagos/eliminar/1056/ usuario=1 excepcion=TemplateDoesNotExist mensaje="pedidos/pago_confirm_delete.html"`.
4. **Registradores:** `django.request` en `ERROR`; `django.security` en `WARNING` (CSRF rechazado, host no permitido); `pedidos` (el de la aplicación) en `INFO`; `fontTools` y `weasyprint` en `WARNING` para eliminar el ruido.
5. **Contexto de la petición:** un filtro de `logging` que, cuando el registro trae la petición, agrega método, ruta y usuario. Sin identificador de petición (decisión del 2026-10-25).
6. **Datos sensibles:** nunca contraseñas, cuerpos de formularios, datos de clientes ni cookies; solo identificadores.
7. **Registrador por módulo** (`logging.getLogger(__name__)`) como convención del proyecto para 01-03 y las épicas siguientes.

### B. Servicio de eventos

1. **Diseño escrito** en la bitácora (o como ampliación de RDA-013) con las dos trampas que siguen vigentes:
   1. **Fallo en cascada:** el servicio nunca lanza una excepción hacia quien lo llama. Si la escritura falla, emite el problema con `logger.exception` y retorna. Es la única captura amplia permitida del proyecto (`AGENTS.md`, regla 4), y el código lo dice con un comentario.
   2. **Costo por petición:** el servicio solo se invoca para el inventario de eventos; nunca en lecturas ordinarias.
2. **Registro después de confirmar:** el evento se escribe con `transaction.on_commit`, para no registrar acciones que no ocurrieron.
3. **Implementación** en un módulo propio dentro de `pedidos/`.

### C. Pruebas

- Una por cada comportamiento de los criterios, con `assertLogs` para el registro.

## Criterios de aceptación

- [x] La bitácora explica el estado actual de `error.log` y `server.log` y la configuración elegida.
- [x] Prueba: un error registrado con el registrador de la aplicación dentro de una petición produce la línea con nivel, método, ruta, usuario, tipo de excepción y la traza completa. `test_registro.py`.
- [x] Prueba: un usuario anónimo aparece como `anonimo`, y la línea no contiene la contraseña ni el cuerpo del formulario.
- [x] Prueba: un mensaje `INFO` de `fontTools` no se emite; uno `WARNING` sí. Incluye el caso de `capture_logs` de WeasyPrint; un PDF real pasó de 540 líneas de `fontTools` a 0.
- [x] Prueba de fallo en cascada: con una excepción inyectada en la escritura del evento, la función retorna sin lanzar y el problema queda en el registro. También con un `IntegrityError` real de MySQL y la aplicación respondiendo después.
- [x] Prueba de costo: el número de consultas de una vista de listado no cambia con el servicio instalado (`assertNumQueries` con el mismo valor antes y después). 4 consultas en `/pagos/lista/`, fijadas en la prueba; el servicio no se llama.
- [x] Prueba de confirmación: un evento registrado dentro de una transacción que se revierte no queda en la tabla; uno dentro de una transacción confirmada, sí.
- [x] Verificación manual en local con `runserver`: un error forzado se ve en la terminal con el formato acordado (salida pegada en la bitácora). Error forzado: POST sin CSRF (403).
- [x] `python manage.py check` sin errores y `python manage.py test pedidos` en verde. 34 pruebas, tres veces.

## Fuera de alcance

- Retirar el middleware y cambiar el `print` del decorador (va en 01-03).
- Llamar al servicio de eventos desde las vistas de negocio (va en 01-04).
- Formato JSON, archivos de registro propios o servicios externos de registro.

## Datos requeridos del cliente

- Ninguno.