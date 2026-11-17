# Bitácora 04-10 · Cierre documental de la redacción (D1 a D4)

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** la 04-10 queda **Pendiente (redactada, decisiones resueltas)**. Solo documentos; sin código, pruebas, `manage.py` ni consultas a la base.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

| # | Resuelta como |
| :- | :------------ |
| D1 | Reutilizar `pedido_eliminado` con la cantidad de pagos en el resumen, **sin migración** (la `0010` queda descartada). |
| D2 | Confirmación escribiendo `ELIMINAR`. |
| D3 | Se exige solo si el pedido tiene pagos. |
| D4 | Si los pagos cambian entre mostrar y confirmar, se compara y se repinta sin borrar. |

## Ajustes

- Iteración: estado, decisiones en tabla (con lo que se descartó), pasos, pruebas, riesgos y retroceso sin las ramas de la migración `0010`. **La 04-10 no crea migración**: se revisaron todos los documentos de la épica y no queda ninguno que lo afirme en su estado vigente (las menciones de la `0010` que sobreviven son notas fechadas de la redacción y dicen que fue descartada o era una opción).
- **Comparación alineada con `RESTAURAR` (04-04):** la 04-04 ya rechazaba `restaurar` en minúsculas (fila 3 de sus pruebas), de modo que el criterio es **coincidencia exacta y sensible a mayúsculas**. Faltaba decir qué pasa con los espacios: en las dos pantallas se ignoran los del inicio y del final (`strip()`). Se agregó a la fila de pruebas de la 04-04 y a la 04-10 (corrección de redacción).
- **Consultas:** la pantalla de confirmación hace **una consulta más** (el agregado de pagos); `AGENTS.md`, sección 11, pide detenerse ante un aumento de consultas por página. Se agregó la medición antes y después (paso 0 y una prueba) y el aviso al desarrollador al ejecutar.
- El cliente **no ha respondido** si el borrado de pagos con el pedido es intencional; la iteración no espera esa respuesta.

## Archivos

`iteracion-04-10-confirmacion-reforzada-al-eliminar-un-pedido-con-pagos.md`, `iteracion-04-04-endurecimiento-de-la-restauracion.md` (una fila de pruebas), `definicion-epica-04.md`, `00_producto/registro-pendientes.md` (por bytes, CRLF intacto) y esta bitácora.
