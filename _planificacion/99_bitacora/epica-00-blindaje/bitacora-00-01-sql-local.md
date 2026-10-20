# Bitácora 00-01 · Línea base de producción (ejecución del SQL en local)

- **Fecha:** 2026-10-20
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (sigue pendiente la evidencia de producción)

## Resumen

Con el MySQL local encendido y el permiso del desarrollador, se ejecutó `scripts/diagnostico/linea_base.sql` contra `manzagrafica_local`. Las 14 sentencias corrieron sin errores. Esto cierra el criterio «el guion SQL se ejecuta sin errores contra el MySQL local» que `bitacora-00-01.md` dejó «sin ejecutar». Los valores obtenidos son de la base de desarrollo, no de producción, y no entran en `linea-base-produccion.md`.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-01-sql-local.md` | Esta bitácora. |
| `_planificacion/00_producto/registro-pendientes.md` | Enlace a esta bitácora, pendiente resuelto e historial. |

No se modificó el guion ni ningún otro archivo del repositorio.

## Verificación

- **Cómo se ejecutó:** script temporal de Python en el scratchpad (fuera del repositorio) con `mysqlclient` del `.venv`. Conexión explícita a `127.0.0.1:3306`, usuario `root` de desarrollo, base `manzagrafica_local`; comprobó que `DATABASE()` fuera esa base antes de seguir y activó `SET SESSION TRANSACTION READ ONLY`. No se usó `mysql`, `mysqldump` ni `dbshell`. Al terminar se hizo `rollback` y se cerró la conexión.
- **Servidor local:** MySQL 8.0.43, conjunto de caracteres `utf8mb4`, colación `utf8mb4_unicode_ci`, `@@time_zone` = `SYSTEM`, `@@system_time_zone` = `UTC`.
- **Resultado:** 14 sentencias, 0 errores, 14 resultados con las secciones esperadas (`0`, `1a`, `1b`, `2a`, `2b`, `2c`, `3`, `4`, `5`, `6a`, `6b`, `6c`, `7a`, `7b`). Ninguna tabla ni columna faltó, así que no hace falta ninguna migración.

Resultados relevantes de la base local (datos de desarrollo):

| Sección | Resultado |
| :------ | :-------- |
| 1a y 1b `HistorialBD` | 14 filas en 7 días en UTC y 6 en hora de Chile; máximo de 4 filas en un mismo día. |
| 2a peso | 18 tablas, 0,63 MB (datos más índices). |
| 2c | `information_schema_stats_expiry` = 86400. |
| 3 filas | 2 clientes, 13 pedidos, 16 ítems de pedido, 5 cotizaciones, 8 ítems de cotización, 7 productos y 13 pagos. |
| 5 zona horaria | Tablas cargadas: sí (`2026-01-15 09:00:00`, el valor esperado). |
| 6c gráfico anual | Con datos: sí (13 pedidos del año, 0 con conversión nula). |
| 7a `estado_pago` | 0 inconsistentes sobre 13 pedidos (matriz diagonal: 1 pagado, 6 parciales, 6 pendientes). |

Observaciones:

- Las filas por día de `HistorialBD` reproducen en local el patrón de AUD-01-006 (varias filas en un mismo día). Es evidencia local; la confirmación sigue siendo la de producción.
- La sección 2b muestra 3 cotizaciones y 6 ítems de cotización, y la sección 3 muestra 5 y 8. Es la diferencia esperada entre la estimación de InnoDB y el conteo exacto, por la caché de estadísticas de 24 horas (2c). Por eso el guion pide ambas y las diferencia.
- La paridad con producción (versión, colación, `sql_mode`) se compara cuando llegue la evidencia: la colación local es `utf8mb4_unicode_ci`.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] El guion SQL se ejecuta sin errores contra el MySQL local antes de entregarlo (14 de 14 sentencias, ejecución en modo solo lectura).
- [ ] Los demás criterios siguen como en `bitacora-00-01.md`: dependen de la evidencia de producción.

## Decisiones tomadas

Comunicadas por el desarrollador el 2026-10-20 y que aplican a la tarea 6:

- Acepta la corrección de la regla 6 de `AGENTS.md` sobre `__year`, ya aplicada por él. En la tarea 6, la aclaración sobre `__year` y AUD-02-007 va en `bitacora-00-01-produccion.md`, sin reescribir la auditoría.
- La carpeta externa de respaldos queda fuera del repositorio y el agente no la lee.
- La medición de producción se hará en una sola sesión, con revisión de la CPU entre pasos.
- Si un guion fallara por tablas inexistentes, el agente informa antes de proponer cualquier migración. No ocurrió.

## Pendientes y riesgos

- Tarea 6 sin hacer: consolidar `linea-base-produccion.md`, escribir `bitacora-00-01-produccion.md` y anotar lo medido en AUD-01-006, AUD-02-004, AUD-02-007 y AUD-02-010.
- El `.sh` y los fragmentos de clave y registros siguen probados solo con simulaciones.

## Commit sugerido

`Épica 0 - Iteración 00-01: registra la ejecución local del guion SQL de línea base (14 sentencias, sin errores)`
