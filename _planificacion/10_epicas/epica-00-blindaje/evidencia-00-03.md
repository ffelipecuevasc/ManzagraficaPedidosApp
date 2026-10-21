# Evidencia 00-03 · Réplica local fiel

- **Fecha del pedido:** 2026-10-21
- **Pedido por:** Claude Code (Opus 5.5)
- **Criterios que dependen de esta evidencia:** tabla de paridad sin «No» sin decisión; `showmigrations` y `check` contra la réplica; conteos frente a la línea base; pantallas coherentes con producción; tiempo de restauración medido.

> Este archivo existe solo porque el agente no pudo obtener estos datos por su cuenta. Responde solo lo que se pide.

## Qué intentó el agente

| Dato | Qué intentó en local | Por qué se necesita al desarrollador |
| :--- | :------------------- | :----------------------------------- |
| Cifrado de D: y ubicación del disco de Docker | Nada: `manage-bde` requiere una consola de administrador y la ubicación del disco está en la configuración de Docker Desktop. | Solo el desarrollador puede confirmarlo en su máquina. |
| Migración al compose y restauración | Preparó `compose.yaml` y el procedimiento. | Los agentes no ejecutan `docker` ni `mysql` y no leen volcados (`AGENTS.md`, sección 6). |
| Paridad de MySQL | Midió Python (3.13.0) y `pip freeze` (21 y 21, sin diferencias). | Los valores de MySQL solo existen después de levantar el compose. |
| Pantallas coherentes | Nada. | Para comparar con producción hay que verla con datos reales. |

## Qué necesito del desarrollador

Sigue `docs/operacion/replica-local.md`. Hazlo en este orden y no abras la aplicación antes del paso 6.

### 1. Cifrado (comprobación previa obligatoria)

- **Para qué:** advertencia de RDA-002. Sin esta confirmación no se restauran datos reales.
- **Cómo obtenerlo:** sección 2 del procedimiento. Dos comprobaciones: (a) `manage-bde -status D:`, como administrador, debe decir «Protección activada» y 100 % cifrado; (b) el archivo del disco de Docker (`ext4.vhdx`) debe estar en D:.
- **Respuesta (2026-10-21):** (a) D: con «Protección activada» y 100 % cifrada; (b) `D:\Docker\datos\DockerDesktopWSL\disk\docker_data.vhdx` (40,27 GB). Se cumplen las dos.

### 2. Paso al compose

- **Para qué:** contenedor reproducible (tarea 1).
- **Cómo obtenerlo:** sección 3 del procedimiento, pasos 1 a 5.
- **Respuesta (2026-10-21):** se quitó el contenedor `mysql` sin borrar el volumen. `docker compose up -d` levantó `manzagrafica-mysql` (`mysql:8.0.46`). El registro muestra la actualización de 8.0.43 a 8.0.46 completada y «ready for connections». Servidor: 8.0.46, `time_zone` UTC, `sql_mode` `NO_ENGINE_SUBSTITUTION` y colación `utf8mb4_unicode_ci`.

### 3. Restauración medida

- **Para qué:** criterio «tiempo de restauración medido».
- **Cómo obtenerlo:** secciones 4 y 5 del procedimiento, con el volcado `respaldo_20-10-2026_13-09-17.sql` (SHA-256 `0fea064c…d008`, verificado en 00-02).
- **Respuesta (2026-10-21):** `respaldo_20-10-2026_13-09-17.sql` restaurado en `manzagrafica_replica` en **4,17 s**, con 18 tablas.

### 4. Guion de paridad

- **Para qué:** tabla de paridad (tarea 4).
- **Cómo obtenerlo:** secciones 6 y 7 del procedimiento.
- **Respuesta (2026-10-21):** 7 de 8 filas coinciden. La única diferencia es Python 3.13.0 frente a 3.13.1 (aceptada). `pip freeze` 21/21, sin diferencias. Código 1, con la versión anterior del guion.
- **Ajuste posterior:** el guion ahora tiene `DIFERENCIAS_ACEPTADAS` y termina con 0 cuando solo hay diferencias aceptadas («Resultado: PARIDAD con diferencias aceptadas»). Opcional: ejecútalo de nuevo y pega aquí la línea «Resultado» y el código.

### 5. Guion SQL de 00-01 contra la réplica (lo ejecuta el desarrollador)

- **Para qué:** comparar los conteos con la línea base (tarea 6).
- **Por qué lo ejecutas tú:** el agente no tiene la contraseña de root y no debe tenerla.
- **Cómo obtenerlo:** en PowerShell 7, desde la raíz del repositorio y con el compose encendido. El guion solo tiene `SELECT` y `SHOW`. Se envuelve en una transacción de solo lectura que termina con `ROLLBACK`, y la primera línea muestra la base en uso. La contraseña la pone el propio contenedor (`$MYSQL_ROOT_PASSWORD`) y no aparece en tu consola.

  ```powershell
  $sql = "SELECT DATABASE() AS base_en_uso;`nSET SESSION TRANSACTION READ ONLY;`nSTART TRANSACTION;`n" + (Get-Content -Raw -Encoding utf8 scripts\diagnostico\linea_base.sql) + "`nROLLBACK;`n"
  $sql | docker compose exec -T db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" --database=manzagrafica_replica --table'
  ```

  `base_en_uso` tiene que decir `manzagrafica_replica`; si no, detente. El aviso `Using a password on the command line interface can be insecure` es normal. Todos los resultados son agregados (conteos, tamaños, fechas mínimas y máximas), igual que en 00-01.
- **Diferencias esperadas:** el volcado es del 2026-10-20 a las 16:09 UTC y la línea base se midió a las 23:43 UTC del mismo día. Las tablas de negocio pueden tener menos filas en la réplica por la actividad de esas 7,5 horas, y `pedidos_historialbd` puede tener una fila menos si alguien abrió «Estadísticas» en ese intervalo. Además, las secciones con «últimos 7 días» y la antigüedad dependen del momento de la medición.
- **Respuesta:** la salida completa.

### 5b. `showmigrations` y `check` contra la réplica (lo ejecuta el desarrollador)

- **Para qué:** criterios de `showmigrations` (0001 a 0006 aplicadas) y de `check`.
- **Por qué lo ejecutas tú:** para apuntar Django a la réplica sin editar `settings.py`, la única forma es `DATABASE_URL`, que lleva la contraseña. Por eso va en tu sesión y no en la del agente.
- **Cómo obtenerlo:** en una sesión de PowerShell 7 con el `.venv` activo:

  ```powershell
  $env:DATABASE_URL = "mysql://root:<contraseña>@127.0.0.1:3306/manzagrafica_replica"
  python -c "import os, django; os.environ['DJANGO_SETTINGS_MODULE'] = 'PedidosApp.settings'; django.setup(); from django.db import connection; c = connection.cursor(); c.execute('SELECT DATABASE()'); print('Base:', c.fetchone()[0])"
  python manage.py showmigrations pedidos
  python manage.py check
  Remove-Item Env:DATABASE_URL
  ```

  La primera línea de salida tiene que ser `Base: manzagrafica_replica`; si no, detente. `showmigrations` y `check` solo leen. La variable se pierde al cerrar la sesión, y `Remove-Item` la quita antes.
- **Respuesta:** las tres salidas.

### 6. Pantallas

- **Para qué:** criterio de coherencia con producción.
- **Cómo obtenerlo:** sección 8 del procedimiento. Abre el panel de control, el listado de pedidos, el trabajo semanal y el panel financiero. Compáralos con producción teniendo en cuenta que el volcado es del 2026-10-20.
- **Respuesta:** «coherente» o la diferencia que viste, sin datos de clientes (solo conteos o totales).

## Lo que no se pudo verificar

- Paridad de MySQL: confirmada el 2026-10-21 (paso 4).
- Conteos frente a la línea base, `showmigrations`, `check` y pantallas: pendientes de los pasos 5, 5b y 6.
