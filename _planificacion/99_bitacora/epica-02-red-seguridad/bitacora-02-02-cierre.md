# Bitácora 02-02-cierre · Pruebas de la lógica de dinero: decisiones tras la revisión

- **Fecha:** 2026-10-26
- **Agente:** Claude Code (Claude Opus 5.5)
- **Estado final:** Terminada (la 02-02, con sus 8 criterios de aceptación marcados)

## Resumen

Registra las decisiones del desarrollador del 2026-10-26 tras revisar [bitacora-02-02](bitacora-02-02.md). Antes estaban como sección final de esa bitácora; salen de allí porque la regla 5.4 de `_planificacion/README.md` dice que una bitácora entregada no se edita y que las correcciones van en una bitácora nueva con sufijo. **La regla 5.4 se respeta con este archivo:** `bitacora-02-02.md` quedó idéntica a la del commit `2393f5c`.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-02.md` | Restaurada tal como se entregó (commit `2393f5c`), sin la sección de decisiones |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-02-cierre.md` | Esta bitácora |
| `_planificacion/00_producto/registro-pendientes.md` | Enlace del historial del cierre apuntando aquí; `PENDIENTE_DESARROLLADOR` de AUD-02-025 resuelto |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-02-025: iteración que lo corrige, 06-05 |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-04-regresiones.md` | R15: la corrige la 06-05 |

En el commit `ac70401` ya quedaron: la auditoría con AUD-02-025 y AUD-02-026, la R15 en la 02-04 (17 regresiones previstas), AUD-02-014 en la 02-03, la nota del IVA en AUD-02-015 y la 02-02 terminada.

## Verificación

- `git diff 2393f5c -- _planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-02.md`: sin diferencias.
- Pruebas: no aplica, solo documentación.

## Migraciones

- Ninguna.

## Criterios de aceptación

- No aplica: es un cierre documental. Los criterios de la 02-02 están marcados en su iteración.

## Decisiones tomadas

Decisiones del desarrollador del 2026-10-26.

- **H1 → AUD-02-025** (Baja). Se suma a la 02-04 como regresión R15, que afirma 29 %; recuento previsto de la 02-04: 17. **La corrige la 06-05, junto con AUD-02-015** (resuelto el `PENDIENTE_DESARROLLADOR`).
- **H2 → AUD-02-026** (Baja). Solo auditoría, ligado al dato `PENDIENTE_CLIENTE` del pedido de $0; sin regresión hasta que el cliente responda.
- **D2:** `dashboard` y `estadisticas_pedidos` se mantienen en la 02-02.
- **AUD-02-014** (valor de la cotización neto o con IVA): lo fija la 02-03 en la conversión de cotización, con `PENDIENTE_CLIENTE`.
- **IVA con diferencias de $1** (150, 350 y 4.950; 500 valores entre 0 y 100.000): solo anotado (D1), como nota de AUD-02-015 en `auditoria-tecnica.md`.
- Las notas H1 y H2 salen de la sección 4 de `registro-pendientes.md`; el historial lo registra.
- La sección de decisiones pasa de `bitacora-02-02.md` a este archivo (regla 5.4).

## Pendientes y riesgos

- Ninguno nuevo.

## Commit sugerido

`Épica 2 - Iteración 02-02: mueve las decisiones de la revisión a bitacora-02-02-cierre.md (regla 5.4) y asigna AUD-02-025 a la 06-05`
