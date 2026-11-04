# Bitácora 03 · Operación: disco de Docker de la réplica en C:

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** Documentado. Paréntesis de Operación: no avanza ninguna iteración y no cambia ningún estado.

## Resumen

El desarrollador comprobó que D: tiene BitLocker activo (100 %, protección activada), pero que el disco de datos de Docker (`docker_data.vhdx`, unos 44 GB) está en C:, que no está cifrada. `replica-local.md` dice D:, y la réplica ya tiene datos reales en ese disco. Se registró como AUD-05-002 y se dejaron notas en `replica-local.md`. El traslado del disco (o el cifrado de C:) y el refresco de la réplica se harán al cerrar la Épica 03, sin respaldo nuevo, para no retrasarla. Solo documentos; no se ejecutó ni verificó nada en el equipo del desarrollador.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/00_producto/auditoria-tecnica.md:255` | AUD-05-002 en la Auditoría 05 (Media, Seguridad/Operación, Abierto). AUD-05-001 queda igual. |
| `docs/operacion/replica-local.md:62` | Nota fechada en la sección 2: la comprobación (b) hoy falla. Sin cambiar pasos ni comandos. |
| `docs/operacion/replica-local.md:225` | Nota fechada en la sección 9: remite a AUD-05-002 y dice cuándo se refresca. Sin cambiar pasos ni comandos. |
| `_planificacion/00_producto/registro-pendientes.md:195` | Pendiente de Operación «al cerrar la Épica 03» (sección 3). |
| `_planificacion/00_producto/registro-pendientes.md:196` | Nota de la 03-02: limitación del conteo de pedidos sin ítems en la réplica (sección 3). |
| `_planificacion/00_producto/registro-pendientes.md:303` | Entrada de historial 2026-11-04. |
| `_planificacion/99_bitacora/epica-03-integridad-transaccional/bitacora-03-operacion-replica.md` | Esta bitácora (nueva). |

## Decisiones tomadas

Decisiones del desarrollador del 2026-11-04:

1. D: tiene BitLocker al 100 % y la protección está activada. El disco de datos de Docker está en C:, sin cifrar. Causa probable, **no verificada**: una actualización de Docker Desktop.
2. El traslado del disco a D: (o el cifrado de C:) y el refresco de la réplica con el respaldo del 2026-11-04 00:12:37 se hacen al cerrar la Épica 03, sin respaldo nuevo.
3. AUD-05-001 se queda como está.

## Pendientes y riesgos

- **Riesgo abierto hasta cerrar la Épica 03:** la réplica, con nombres, teléfonos, montos y hashes de contraseña de producción, sigue en un disco sin cifrar. Es una decisión del desarrollador para no retrasar la épica; el hallazgo queda «Abierto».
- **Al trasladar el disco:** comprobar que no queda un `.vhdx` con datos en C: (sugerencia mía, no decidida por el desarrollador).
- **Limitación para la 03-02:** el conteo de pedidos sin ítems se hará sobre la réplica con su último refresco registrado (volcado del 2026-10-25 21:02:34, según `replica-local.md`), más una conversión de prueba del 2026-11-04. No representa el estado actual de producción y debe declararse así.
- **No verificado por el agente:** la ubicación del disco, el estado de BitLocker y la causa. Todo viene de lo que informó el desarrollador.

## Confirmación

- No cambió ningún estado de iteración, de épica ni de hallazgo existente.
- No se tocaron `.claude/`, `AGENTS.md`, código, `pedidos/tests/`, otras secciones de `replica-local.md`, iteraciones ni bitácoras entregadas.
- `git --no-pager status --short` y `git --no-pager diff --stat`: solo los `.md` de la tabla.

## Commit sugerido

`Operación: registra AUD-05-002 (disco de Docker en C: sin cifrar) y el refresco de la réplica`
