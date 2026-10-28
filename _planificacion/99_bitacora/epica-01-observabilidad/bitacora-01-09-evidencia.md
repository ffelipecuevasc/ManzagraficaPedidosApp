# Bitácora 01-09 · Capturas amplias que incumplen la regla 4 (evidencia de despliegue)

- **Fecha:** 2026-10-27
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión hasta el despliegue del domingo 2026-11-01 (sin cambio de estado)

## Resumen

Se preparó [evidencia-01-09](../../10_epicas/epica-01-observabilidad/evidencia-01-09.md) para desplegar `v1.2-capturas` (01-09, 01-08 y 01-07 reabierta) el domingo 2026-11-01, en el orden decidido por el desarrollador: respaldo previo, parte D de la 01-06, lista de comprobación, etiqueta sobre `81005df`, despliegue y validación. Antes se comprobó con Git, en solo lectura, qué contiene la etiqueta. La iteración 01-09 suma su cabecera de despliegue y los criterios de producción, y `evidencia-00-07` remite a esta evidencia para crear `v1.2-capturas` una sola vez. Solo documentación.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/10_epicas/epica-01-observabilidad/evidencia-01-09.md` | Nuevo: partes A a E y tablas de resultados |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-09-capturas-amplias.md` | Cabecera (etiqueta, retroceso, ventana, evidencia) y cuatro criterios de producción, sin borrar nada |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-07.md` | Orden del domingo y nota de la parte B (B1 a B3 en la evidencia-01-09); texto anterior tachado |
| `_planificacion/00_producto/registro-pendientes.md` | Línea de historial |
| `_planificacion/99_bitacora/epica-01-observabilidad/bitacora-01-09-evidencia.md` | Esta bitácora |

## Verificación (comprobaciones de Git, solo lectura, 2026-10-27)

```
$ git log --oneline -n 4
359893f Épica 0 - Iteración 00-07: verifica en local el bloqueo del doble envío …
4560874 Épica 0 - Iteración 00-07: evita el doble envío de Crear Pedido al crear y editar …
81005df Épica 0 - Iteración 00-07: registra la Auditoría 04 (AUD-04-001 a 005) …
276b616 Épica 2 - Cierre: corrige tres discrepancias documentales …

$ git log --oneline --reverse -- pedidos/templates/pedidos/pedido_form.html | tail -3
1dd5e91 Refactorización: Implementación del Módulo de Pagos …
4560874 Épica 0 - Iteración 00-07: evita el doble envío …
359893f Épica 0 - Iteración 00-07: verifica en local …

$ git rev-parse --short 4560874^
81005df

$ git diff --stat v1.1-observabilidad 81005df -- pedidos/templates pedidos/static requirements.txt pedidos/migrations
(sin salida)

$ git diff --stat 81005df main -- . ":(exclude)_planificacion" ":(exclude)docs"
 pedidos/templates/pedidos/pedido_form.html | 44 ++++++++++++++++++++++++++++--
 1 file changed, 41 insertions(+), 3 deletions(-)

$ git status --short
(sin salida)
$ git status -sb
## main...origin/main
```

- `4560874` es el primer commit que cambia `pedido_form.html` después de `1dd5e91` (anterior a todo el plan) y `81005df` es su padre: es el commit de `v1.2-capturas`. `81005df` lleva la marca «00-07», pero solo trae documentos.
- Entre `v1.1-observabilidad` y `81005df` no cambian plantillas, `pedidos/static`, `requirements.txt` ni migraciones: el despliegue no necesita `pip`, `collectstatic` ni `migrate`. Los cambios ejecutables de ese tramo son `pedidos/views.py` (01-09), `pedidos/registro.py` (emojis de la 01-07) y comentarios de `settings.py`, `decorators.py` y `eventos.py` (01-08), medidos el 2026-10-27 en el informe de la Auditoría 04.
- Entre `81005df` y la punta de `main` solo cambia `pedido_form.html` (la 00-07).

## Migraciones

- Ninguna.

## Criterios de aceptación

- Ninguno marcado: los cuatro criterios nuevos de la 01-09 dependen del domingo 2026-11-01.

## Decisiones tomadas

- Las del desarrollador del 2026-10-27, copiadas en la evidencia: el orden del domingo, `v1.2-capturas` sobre `81005df` y retroceso a `v1.1-observabilidad`, y el respaldo previo como respaldo semanal de la parte D de la 01-06.
- En la parte B, las pruebas se ejecutan sobre la punta de `main` (con la 00-07), sin `checkout` de `81005df`: la diferencia es solo `pedido_form.html`, que ninguna prueba recorre.

## Pendientes y riesgos

- **La descarga del respaldo puede cortarse** por la recarga a los 2 segundos (AUD-03-002, se corrige en la 04-01). La evidencia indica que, si el volcado queda listado, se descarga desde **Files** y que en la validación (E2) no es motivo de retroceso.
- **El respaldo previo deja un evento `respaldo_generado`** antes de la medición de la parte D de la 01-06: entra en su conteo, y la evidencia pide anotarlo.
- **Contradicción documental sin resolver:** `iteracion-01-09` (sección «Dónde queda el respaldo de emergencia») supone que el nombre del volcado va en UTC, mientras `respaldo.md` (sección 1) dice, medido, que va en hora de Chile. No cambia esta evidencia; se anota para que el desarrollador decida si corrige la iteración.

## Commit sugerido

`Épica 1 - Iteración 01-09: prepara evidencia-01-09 para desplegar v1.2-capturas sobre 81005df el 2026-11-01 y ordena la 00-07 detrás de su validación`
