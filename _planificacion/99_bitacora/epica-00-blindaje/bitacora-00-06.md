# Bitácora 00-06 · Correcciones tempranas de riesgo nulo

- **Fecha:** 2026-10-23
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Terminada (2026-10-25). Desplegada el 2026-10-23 como `v0.2-correcciones`, sin retroceso. Cierra también la Épica 00.

## Resumen

- **Tarea 1, WeasyPrint diferido:** `import weasyprint` sale de la cabecera de `pedidos/views.py` y pasa al interior de `exportar_cotizacion_pdf`, con un comentario que explica el motivo. Si la importación falla, el error aparece al exportar el PDF y no al iniciar la app.
- **Tarea 2, `robots.txt`:** nueva vista `robots_txt` con `require_safe` (GET y HEAD; antes `require_GET`, cambiado el 2026-10-23 a pedido del desarrollador) y `login_not_required`, que responde `text/plain; charset=utf-8` con `User-agent: *` y `Disallow: /`, sin plantilla.
  - Mecanismos globales revisados: `MIDDLEWARE` no incluye `LoginRequiredMiddleware`, y el único middleware propio (`ErrorHandlingMiddleware`) no exige sesión. Por eso hoy basta con no decorar la vista con `login_required`. `login_not_required` la mantiene pública si más adelante se activa ese middleware.
- **Tarea 3, doble envío en el acceso:** al primer envío, el botón se deshabilita, marca `aria-busy` y muestra «Ingresando…» con un ícono que gira. Un segundo envío se cancela. El evento `pageshow` lo restaura al recargar y al volver con «atrás» (caché del navegador). Script en línea en la propia plantilla.
- **Tarea 4:** `pagos/lista` pasa a `pagos/lista/`. `CommonMiddleware` con `APPEND_SLASH` redirige con 301 la dirección sin barra.
- **Pruebas:** `pedidos/tests.py` pasa de vacío a 6 pruebas: `robots.txt` sin sesión, con HEAD y 405 con POST, pagos con barra y redirección sin barra, y `weasyprint` fuera de `sys.modules` tras recargar las vistas.

## Desviaciones y observaciones

- **La definición dice que la página de acceso no carga `index.js`, pero sí lo carga** (última línea de `login.html`). Se dejó así, porque quitarlo queda fuera de alcance. Sus manejadores apuntan a otros botones y no interfieren. El script del acceso queda en la plantilla, como pide la tarea.
- **Pruebas en `pedidos/tests.py`, no en un paquete por dominio** (AGENTS.md, 8.15): convertir el archivo en paquete implica eliminarlo o moverlo, lo que requiere consulta. Queda para la 02-01.
- `despliegue.md`, punto 1 de la lista: dice «Hasta la 02-01 no hay pruebas». Desde esta iteración hay 5. Es una nota de procedimiento, no de un documento protegido; se deja para cuando la 02-01 lo revise.
- `test pedidos` muestra la advertencia `mysql.W002` (modo estricto de MySQL sin activar). Existía antes y no viene de esta iteración.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/views.py` | Tareas 1 y 2 (importaciones `login_not_required` y `require_safe`, vista `robots_txt`) |
| `pedidos/urls.py` | Ruta `robots.txt` y `pagos/lista/` |
| `pedidos/templates/registration/login.html` | Tarea 3 |
| `pedidos/tests.py` | 6 pruebas |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-06.md` | Nuevo: partes A, B y C |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-06-correcciones-tempranas.md` | Estado |
| `_planificacion/00_producto/registro-pendientes.md` | Estado, seguimiento, hallazgo `favicon.ico` e historial |
| `_planificacion/00_producto/auditoria-tecnica.md` | Cierre de AUD-01-020 y AUD-01-021; avance de AUD-01-011 y AUD-01-024; notas de 00-06 |
| `_planificacion/10_epicas/epica-00-blindaje/definicion-epica-00.md` | Épica cerrada, criterios de término y resumen de cierre |

## Verificación

- **Medición «antes»** (desarrollador, 2026-10-23): importar `pedidos.urls` tardó 1.723,9, 690,6 y 672,4 ms, con media de 1.029,0 ms. `weasyprint` estaba en `sys.modules`: `True`.
- **Medición «después»** (desarrollador): 40,6, 22,4 y 16,0 ms, con media de 26,3 ms, unas 39 veces menos que antes (26 veces frente a la media sin la primera corrida). `weasyprint` en `sys.modules`: `False`.
- **Parte A revisada por el agente el 2026-10-23: todos los criterios locales se cumplen.**
  - PDF de la cotización 5: `200`, `application/pdf`, `%PDF`.
  - `robots.txt` sin sesión: `200`, `text/plain`, `Disallow: /`. El POST da `403` por CSRF, que es aceptable.
  - `/pagos/lista/`: `200`; `/pagos/lista` redirige con `301`.
  - Botón de acceso: revisado en escritorio y a 360 px en Firefox. En Chrome, «atrás» tras un POST fallido pide confirmar el reenvío (`ERR_CACHE_MISS`), que es comportamiento del navegador.
- **Comandos corregidos en la evidencia:** A4 y A7 (`-MaximumRedirection 0` falla en PowerShell 7.6) y `$pk` en A5 (`Select-Object -Last 1` y `.Trim()`).
- **Agente:** `python manage.py test pedidos` dio 6 pruebas en `OK` tras el cambio a `require_safe`; `check` no encontró problemas; `makemigrations --check --dry-run` dio `No changes detected`.
- **Cambio de esquema:** ninguno; no hay migraciones.

## Despliegue y cierre (2026-10-23 a 2026-10-25)

- **Parte B:** lista de comprobación en verde (`Ran 6 tests`, `OK`; `check --deploy` con las cinco advertencias conocidas; sin migraciones). Etiqueta `v0.2-correcciones` en el commit `7944943`, recarga el 2026-10-23 a las 18:35 Chile (21:35 UTC). Los `diff` de `requirements.txt`, `pedidos/static` y `pedidos/migrations` salieron vacíos.
- **Incidente de etiqueta:** se creó primero con el texto de relleno `<AAAA-MM-DD>` en el mensaje. Ningún servidor la había descargado: se eliminó y se recreó sobre el mismo commit. Lección: la etiqueta se crea solo con el mensaje final.
- **Verificación en producción (B3):** `robots.txt` con `200` y `text/plain`, acceso con «Ingresando…», panel, pedidos, pagos y PDF correctos. Única línea nueva en el registro de errores: `Not Found: /favicon.ico` (hallazgo menor, registrado como propuesta).
- **Conteo C1 (2026-10-25):**

| Fecha UTC | `robots` | `robots_404` | `broken_pipe` |
| :-------- | -------: | -----------: | ------------: |
| 2026-10-19 a 2026-10-22 | 9 | 9 | 2 |
| 2026-10-23 (despliegue) | 1 | 0 | 0 |
| 2026-10-24 | 0 | 0 | 1 |
| 2026-10-25 (parcial) | 0 | 0 | 0 |

- **Lectura:** 0 404 desde el despliegue; la única petición posterior (verificación manual) dio 200. Ningún rastreador pidió la ruta el 24 ni el 25. `Broken pipe`: 3 en 7 días, igual que la línea base.
- **Decisión del desarrollador (2026-10-25):** cerrar la 00-06 y la Épica 00 con esta evidencia. Se cierran AUD-01-020 y AUD-01-021; avanzan AUD-01-011 (05-01) y AUD-01-024 (06-06).

## Pendientes

- **Seguimiento (2026-11-20):** parte C2, con la tasa de `Broken pipe` a 28 días y la confirmación de que un rastreador real recibe 200 en `/robots.txt`.
- `favicon.ico` con 404: propuesta de prioridad baja en `registro-pendientes.md`, sección 4.
- Propuesta registrada: redirigir al panel desde el acceso cuando ya hay sesión (Épica 04, prioridad baja). La parte C2 (28 días) va en paralelo y no bloquea la Épica 01.
