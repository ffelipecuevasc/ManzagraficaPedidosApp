# Bitácora 03 · Alineación documental previa

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión

## Resumen

Antes de abrir la Épica 03 se alinearon tres inconsistencias entre documentos, según la verificación de solo lectura del mismo día y tres decisiones del desarrollador: el cierre de AUD-01-002 (03-02 o 03-03), la iteración de la regresión R21 (02-04 o 03-04) y la precondición de la Épica 03. Todo con notas fechadas, sin reescribir hallazgos ni historial. Sin cambios de código ni de pruebas. La Épica 03 sigue «Pendiente» y no se cambió el estado de ninguna iteración.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `00_producto/auditoria-tecnica.md:24` | AUD-01-002: nota 2026-11-04. Se cierra en la 03-03 con R1, R2 y R4; la 03-02 queda como avance; el avance de la 01-09 ya está en producción con `v1.2-capturas`. |
| `00_producto/auditoria-tecnica.md:73` | AUD-02-008: nota 2026-11-04. La 03-01 es caso de estudio; el cierre va con R3 en la 03-03. |
| `10_epicas/epica-01-observabilidad/definicion-epica-01.md:95` | Nota 2026-11-04: AUD-01-002 se cierra en la 03-03. |
| `10_epicas/epica-01-observabilidad/iteracion-01-09-capturas-amplias.md:8` | Nota 2026-11-04: AUD-01-002 se cierra en la 03-03. |
| `10_epicas/epica-01-observabilidad/iteracion-01-09-capturas-amplias.md:141` | Nota 2026-11-04 en la columna de mitigación. |
| `10_epicas/epica-03-integridad-transaccional/definicion-epica-03.md:6` | Remite a la nota del 2026-11-04 (sección «Notas») como precondición vigente. |
| `10_epicas/epica-03-integridad-transaccional/definicion-epica-03.md:7` | «Última revisión» pasa a 2026-11-04 y conserva la anterior. |
| `10_epicas/epica-03-integridad-transaccional/definicion-epica-03.md:22` | ~~02-04~~ 03-04 en R21, con nota fechada. |
| `00_producto/registro-pendientes.md:43` | Fila 03-01: se suma «00-07 desplegada y validada (cumplido el 2026-11-04)» en «Depende de». |
| `00_producto/registro-pendientes.md:295` | Entrada de historial 2026-11-04 con las tres decisiones. |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-alineacion-previa.md` | Esta bitácora (nueva). |

## Verificación

- Antes de cada edición se reconfirmó la línea citada en la verificación previa: todas coincidían.
- `git --no-pager status --short` y `git --no-pager diff --stat`: solo los archivos `.md` de la tabla.
- Pruebas: no se ejecutaron (sin cambios de código).
- Revisión de pantallas: no aplica.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] AUD-01-002 y AUD-02-008 con nota fechada de cierre en la 03-03 (`auditoria-tecnica.md:24` y `:73`).
- [x] Notas en `definicion-epica-01.md:95` e `iteracion-01-09-capturas-amplias.md:8` y `:141`, sin borrar el texto anterior.
- [x] R21 en la 03-04 (`definicion-epica-03.md:22`), «Última revisión» y precondición actualizadas (`:6` y `:7`).
- [x] Fila 03-01 e historial del registro actualizados; el historial anterior (`:279` y `:289`) no se editó.

## Decisiones tomadas

Decisiones del desarrollador del 2026-11-04:

1. AUD-01-002 se cierra en la 03-03, junto con R1, R2 y R4; la 03-02 queda como avance.
2. R21 va en la 03-04; «02-04» era un error.
3. Precondición: se actualizan los textos vigentes y el historial no se edita.

## Pendientes y riesgos

- `docs/operacion/pruebas.md` §7.1 y los comentarios de `test_regresiones.py` ya decían 03-03 y no se tocaron. `iteracion-02-04-regresiones.md:35` y `:36` siguen diciendo «03-02 / 03-03» para R1 y R2: está fuera del alcance de este cambio y queda como diferencia conocida.
- `plan-de-trabajo.md:321` y `:676` no mencionan la 00-07 en la precondición de la Fase 3. No se tocaron.

## Commit sugerido

`Épica 3 - Alineación documental previa: AUD-01-002 se cierra en la 03-03, R21 pasa a la 03-04 y la precondición de la Épica 03 queda vigente`
