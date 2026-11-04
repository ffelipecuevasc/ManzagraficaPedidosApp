# Bitácora 00-07 · Despliegue de `v0.3-doble-envio`

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión. Desplegada y validada el 2026-11-04; falta la medición de `access.log` del 2026-11-11 (hacia las 01:32) para cerrarla.

Es la bitácora nueva que pide la regla 5.4 de `_planificacion/README.md`: [bitacora-00-07](bitacora-00-07.md) y [bitacora-00-07-revision](bitacora-00-07-revision.md) ya están entregadas y no se editan. Solo se citan conteos, horas, códigos de estado y rutas sin parámetros; ningún dato de clientes, ninguna dirección IP y ninguna ruta de la carpeta de respaldos (solo nombres de archivo). Todas las horas son de Chile, salvo que diga UTC. Toda la medición viene de producción y del PC del desarrollador; el agente no tiene acceso a ellos.

## Resumen

`v0.3-doble-envio` (etiqueta anotada, objeto `e68f87212245679d68ba8340db46cd9c3218419d`, sobre el commit `5dc82a8`, que es `main` y `origin/main`; partida y destino de retroceso `v1.2-capturas`) se desplegó el 2026-11-04 **sin migraciones, sin `pip`, sin `collectstatic` y sin respaldo previo nuevo**. La **hora oficial de la recarga es 01:32:51**, la del reinicio efectivo (`Starting uWSGI`); la orden de Reload se recibió a las 01:32:45. La validación en una ventana privada (acceso, panel, listado, detalle, «Nuevo pedido» y «Editar pedido») salió sin problemas, sin enviar formularios, y no hubo líneas con `nivel=` desde el reinicio. **No hizo falta retroceder.** La iteración no se cierra: su último criterio, que `access.log` no muestre dos `POST /pedidos/nuevo/` en el mismo segundo durante la semana siguiente, se mide el 2026-11-11.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-07.md` | Partes A a C completas, nota fechada, fecha de la parte D (2026-11-11) y respuesta del desarrollador |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-07-correcciones-tempranas-ii.md` | Estado «En revisión (desplegada el 2026-11-04 como `v0.3-doble-envio`; falta la medición del 2026-11-11)»; dos criterios de producción marcados y el de la semana sin marcar |
| `docs/operacion/despliegue.md` | Sección 5: fila de `v0.3-doble-envio`. Sección 3: advertencia sobre el checkout de ramas (en 3.2) y, en 3.6, regla de la hora de una recarga y comando para detectar reinicios (decisión 2 y 5) |
| `docs/operacion/respaldo.md` | Sección 6: la fila del respaldo de las 00:12:37 dice que se descargó desde Files y que la descarga automática se cortó |
| `_planificacion/10_epicas/epica-01-observabilidad/evidencia-01-09.md` | Ventana del incidente «VERIFICADA» y descarga de E2 «desde Files» |
| `_planificacion/00_producto/auditoria-tecnica.md` | Notas fechadas de AUD-03-002, AUD-04-004, AUD-01-003 y AUD-01-020, sin reescribir hallazgos |
| `_planificacion/00_producto/registro-pendientes.md` | Iteración activa, próximo hito, fechas vigentes, fila de la 00-07, seguimiento de `robots.txt` e historial |
| `_planificacion/10_epicas/epica-03-integridad-transaccional/definicion-epica-03.md` | Nota fechada con la decisión 1; alcance sin cambios |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-07-despliegue.md` | Esta bitácora |
| `_planificacion/99_bitacora/epica-01-observabilidad/bitacora-01-09-despliegue-verificacion.md` | Bitácora nueva con los conteos de la ventana del incidente y las verificaciones de la noche |

Sin cambios de código, de `pedidos/tests/`, de documentos protegidos, de `.claude/` ni de bitácoras ya entregadas. Se corrigieron antes las fechas «2026-11-01» de la iteración 00-07, de la evidencia y del registro (ronda anterior); no se tocó la fila de `v1.1-observabilidad` de `despliegue.md`.

## Datos del despliegue (hora de Chile; el reloj de la consola de PythonAnywhere marca UTC)

| Paso | Resultado |
| :--- | :-------- |
| Comprobaciones previas en el PC | `git status --short` vacío; `main` igual a `origin/main`; el `diff` de `v1.2-capturas..main` sin `_planificacion` ni `docs` lista solo `pedido_form.html` (1 archivo, 41 inserciones, 3 eliminaciones) |
| Pruebas y `check --deploy` | **No repetidos, a propósito:** el `diff` de `bd07f21` contra `main`, sin `_planificacion` ni `docs`, salió vacío, así que el código es idéntico al de `bd07f21`, donde corrieron el mismo 2026-11-04: `Ran 184 tests`, `OK (expected failures=19)` en dos ejecuciones (174,975 s y 283,578 s), y `check --deploy` con exactamente `W004`, `W008`, `W009`, `W012` y `W016` (evidencia-01-09, parte B) |
| Etiqueta (B4) | `v0.3-doble-envio` anotada sobre `5dc82a8`, mensaje «Iteración 00-07 · desplegada el 2026-11-04», publicada; `ls-remote` devolvió una línea |
| Servidor, antes | Prompt «(HEAD detached at v1.2-capturas)», `git status --short` vacío, `describe` = `v1.2-capturas` |
| Servidor, `fetch` y `checkout` | `fetch --tags` trajo `bd07f21..5dc82a8` y la etiqueta; `checkout` dejó HEAD en `5dc82a8` (`describe` = `v0.3-doble-envio`) |
| Migraciones, `pip` y estáticos | `migrate --plan`: «No planned migration operations.» (con la advertencia conocida `mysql.W002`). `diff --stat` entre `v1.2-capturas` y `v0.3-doble-envio` de `requirements.txt`, `pedidos/static` y `pedidos/migrations`: vacío. El de `pedidos/templates`: solo `pedido_form.html` |
| Reload | Orden recibida a las **01:32:45** (`received message 0 from emperor`, que marca el clic); reinicio efectivo, **01:32:51** (`Starting uWSGI`): **hora oficial**, por la decisión 5. El mensaje interno de uWSGI dice 04:32:50 UTC (01:32:50 en Chile) |
| Validación en ventana privada | Acceso, panel, listado de pedidos, detalle de un pedido, «Nuevo pedido» y «Editar pedido» abren y muestran el cambio. **No** se envió ningún formulario y **no** se usó «Estadísticas» |
| `server.log` desde el reinicio | Conteo por `nivel=`: **0** líneas |
| Respaldo previo | No se hizo uno nuevo: la 00-07 no toca datos ni esquema. El último verificado es `respaldo_04-11-2026_00-12-37.sql` (19 de 19, `VÁLIDO`) |
| Retroceso | No necesario |

## Criterios de aceptación

Criterios de la [iteración 00-07](../../10_epicas/epica-00-blindaje/iteracion-00-07-correcciones-tempranas-ii.md): 10 de 11 marcados.

- [x] Los 8 criterios de la verificación en local (2026-10-27) ya estaban marcados ([bitacora-00-07-revision](bitacora-00-07-revision.md)).
- [x] **Desplegada con su propia etiqueta, `v0.3-doble-envio`, distinta de `v1.2-capturas`.** Medido: etiqueta sobre `5dc82a8`, publicada; en el servidor, `describe` = `v0.3-doble-envio`; reinicio efectivo a las 01:32:51; sin retroceso.
- [x] **`v1.2-capturas` apunta al último commit anterior a la 00-07, y el `diff` muestra solo `pedido_form.html` y documentos.** Medido: `v1.2-capturas` → `81005df`; `diff` sin `_planificacion` ni `docs`: solo `pedido_form.html`.
- [ ] **Una semana después del despliegue, `access.log` no muestra dos `POST /pedidos/nuevo/` en el mismo segundo.** **Sin marcar:** se mide el **2026-11-11, hacia las 01:32** (evidencia-00-07, parte D). El 2026-11-04 UTC mezcla unas 4,5 h anteriores al despliegue (el reinicio fue a las 04:32:51 UTC).

## Verificación

- Evidencia de producción: tomada tal como la entregó el desarrollador; el agente no la pudo comprobar.
- Pruebas: no se ejecutaron en esta tarea (no hay cambios de código); las del despliegue se reutilizan por tener código idéntico (arriba). Pantallas del navegador: no aplica.
- Diferencias de tiempo: 01:32:51 − 01:32:45 = 6 s entre la orden de Reload y el reinicio efectivo.
- Lo que el agente **no** pudo comprobar: el efecto del cambio con un doble clic real en producción (la revisión solo miró, a propósito), qué texto exacto mostraron los botones, «Nueva cotización», `check` y `makemigrations --check` de esta ejecución, y la salida literal de `git tag -n` y de los `rev-parse` (no informados).

## Migraciones

- Ninguna. `migrate --plan` del servidor: «No planned migration operations.» Esta tarea solo toca documentos `.md`.

## Decisiones tomadas (2026-11-04, todas del desarrollador)

1. **Épica 03:** puede empezar cuando la 00-07 esté desplegada y validada. La semana de vigilancia de la 00-07 corre en paralelo y ya no bloquea el inicio. Cambia lo que decía el registro («bloqueada hasta cerrar la 00-07»); la 00-07 está desplegada y validada, así que la precondición se cumple. No se empezó la Épica 03 ni se redactaron sus iteraciones (las inicia el desarrollador en un chat nuevo). Nota fechada en `definicion-epica-03.md`.
2. **Propuestas de la 01-09:** se aplican a `despliegue.md` §3 (advertencia y comando de reinicios). El comando quedó probado el 2026-11-04: con `DESDE_CL="2026-11-03 23:30:00"` imprimió solo la línea de las 00:11:49. No se modificó el servidor.
3. **Ventana del incidente:** de «no verificada» a «verificada», con tres conteos ([bitacora-01-09-despliegue-verificacion](../epica-01-observabilidad/bitacora-01-09-despliegue-verificacion.md)).
4. **Respaldo de las 00:12:37:** se descargó desde Files; la descarga automática se cortó.
5. **Hora oficial de una recarga:** la del reinicio efectivo (`Starting uWSGI`, prefijo en hora de Chile), no la del reloj del desarrollador; `received message 0 from emperor` marca el clic de Reload. Regla agregada a `despliegue.md` §3.6.
6. **Cierre:** la 00-07 no se cierra y la Épica 00 sigue «reabierta» hasta cerrarla. AUD-04-001 sigue Abierto: la 00-07 solo cubre el lado del cliente; el servidor, la 03-04.

## Pendientes y riesgos

- **Medición del 2026-11-11, hacia las 01:32** (evidencia-00-07, parte D): con ella se marca el último criterio y se cierra la 00-07. Un `segundos_repetidos` mayor que 0 no prueba un duplicado, pero con un solo usuario es la señal que se busca.
- **Dos de los días de la medición son parciales:** el 2026-11-04 UTC (mezcla antes y después) y el 2026-11-11 UTC (llega hasta las 04:32 UTC).
- **«Nueva cotización» (C4.3) no se informó** y el texto de C4.1 y C4.2 («se ve igual») es anterior a la decisión 7 (el botón dice «Editar Pedido» al editar); la evidencia lo anota. Queda a decisión del desarrollador si basta con lo informado («muestran el cambio»).
- **El doble clic no se probó en producción:** solo lo medirá la parte D, de forma indirecta.
- **Fechas vigentes:** renovar la web app de PythonAnywhere hacia el 2026-11-10 (vence el 2026-11-20); próximo respaldo semanal hacia el 2026-11-10 u 11; medición de la 00-07 el 2026-11-11; informe de desconexiones a 28 días (C2 de la 00-06) el 2026-11-20.
- **Avisar a Manza Gráfica** de que el cambio ya está en producción (el botón dice «Guardando…» tras el primer clic).
- **El servidor conserva su rama `main` atrasada** (`v0.0-inicial`); la advertencia de `despliegue.md` §3.2 lo cubre en el procedimiento.

## Commit sugerido

`Épica 0 - Iteración 00-07: registra el despliegue de v0.3-doble-envio y su validación, aplica a despliegue.md las advertencias del incidente y deja la Épica 03 lista para empezar`
