# Bitácora 00-03 · Réplica local fiel

- **Fecha:** 2026-10-21
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Terminada (evidencia respondida el 2026-10-21; por indicación del desarrollador se consolida en esta bitácora, como en 00-02)

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

## Evidencia de la réplica (2026-10-21)

Respondida por el desarrollador en `evidencia-00-03.md`. El agente no tuvo la contraseña de root ni leyó el volcado: solo recibió las salidas.

- **Cifrado:** D: con «Protección activada» y 100 % cifrada. El disco de Docker está en D: (`docker_data.vhdx`, 40,27 GB). C: queda sin cifrar por decisión informada (nota en RDA-002).
- **Paso al compose:** el contenedor `mysql` montaba `mysql_data` en `/var/lib/mysql`. Se quitó y el volumen siguió listado. `docker compose up -d` levantó `manzagrafica-mysql` con `mysql:8.0.46`. El registro dice «Server upgrade from '80043' to '80046' completed» y «ready for connections». `manzagrafica_local` sigue en la lista de bases.
- **Restauración:** `respaldo_20-10-2026_13-09-17.sql` en `manzagrafica_replica` vacía, en **4,17 s** (`Measure-Command`, 4.173 ms), con 18 tablas. El desarrollador usó `docker exec -e MYSQL_PWD` en vez de la variable del contenedor, que es equivalente y evita el aviso de contraseña en la línea de comandos.
- **Paridad:** 7 de 8 elementos coinciden. Python 3.13.0 frente a 3.13.1 es una diferencia aceptada. `pip freeze` 21/21. El guion terminó con código 1 en su versión anterior. Después se agregó `DIFERENCIAS_ACEPTADAS`: ahora termina con 0 si solo hay diferencias aceptadas, y con 1 si hay alguna no aceptada. Se probó simulando la medición (0 con 3.13.0 y 3.13.1; 1 con 3.12.9 o con `sql_mode` estricto).
- **Django contra la réplica**, con `DATABASE_URL` solo en la sesión del desarrollador (`settings.py`, líneas 111 a 118):
  - `SELECT DATABASE()` dio `manzagrafica_replica`.
  - `showmigrations pedidos`: `0001` a `0006` aplicadas.
  - `check`: 0 problemas.
- **Guion SQL de 00-01:** solo lectura, con `ROLLBACK` al final, medido a las 23:47:09 UTC del 2026-10-21. `base_en_uso` = `manzagrafica_replica`.

### Comparación con la línea base de producción (00-01)

| Elemento | Producción (línea base) | Réplica | Diferencia |
| :------- | :---------------------- | :------ | :--------- |
| `pedidos_historialbd`: filas, primera y última (UTC) | 187 · 2026-02-07 03:41 · 2026-10-20 16:09 | 187 · 2026-02-07 03:41:22 · 2026-10-20 16:09:02 | 0 |
| Días distintos UTC / Chile, máximo por día, días con más de una fila, sobrantes | 121 / 119 · 16 (UTC) y 17 (Chile) · 23 y 24 · 66 y 68 | Iguales | 0 |
| `HistorialBD` en los últimos 7 días | 2 | 1 | −1 (ventana móvil) |
| Clientes | 722 | 718 | −4 |
| Pedidos | 870 | 866 | −4 |
| Ítems de pedido | 850 | 844 | −6 |
| Cotizaciones · ítems de cotización · productos | 25 · 52 · 55 | 25 · 52 · 55 | 0 |
| Pagos | 1.033 | 1.029 | −4 |
| Pedidos por mes en hora de Chile, enero a septiembre | 109, 121, 91, 82, 85, 87, 65, 77, 89 | Iguales | 0 |
| Pedidos de octubre (Chile / UTC) | 64 / 64 | 60 / 60 | −4 |
| Julio y agosto en UTC | 64 · 78 | 64 · 78 | 0 |
| Pedidos del año · con conversión nula | 870 · 0 | 866 · 0 | −4 · 0 |
| `estado_pago` inconsistente | 610 de 870 | 606 de 866 | −4 |
| `PAGADO→PAGADO` · `PARCIAL→PARCIAL` · `PENDIENTE→PENDIENTE` | 234 · 4 · 22 | 234 · 4 · 22 | 0 |
| `PENDIENTE→PAGADO` · `PENDIENTE→PARCIAL` | 563 · 47 | 562 · 44 | −1 · −3 |
| Pedidos con valor $0 | 0 | 0 | 0 |
| MySQL, conjunto de caracteres, colación, zona, modo SQL y tablas de zona horaria | 8.0.46, `utf8mb4`, `utf8mb4_unicode_ci`, UTC/UTC, `NO_ENGINE_SUBSTITUTION`, cargadas | Iguales (conversión de prueba `2026-01-15 09:00:00`) | 0 |
| Tablas · peso total (MB) | 18 · 2,20 | 18 · 2,56 | No comparable (ver abajo) |

**Explicación de las diferencias.** Tu hipótesis se confirma por los datos, pero no por la hora:

- **La hora de la línea base no quedó registrada.** `linea-base-produccion.md` solo dice que se midió el 2026-10-20, y ningún documento del repositorio guarda el `medido_utc` de la sección 0 del guion. Las 23:43 UTC vienen de lo que informó el desarrollador y no se pudieron contrastar.
- **El volcado es de las 16:09:17 UTC** (13:09:17 en hora de Chile). La última fila de `HistorialBD` en la réplica es de las 16:09:02 UTC, 15 segundos antes, y es la misma última fila que tiene la línea base. Eso es coherente con que nadie abrió «Estadísticas» entre el volcado y la medición.
- **Los datos muestran que la línea base es posterior al volcado.** La réplica no tiene ninguna fila que falte en producción. Todas las diferencias son filas de más en producción y caben en un solo patrón:
  - Las 4 diferencias de pedidos caen en octubre de 2026, en hora de Chile y en UTC. Los meses de enero a septiembre son idénticos.
  - Hay 4 pedidos, 4 clientes, 4 pagos y 6 ítems de pedido de más. Son 4 pedidos nuevos, al parecer cada uno con un cliente nuevo y un pago.
  - Los 4 pedidos nuevos quedaron en `PENDIENTE` aunque tienen pagos: 1 debería estar en `PAGADO` y 3 en `PARCIAL`. Por eso la inconsistencia baja exactamente en 4 (610 → 606) y las demás celdas de la matriz no cambian. Esto confirma además que AUD-02-004 sigue ocurriendo con cada pedido nuevo.
  - Cotizaciones, productos y `HistorialBD` no cambian.
- **«Últimos 7 días» (2 → 1)** no es una diferencia de datos. La réplica se midió el 2026-10-21 a las 23:47 UTC y producción el 2026-10-20, así que la ventana de 7 días se corrió y una fila quedó fuera.
- **Conclusión:** todas las diferencias se explican por actividad posterior al volcado. Si la línea base hubiera sido anterior al volcado, la réplica tendría más filas, no menos.

**Peso en MB y filas estimadas: no son comparables.**

- El peso sale de `information_schema.TABLES` y depende de cómo InnoDB dispone las páginas. Una base recién restaurada carga las filas de una sola vez, con otro llenado de páginas y otros índices secundarios que una base que creció con meses de inserciones y borrados. Por eso la réplica pesa 2,56 MB (2,06 de datos y 0,50 de índices) frente a 2,20 MB (1,86 y 0,34) en producción, con menos filas.
- `filas_estimadas` es una estimación de las estadísticas de MySQL, con `information_schema_stats_expiry` = 86400: pueden tener hasta 24 horas. En la réplica se acercan a las cifras exactas (por ejemplo, 1.029 pagos) porque las estadísticas se calcularon al restaurar. En producción estaban muy por debajo (191 pedidos estimados frente a 870 reales). Para comparar volumen se usan las cifras exactas de la sección 3 del guion y el tamaño del volcado.

**Otros datos medidos en la réplica:**

- `auth_user`: 1 usuario, superusuario, en el volcado del 2026-10-20. Es un dato parcial para el pendiente del cliente «Número de usuarios, sus roles y los dispositivos».
- Las tablas de sistema de Django difieren de la línea base solo en estimaciones (`django_content_type` 14 y `django_migrations` 24 en la réplica frente a 9 y 18 estimadas en producción). No hay conteo exacto de esas tablas en la línea base.

**La réplica ya no es idéntica al volcado:** después de la medición, el desarrollador inició sesión (escribe `django_session` y `last_login`) y abrió «Estadísticas» y «Estadísticas BD», que pueden agregar filas a `pedidos_historialbd` (AUD-01-006). Una medición futura de la réplica tiene que considerarlo, o refrescar la réplica antes.

### Pantallas

Revisión del desarrollador: «todo funciona como debería, sin problemas, no hay observaciones». Las pantallas que abrió fueron inicio, estadísticas de pedidos, listado de pedidos, nuevo pedido, trabajo semanal, estadísticas y listado de pagos, y estadísticas de la base. Todas respondieron 200.

### Hallazgo nuevo: AUD-02-022

El primer `runserver` respondió 400 en `/` y `/favicon.ico`, porque `ALLOWED_HOSTS` (`settings.py:43`) solo contiene `manzagrafica.pythonanywhere.com`. El desarrollador agregó el host local de forma temporal en su copia y lo deshizo con `git restore`, sin commitear; `git status` quedó limpio. Se registró como AUD-02-022 (Baja) y la advertencia quedó en el procedimiento, sección 8.

## Criterios de aceptación

- [x] Tabla de paridad sin «No» sin decisión: el único «No» (Python) tiene su decisión y el guion lo marca como aceptado.
- [x] `showmigrations pedidos`: `0001` a `0006` aplicadas, ninguna pendiente.
- [x] `check` contra la réplica: 0 problemas.
- [x] Conteos frente a la línea base: todas las diferencias se explican por actividad posterior al volcado (tabla y explicación arriba).
- [x] Pantallas coherentes con producción: confirmado por el desarrollador.
- [x] Tiempo de restauración: 4,17 s.
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

- **Ampliación de 00-04 (2026-10-21, aprobada por el desarrollador):** (a) `ALLOWED_HOSTS` se lee del entorno, con un valor por defecto local (`localhost` y `127.0.0.1`, nunca `*`); (b) se quita la contraseña fija `'root'` de `DATABASES`. Quedó en la tarea 3 (ampliada), en una tarea 7 nueva y en cuatro criterios nuevos. La línea de «Fuera de alcance» que mandaba `ALLOWED_HOSTS` a 04-02 recibió una nota, sin borrar el texto, y la épica 04 una nota equivalente. **Riesgo para el despliegue de 00-04:** si el servidor no define `ALLOWED_HOSTS` antes, producción responde 400. Quedó como pendiente del desarrollador y como paso de la lista de 00-05.

## Pendientes y riesgos

- La propuesta de cambio de la sección 5 de `AGENTS.md` sigue pendiente de que el desarrollador la aplique.

- La actualización de 8.0.43 a 8.0.46 sobre `mysql_data` no se puede revertir. El procedimiento recomienda respaldar `manzagrafica_local` antes.
- `DB_PASSWORD` tiene que coincidir con la contraseña de root que ya tiene el volumen.
- La réplica trae los hashes de contraseña y las sesiones de producción: unidades cifradas obligatorias y no usar «Respaldar BD» ni «Restaurar» en la réplica.

## Commit sugerido

- Primera entrega: `Épica 0 - Iteración 00-03: agrega compose.yaml con MySQL 8.0.46 y modo SQL de producción, el guion de paridad, el procedimiento de réplica local y el pedido de evidencia`
- Cierre: `Épica 0 - Iteración 00-03: cierra la iteración con la réplica restaurada en 4,17 s, explica los conteos frente a la línea base, registra AUD-02-022 y amplía la 00-04`
