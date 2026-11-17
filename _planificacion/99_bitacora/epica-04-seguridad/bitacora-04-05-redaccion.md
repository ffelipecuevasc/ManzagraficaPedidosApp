# Bitácora 04-05 · Redacción de la iteración

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-05 queda **Pendiente (redactada, decisiones abiertas D1 a D4)**. Solo documentos; sin código, pruebas ni `manage.py`.

## Resumen

Se redactó [iteracion-04-05](../../10_epicas/epica-04-seguridad/iteracion-04-05-correcciones-de-configuracion.md): `django.conf.settings` en `views.py`, `CONN_HEALTH_CHECKS`, `BASE_DIR` único, `TEMPLATES['DIRS']`, importaciones duplicadas o sin uso y código comentado. Clase 1, sin migraciones, con una tabla para comprobar que nada cambia. Orden de despliegue: 04-01 → 04-02 → 04-03 → 04-04 → 04-05.

## Verificación (solo lectura, búsquedas reales)

- `views.py:19` es el único `from PedidosApp import settings`; solo se usa para `BASE_DIR` (`:81`, `:1194`, `:1265`, `:1331`). Seis pruebas parchan `views.settings.BASE_DIR`.
- `settings.py`: `BASE_DIR` en `:21` y `:30`; `DIRS` en `:84` con coma suelta en `:85`; `dj_database_url.config` sin `conn_health_checks` (`:132-136`).
- `views.py:6` (`F` dos veces), `views.py:8` (`HttpResponseForbidden` sin uso), `urls.py:2` (importación redundante), `utils.py:25` (código comentado). Ninguna función sin uso.
- `templates/` existe vacía en la copia de trabajo y no está en Git.
- `es_superusuario` (`views.py:1176`) ya no lleva `@login_required`.

## Contradicciones

1. `views.py:19`: AUD-05-008 lo da a la Épica 08 y AUD-01-009 a la 04-05. Queda en la **04-05** (hallazgo anterior y Alto, plan 4.5, definición alcance 5, es configuración). Anotado en AUD-05-008.
2. AUD-02-020 promete probar el modo estricto «en 04-05»; la definición no lo incluye y no es Clase 1 (D4).
3. La nota H3 de AUD-01-025 está desactualizada (anotado en la auditoría).

## Qué no se pudo ver

- Si producción sufre hoy conexiones muertas tras hibernar (`server.log`).
- El puerto de MySQL en producción (relevante para `utils.py:25`).
- El commit que quitó `@login_required` de `es_superusuario`.
- El efecto exacto de `mock.patch.object` sobre `LazySettings` (inferido; se confirma corriendo la suite).

## Decisiones abiertas

D1 `TEMPLATES['DIRS']`, D2 parches de las pruebas, D3 salud de la conexión, D4 modo estricto. Fila en la sección 3 del registro.

## Archivos

Nuevo `iteracion-04-05-correcciones-de-configuracion.md`; `definicion-epica-04.md`; `00_producto/registro-pendientes.md` (fila, decisiones, propuesta de `TruncMonth`, próximo hito 04-06, historial); `00_producto/auditoria-tecnica.md` (AUD-05-008 y nota de AUD-01-025); esta bitácora.
