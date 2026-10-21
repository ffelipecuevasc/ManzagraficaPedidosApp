# Evidencia 00-03 · Réplica local fiel

- **Fecha del pedido:** 2026-10-21
- **Pedido por:** Claude Code (Opus 5.5)
- **Criterios que dependen de esta evidencia:** tabla de paridad sin «No» sin decisión; `showmigrations` y `check` contra la réplica; conteos frente a la línea base; pantallas coherentes con producción; tiempo de restauración medido.

> Este archivo existe solo porque el agente no pudo obtener estos datos por su cuenta. Responde solo lo que se pide.

## Qué intentó el agente

| Dato | Qué intentó en local | Por qué se necesita al desarrollador |
| :--- | :------------------- | :----------------------------------- |
| Cifrado de C: y D: | Nada: `manage-bde` requiere una consola de administrador. | Solo el desarrollador puede confirmarlo con permisos de administrador. |
| Migración al compose y restauración | Preparó `compose.yaml` y el procedimiento. | Los agentes no ejecutan `docker` ni `mysql` y no leen volcados (`AGENTS.md`, sección 6). |
| Paridad de MySQL | Midió Python (3.13.0) y `pip freeze` (21 y 21, sin diferencias). | Los valores de MySQL solo existen después de levantar el compose. |
| Pantallas coherentes | Nada. | Para comparar con producción hay que verla con datos reales. |

## Qué necesito del desarrollador

Sigue `docs/operacion/replica-local.md`. Hazlo en este orden y no abras la aplicación antes del paso 6.

### 1. Cifrado (comprobación previa obligatoria)

- **Para qué:** advertencia de RDA-002. Sin esta confirmación no se restauran datos reales.
- **Cómo obtenerlo:** sección 2 del procedimiento (`manage-bde -status D:` y `manage-bde -status C:`, como administrador).
- **Respuesta:** (para cada unidad, solo la línea «Estado de protección»)

### 2. Paso al compose

- **Para qué:** contenedor reproducible (tarea 1).
- **Cómo obtenerlo:** sección 3 del procedimiento, pasos 1 a 5.
- **Respuesta:** la salida del paso 2 (montajes), confirmación de que `mysql_data` sigue listado después del `docker rm` y la salida del paso 5 sin cambios (lista de bases, versión, zona y modo).

### 3. Restauración medida

- **Para qué:** criterio «tiempo de restauración medido».
- **Cómo obtenerlo:** secciones 4 y 5 del procedimiento, con el volcado `respaldo_20-10-2026_13-09-17.sql` (SHA-256 `0fea064c…d008`, verificado en 00-02).
- **Respuesta:** la línea `Código: … · Segundos: …`, si apareció algún `ERROR` (solo el código, sin el texto del volcado), la lista de bases y el conteo de tablas del paso 3 (se esperan 18).

### 4. Guion de paridad

- **Para qué:** tabla de paridad (tarea 4).
- **Cómo obtenerlo:** secciones 6 y 7 del procedimiento.
- **Respuesta:** la salida completa del guion y `$LASTEXITCODE`. Se espera código 1 solo por la versión de Python. La línea «Base medida» tiene que decir `manzagrafica_replica`.

### 5. Permiso para que el agente ejecute el guion SQL de 00-01 contra la réplica

- **Para qué:** comparar los conteos con la línea base (tarea 6).
- **Cómo lo hace el agente:** con el mismo método de la 00-01. Un script temporal de Python en el scratchpad, con `mysqlclient` del `.venv`, se conecta a `127.0.0.1:3306` con el usuario `root` y la base `manzagrafica_replica`. Comprueba `DATABASE()` antes de seguir, usa `SET SESSION TRANSACTION READ ONLY` y hace `rollback` al final. Solo muestra resultados agregados, nunca filas de clientes. Luego ejecuta `showmigrations pedidos` y `check` con `DATABASE_URL` apuntando a la réplica.
- **Necesito:** tu permiso en el momento y la contraseña por la vía que prefieras (por ejemplo, `$env:DATABASE_URL` en la sesión del agente). El agente no lee `.env`.
- **Diferencias esperadas:** el volcado es del 2026-10-20 a las 16:09 UTC y la línea base se midió a las 23:43 UTC del mismo día. Las tablas de negocio pueden tener menos filas en la réplica por la actividad de esas 7,5 horas, y `pedidos_historialbd` puede tener una fila menos si alguien abrió «Estadísticas» en ese intervalo.
- **Respuesta:** «autorizado» o «no autorizado».

### 6. Pantallas

- **Para qué:** criterio de coherencia con producción.
- **Cómo obtenerlo:** sección 8 del procedimiento. Abre el panel de control, el listado de pedidos, el trabajo semanal y el panel financiero. Compáralos con producción teniendo en cuenta que el volcado es del 2026-10-20.
- **Respuesta:** «coherente» o la diferencia que viste, sin datos de clientes (solo conteos o totales).

## Lo que no se pudo verificar

- Todo lo de MySQL en la tabla de paridad, salvo Python y `pip freeze`, queda como valor esperado hasta que respondas el paso 4.
