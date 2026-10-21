# Bitácora 00-03 · Réplica local fiel

- **Fecha:** 2026-10-21
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión (falta la evidencia del desarrollador)

## Resumen

Se crearon `compose.yaml` (MySQL 8.0.46, volumen `mysql_data` externo y configuración de producción, con `sql_mode` incluido), el guion de solo lectura `scripts/diagnostico/paridad_replica.py`, el procedimiento `docs/operacion/replica-local.md` y el pedido `evidencia-00-03.md`. No se ejecutó `docker` ni `mysql`, no se leyó `.env` ni ningún volcado y no se tocó código de la aplicación, `settings.py`, esquema ni plantillas. La restauración, la paridad de MySQL, la comparación de conteos y la revisión de pantallas dependen de la evidencia.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `compose.yaml` | Nuevo (aprobado por el desarrollador). |
| `scripts/diagnostico/paridad_replica.py` | Nuevo (aprobado). Solo lectura, sin filas de datos. |
| `docs/operacion/replica-local.md` | Nuevo. Procedimiento, advertencias y tabla de paridad. |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-03.md` | Nuevo. Seis pedidos al desarrollador. |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-03-replica-local.md` | Estado «En revisión». |
| `_planificacion/10_epicas/epica-02-red-seguridad/definicion-epica-02.md` | Nota para 02-01 sobre el modo estricto en la base de pruebas. |
| `_planificacion/00_producto/auditoria-tecnica.md` | Nota sobre AUD-02-020, sin reescribir el hallazgo. |
| `_planificacion/00_producto/registro-pendientes.md` | Estado, decisiones e historial. |

## Verificación

- **Python del `.venv`:** `.venv/Scripts/python --version` → `Python 3.13.0`.
- **`pip freeze` frente a `requirements.txt`:** comparación de conjuntos, leyendo `requirements.txt` como UTF-16. 21 y 21 paquetes, 0 solo en requirements y 0 solo en local.
- **`paridad_replica.py`:** `py_compile` sin errores. No se ejecutó contra la base: requiere el compose levantado y el permiso del desarrollador.
- **Etiqueta `mysql:8.0.46`:** comprobada por el desarrollador en Docker Hub (publicada el 2026-05-05).
- **Tablas de zona horaria:** producción las tiene cargadas (línea base, sección 5) y el volumen local también (bitácora 00-01 SQL local, sección 5). Por eso `--default-time-zone=UTC` es viable, y la tarea 2 se cumple dejándolas cargadas.
- `python manage.py test pedidos`, `showmigrations` y `check` contra la réplica: pendientes de la evidencia (pasos 5 y 6).

## Migraciones

- Ninguna. Cambio de esquema: Ninguno.

## Criterios de aceptación

- [ ] Tabla de paridad sin «No» sin decisión: escrita. El único «No» (Python 3.13.0) tiene su decisión. Los valores de MySQL se confirman con el paso 4 de la evidencia.
- [ ] `showmigrations` de 0001 a 0006: pendiente de la evidencia.
- [ ] `check` contra la réplica: pendiente.
- [ ] Conteos frente a la línea base: pendiente (paso 5).
- [ ] Pantallas coherentes: pendiente (paso 6).
- [ ] Tiempo de restauración: pendiente (paso 3).
- [x] Procedimiento de refresco escrito: `replica-local.md`, sección 9.

## Decisiones tomadas

- **`sql_mode`:** opción A del desarrollador (2026-10-21), `NO_ENGINE_SUBSTITUTION` igual que producción. La opción C se evalúa en 02-01 (nota en la épica 02 y en AUD-02-020).
- **Variables:** `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT`, aprobadas. El contenedor usa `MYSQL_ROOT_PASSWORD: ${DB_PASSWORD:?}`. Hasta 00-04, la app solo lee `DATABASE_URL`, que se define en la sesión de PowerShell.
- **Contenedor `manzagrafica-mysql`:** nombre nuevo, para no confundirlo con el `mysql` que se quita. El puerto se publica solo en `127.0.0.1`, porque la réplica tiene datos reales.
- **Python 3.13.0 frente a 3.13.1:** se acepta por ser un parche menor (decisión del desarrollador).
- **Guion SQL de 00-01 contra la réplica:** lo ejecuta el agente, con permiso en el momento y el método de la 00-01.
- **Orden de la evidencia:** los conteos se miden antes de abrir pantallas, porque «Estadísticas» escribe en `pedidos_historialbd` (AUD-01-006).

## Propuesta de cambio para `AGENTS.md` (documento protegido; lo edita el desarrollador)

1. **Archivo y sección:** `AGENTS.md`, sección 5, último bloque.
2. **Texto actual:**

   ```text
   # Contenedor MySQL local: PENDIENTE_DESARROLLADOR (comando de `docker run` o archivo compose;
   # se documenta en la iteración 00-03 y en docs/operacion/replica-local.md)
   ```

   **Texto propuesto:**

   ```text
   # Contenedor MySQL local (compose.yaml en la raíz; lo ejecuta el desarrollador)
   docker compose up -d
   docker compose stop
   # Nunca `docker compose down -v` ni `docker volume rm mysql_data`.
   # Réplica de producción y su refresco: docs/operacion/replica-local.md
   ```

3. **Por qué:** cierra el `PENDIENTE_DESARROLLADOR` que la iteración pide cerrar y deja a la vista de cualquier agente la prohibición sobre el volumen. Si no se hace, la sección 5 sigue diciendo que el contenedor no está definido.

## Pendientes y riesgos

- La actualización de 8.0.43 a 8.0.46 sobre `mysql_data` no se puede revertir. El procedimiento recomienda respaldar `manzagrafica_local` antes.
- `DB_PASSWORD` tiene que coincidir con la contraseña de root que ya tiene el volumen.
- La réplica trae los hashes de contraseña y las sesiones de producción: unidades cifradas obligatorias y no usar «Respaldar BD» ni «Restaurar» en la réplica.

## Commit sugerido

`Épica 0 - Iteración 00-03: agrega compose.yaml con MySQL 8.0.46 y modo SQL de producción, el guion de paridad, el procedimiento de réplica local y el pedido de evidencia`
