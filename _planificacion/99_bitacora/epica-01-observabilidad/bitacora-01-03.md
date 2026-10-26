# Bitácora 01-03 · Retiro del middleware y trazas completas

- **Fecha:** 2026-10-25
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Terminada (2026-10-25, revisada por el desarrollador); sin desplegar; se despliega en 01-06, donde también se revisa la página 500 a 360 px. Sin migraciones. **Actualización 2026-10-26:** desplegada el 2026-10-25 en `v1.1-observabilidad` (commit `d6768d0`).

## Resumen

- `ErrorHandlingMiddleware` sale de `MIDDLEWARE` y se elimina `pedidos/middleware.py` (los dos cambios, aprobados). Ningún otro archivo lo importaba.
- `@transaccion_segura` cambia su `print` por `logger.exception` con la petición: la línea lleva vista, método, ruta, usuario, tipo de excepción y traza completa. Del decorador no cambia nada más.
- Los otros 6 `print` de diagnóstico pasan a `logging`. No queda ninguno en `pedidos/`.
- La página 500 muestra «Algo salió mal», sin código de error, sin detalles técnicos y sin la broma de los correos (texto aprobado).
- **8 pruebas nuevas** en `pedidos/tests/test_errores.py`, con `DEBUG=False` forzado. En total son 42, en verde tres veces.

## Decisión del desarrollador: los 404 (2026-10-25)

`django.request` se queda en nivel `ERROR`: los 404 no van a `error.log` y siguen visibles en `access.log`. **Motivo:** los rastreadores y bots que piden rutas inexistentes llenarían de ruido el registro de errores. No cambia `LOGGING`. Registrada en «Decisiones de la épica» de `definicion-epica-01.md`.

## Por qué el middleware era redundante y qué se perdía

- **Django ya convierte cada excepción en respuesta.** Cada capa de middleware queda envuelta por `convert_exception_to_response`. Si la vista lanza una excepción, la capa más interna la convierte en respuesta antes de que suba: registra `Internal Server Error` en `django.request` con la traza (`exc_info`) y, con `DEBUG=False`, llama a `handler500` (`pedidos.views.error_500`, ya declarado en `PedidosApp/urls.py`). Por eso el `try/except` de `ErrorHandlingMiddleware` casi nunca recibía la excepción de una vista: solo capturaba fallos de los middlewares que estaban por debajo de él.
  - **Comprobado:** con el middleware todavía puesto, la prueba `test_excepcion_en_vista_sin_decorador_responde_500_con_traza` ya pasaba (500, plantilla 500 y registro con traza). Las 6 pruebas que fallaban antes del cambio eran las del middleware, el decorador, la página 500 y los `print`.
- **Qué se perdía con él:** en los casos que sí capturaba, devolvía una página 500 propia sin pasar por `django.request`, así que el error quedaba fuera del registro de Django y su traza se perdía en un `print`. Además, la página recibía el mensaje de la excepción en el contexto (`error_message`).
- **Caso real del 2026-10-22, `/pagos/eliminar/1056/`:** `eliminar_pago` tiene `@transaccion_segura`, que capturaba la excepción (`TemplateDoesNotExist`) y dejaba solo un `print` truncado en `server.log` (`⚠️ Error capturado por decorador en eliminar_pago: pedidos/pago_confirm_delete.html`). Después devolvía una respuesta 500. Django registraba esa respuesta como `Internal Server Error: /pagos/eliminar/1056/` en `error.log`, **sin traza**, porque para Django la vista había respondido normalmente. La traza se perdía en el decorador, no en el middleware. Por eso el cambio del `print` del decorador es el que más aporta en esta iteración.
- **Después de 01-03, el mismo caso** deja en `error.log` dos líneas: la del decorador, con todo el contexto y la traza, y el resumen de Django:

```text
nivel=ERROR registrador=pedidos.decorators metodo=GET ruta=/pagos/eliminar/1056/ usuario=1 excepcion=TemplateDoesNotExist mensaje="Error capturado por decorador en eliminar_pago"
Traceback (most recent call last):
  ...
django.template.exceptions.TemplateDoesNotExist: pedidos/pago_confirm_delete.html
nivel=ERROR registrador=django.request metodo=GET ruta=/pagos/eliminar/1056/ usuario=1 excepcion=- mensaje="Internal Server Error: /pagos/eliminar/1056/"
```

Ejemplo armado con el formato verificado en la prueba de regresión, que usa un pago creado con las factorías. En producción, PythonAnywhere antepone su fecha UTC a cada línea.

## Inventario de `print` de diagnóstico

| Ubicación | Antes | Después | Nivel |
| :-------- | :---- | :------ | :---- |
| `pedidos/middleware.py:14` | `🔴 Error capturado por Middleware` | Archivo eliminado | — |
| `pedidos/decorators.py:18` | `⚠️ Error capturado por decorador en …` | `logger.exception('Error capturado por decorador en %s', vista, extra={'request': request})` | ERROR con traza |
| `pedidos/utils.py:87` | `Respaldo antiguo eliminado: …` | `logger.info(...)` | INFO |
| `pedidos/utils.py:89` | `Error al borrar respaldo antiguo …` | `logger.warning(..., exc_info=True)` (aprobado) | WARNING con traza |
| `pedidos/views.py:190` | `Error procesando items: …` | `logger.exception('Error procesando items del pedido %s', ...)` con la petición (aprobado). El `except Exception` que descarta ítems sigue igual: se corrige en 03-02 | ERROR con traza |
| `pedidos/views.py:219-222` | 4 `print` con `form.errors` | `logger.info` solo con los nombres de los campos con error, sin los mensajes (aprobado) | INFO |

**Búsqueda final** (`Grep`, patrón `\bprint\s*\(`, archivos `*.py` en `pedidos/`):

```text
No matches found
```

## Página 500

- **Antes:** título «500 ERROR», «Algo salió mal en nuestros sistemas» y «…nuestro equipo ya ha sido notificado (bueno, cuando configuremos los correos 😉)…».
- **Después:** título «Algo salió mal», «No pudimos completar lo que pediste. Vuelve a intentarlo en unos minutos.» y «Si el problema sigue, avísale al administrador y cuéntale qué estabas haciendo.» Se mantienen el ícono (ahora con `aria-hidden="true"`) y los botones «Recargar» e «Ir al inicio».
- Los párrafos pasan de `text-slate-500` / `dark:text-slate-400` a `text-slate-600` / `dark:text-slate-300`, para un contraste más holgado (regla 17).
- La plantilla no muestra `mensaje_tecnico`, que el decorador sigue pasando en el contexto. Quitarlo es parte del rediseño del decorador (03-01).

## Propuesta para `AGENTS.md`, regla 4 (`PENDIENTE_DESARROLLADOR`)

**Adoptada el 2026-10-26.** El desarrollador comprobó que `AGENTS.md` ya tiene la versión final acordada de la regla 4 («norma general que exige registrar»). El texto de abajo se conserva como historia; `AGENTS.md` no se modificó desde esta bitácora.

Solo como propuesta: el agente no edita `AGENTS.md`.

- **Archivo y sección:** `AGENTS.md`, sección 8, regla 4.
- **Texto actual:** «**Nada de supresión silenciosa.** Prohibido `except Exception: pass` y equivalentes. Se captura la excepción concreta que se sabe manejar y se registra con el servicio de registro del proyecto. La única captura amplia permitida está dentro del propio servicio de registro, porque el registrador nunca puede hacer fallar una petición; esa captura emite el error a la salida estándar antes de absorberlo.»
- **Texto propuesto:** «**Nada de supresión silenciosa.** Prohibido `except Exception: pass` y equivalentes. Se captura la excepción concreta que se sabe manejar y se registra con `logging` (`logger = logging.getLogger(__name__)`; dentro de una vista, con `extra={'request': request}`), que la escribe en la salida de error con el formato del proyecto; en PythonAnywhere se revisa en `server.log` (RDA-013). Las únicas capturas amplias permitidas están en el servicio de registro: el filtro de contexto (`pedidos/registro.py`) y el servicio de eventos (`pedidos/eventos.py`), porque el registro nunca puede hacer fallar una petición. Cada una lleva un comentario que lo dice y deja el problema en la salida de error (`logger.exception` o `sys.stderr`) antes de absorberlo. Nunca `print` ni la salida estándar para errores.»
- **Por qué:**
  - El texto actual dice «salida estándar», pero el proyecto registra con `logging` hacia la salida de error.
  - En producción, medido en la 01-06 el 2026-10-25, esa salida termina en `server.log`, con la línea completa (emoji, `clave=valor` y traza con `#012`). `error.log` recibe los mismos errores en el formato de PythonAnywhere.
  - Por decisión del desarrollador (opción A), el diagnóstico se hace en `server.log`. Por eso la regla nombra `logging`, no un archivo: el destino lo pone el entorno.
  - También conviene nombrar los dos módulos donde la captura amplia es legítima, para que no se confundan con la supresión que corrige la Épica 03.
- **Si no se cambia:** la regla sigue siendo compatible. Pero un agente podría usar `print` o la salida estándar, que no pasan por el filtro ni por el formato con contexto, y dejar el error sin método, ruta ni usuario.
- **Reescrita el 2026-10-25** tras el hallazgo de la 01-06 ([bitacora-01-06-produccion](bitacora-01-06-produccion.md)). La versión anterior afirmaba que la salida de error iba a `error.log` y la estándar a `server.log`. Lo primero quedó desmentido en producción y lo segundo no se midió.
- Mientras tanto, `@transaccion_segura` sigue con su `except Exception` amplio, ahora con registro completo. No es una excepción a la regla: es deuda conocida de la 03-01.

## Verificación

PowerShell 7, `DB_NAME=manzagrafica_replica`.

**Antes de corregir** (las pruebas se escribieron primero, regla 15): `python manage.py test pedidos.tests.test_errores` dio 8 pruebas con 6 `FAIL` (middleware presente, decorador sin registro, página 500, regresión de eliminar pago y los dos `print`). Pasaron la del 404 y la de la vista sin decorador, lo que confirma que Django ya manejaba esos casos.

**Después:**

| Criterio | Prueba (`test_errores.py`) |
| :------- | :------------------------- |
| Middleware retirado y archivo inexistente | `test_middleware_propio_retirado` |
| 404 con su plantilla | `test_pedido_inexistente_responde_404_con_su_plantilla` |
| 500 y traza en una vista sin decorador | `test_excepcion_en_vista_sin_decorador_responde_500_con_traza` |
| 500 y traza con `@transaccion_segura`, con el nombre de la vista | `test_excepcion_en_vista_con_transaccion_segura_registra_vista_y_traza` |
| Caso real de eliminar pago (AUD-02-002): tipo y traza completa | `test_regresion_eliminar_pago_deja_tipo_y_traza` (pasa: fija el registro, no el defecto) |
| Página 500 sin el mensaje, la traza ni la broma | `test_pagina_500_sin_detalles_tecnicos` |
| `print` pasados a `logging` | `PrintsDiagnosticoTests` (2 pruebas; la de validación comprueba que no aparece el texto escrito por el usuario) |

- `python manage.py test pedidos`: **42 pruebas en `OK`** en tres ejecuciones (20,6 s, 20,1 s y 20,4 s), sin líneas de registro sueltas en la salida.
- `python manage.py check`: sin problemas.
- `makemigrations --check --dry-run`: `No changes detected`. **Sin migraciones.**

## Desviaciones y observaciones

- **Fin de línea mixto en `settings.py`:** el archivo usa CRLF, pero los bloques `TEST` (02-01) y `LOGGING` (01-02) quedaron en LF al agregarlos. Python lo lee sin problemas. Normalizarlo es editar configuración, así que queda como propuesta en `registro-pendientes.md`. En esta iteración, el cambio de `MIDDLEWARE` respetó el CRLF.
- **Revisión visual de la página 500** en escritorio y a 360 px: no se hizo. Provocar un 500 en `runserver` exige iniciar sesión en la réplica, lo que escribe una sesión y `last_login`. El cambio es solo de texto y clases de color dentro del mismo contenedor. Queda para el desarrollador o para la validación de 01-06, donde el error controlado muestra esta página.
- **Dos líneas por error en las vistas con el decorador** (la del decorador con traza y el resumen de `django.request`): es lo esperado mientras exista el decorador. Se simplifica en 03-01.
- **AUD-01-004** queda «resuelto en local». Se cierra al desplegar en 01-06.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `PedidosApp/settings.py` | `MIDDLEWARE` sin `ErrorHandlingMiddleware` (aprobado) |
| `pedidos/middleware.py` | Eliminado (aprobado) |
| `pedidos/decorators.py` | `logger.exception` con la petición |
| `pedidos/utils.py` | 2 `print` → `logging` |
| `pedidos/views.py` | Registrador del módulo; 5 `print` → `logging` |
| `pedidos/templates/pedidos/errors/500.html` | Texto nuevo (aprobado) |
| `pedidos/tests/test_errores.py` | Nuevo: 8 pruebas |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-01-004 resuelto en local |
| `_planificacion/00_producto/registro-pendientes.md` | Cierre de 01-02, estado de 01-03, 2 decisiones abiertas e historial |
| `_planificacion/10_epicas/epica-01-observabilidad/definicion-epica-01.md` | Decisión de los 404, estados y referencia a la propuesta de la regla 4 |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-02-servicio-registro.md`, `iteracion-01-03-retiro-middleware.md`, `iteracion-01-06-despliegue-validacion.md` | Cierre de 01-02, estado de 01-03 y tarea 6 de 01-06 (sin líneas duplicadas) |
| `_planificacion/99_bitacora/epica-01-observabilidad/bitacora-01-02.md` | Estado final |

## Despliegue

- **Sin migraciones.** Viaja en 01-06, que ya exige respaldo previo por la 0007.
- En 01-06, el error controlado (por ejemplo, abrir la eliminación de un pago) debería dejar en `error.log` las dos líneas del ejemplo de arriba y mostrar la página 500 nueva.

## Pendientes

- Revisión del desarrollador.
- ~~Decisión sobre la propuesta de la regla 4 de `AGENTS.md`.~~ Resuelta el 2026-10-26: adoptada.
- Revisión visual de la página 500 a 360 px.
