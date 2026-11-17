# Bitácora 04-05 · Cierre documental de la redacción (D1 a D4)

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-05 queda **Pendiente (redactada, decisiones resueltas)**. Solo documentos; sin código, pruebas ni `manage.py`.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

| # | Resuelta como |
| :- | :------------ |
| D1 | `TEMPLATES['DIRS']` vacío hasta la 08-02. |
| D2 | Las seis pruebas que parchan `views.settings.BASE_DIR` pasan a `override_settings`, para aislar el cambio. |
| D3 | `conn_health_checks=True`, manteniendo `conn_max_age=60`. |
| D4 | El modo estricto de `sql_mode` sale de la 04-05 y pasa a la Épica 06 como medición. |

## Ajustes

- Iteración: estado, decisiones en tabla, alcance, pasos (las pruebas se migran antes de cambiar `views.py:19`), tabla de Clase 1 con valores esperados, pruebas con las seis rutas, riesgos (alcance de `override_settings` y `DIRS` vacío). **Se conserva** la consulta previa para editar `settings.py` (paso 0).
- AUD-02-020: acción reescrita (medición en la Épica 06) y nota de reasignación; las notas que decían «sigue en 04-05» quedan como historia. `definicion-epica-02.md` e `iteracion-02-01` no se tocan (documentos cerrados).
- `definicion-epica-06.md`: sección nueva para la iteración que mida el modo estricto (sin número asignado).

## Archivos

`iteracion-04-05-correcciones-de-configuracion.md`, `definicion-epica-04.md`, `definicion-epica-06.md`, `00_producto/auditoria-tecnica.md` y `00_producto/registro-pendientes.md` (ambos por bytes, CRLF intacto) y esta bitácora.
