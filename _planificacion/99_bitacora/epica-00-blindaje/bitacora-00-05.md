# Bitácora 00-05 · Protocolo de versionado, despliegue y retroceso

- **Fecha:** 2026-10-21
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión

## Resumen

- **Tarea 1:** el desarrollador eligió el formato `v<fase>.<correlativo>-<propósito>` (consulta con opciones; la propuesta del agente era mantener `fase<N>-<propósito>-AAAA-MM-DD`). La 00-04 se despliega como `v0.1-higiene`.
- **Tareas 2 y 3:** `docs/operacion/despliegue.md` con la convención, la lista de comprobación de 8 puntos y los pasos en PythonAnywhere. Cada comando indica su terminal: PowerShell 7 en el PC, consola Bash o panel de PythonAnywhere.
- **Tarea 4:** `docs/operacion/retroceso.md` con los casos 1 (sin migraciones), 2 (Clase 2, con el orden revertir y después volver el código) y 3 (restaurar el respaldo).
- **Tareas 5 y 6:** paso a paso en `evidencia-00-05.md`, partes A (ensayo en `manzagrafica_replica`) y B (despliegue de 00-04). Ninguna está ejecutada.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `docs/operacion/despliegue.md` | Nuevo (tareas 1 a 3). |
| `docs/operacion/retroceso.md` | Nuevo (tarea 4). |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-05.md` | Nuevo (tareas 5 y 6). |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-05-protocolo-despliegue.md` | Estado y dos criterios marcados. |
| `_planificacion/00_producto/registro-pendientes.md` | Estado, decisión de etiquetas e historial. |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-05.md` | Esta bitácora. |

## Verificación

- `python manage.py check`: «System check identified no issues (0 silenced)».
- `python manage.py makemigrations --check --dry-run`: «No changes detected».
- `python manage.py check --deploy` con `DEBUG=False` en la sesión: 5 advertencias, `security.W004`, `W008`, `W009`, `W012` y `W016`, sin errores. Se corrigen en 04-02 y 04-03. `W009` refleja la clave del `.env` local, que el agente no abrió.
- Migración temporal del ensayo: compilada con `py_compile` en el scratchpad del agente (código 0). No se creó en `pedidos/migrations/`.
- `python manage.py test pedidos`: no aplica, sin pruebas hasta 02-01.
- Revisión de pantallas: no aplica, no se tocaron plantillas.

## Migraciones

- Ninguna versionada. La migración temporal `0007_ensayo_retroceso.py` (Clase 2 esperada: `CREATE TABLE ensayo_retroceso`) la crea y la borra el desarrollador en la parte A. Su SQL de `sqlmigrate` se copia aquí al consolidar la evidencia.

## Criterios de aceptación

- [x] `despliegue.md` con convención, lista y pasos.
- [x] `retroceso.md` con los tres casos en pasos numerados.
- [ ] Ensayo medido en menos de 15 minutos con `showmigrations` igual antes y después: pendiente de la parte A.
- [ ] Migración temporal ausente de `git status` y de `pedidos/migrations/`: pendiente de A6.
- [ ] Etiqueta del despliegue de 00-04 en `git tag -n` y lista completada: pendiente de la parte B.

## Decisiones tomadas

- **Formato de etiquetas:** `v<fase>.<correlativo>-<propósito>`, decisión del desarrollador. El agente fijó como interpretación que el correlativo empieza en `1` en cada fase (`v0.1`, `v1.1`), y que la fecha del despliegue va solo en el mensaje de la etiqueta. Las etiquetas de ensayo empiezan con `ensayo-` y nunca se publican.
- **Se despliega la etiqueta, no la punta de `main`:** `git checkout <etiqueta>` en el servidor (RDA-007: `main` puede tener trabajo sin desplegar). `v0.1-higiene` apunta a `64655f8`, para que los documentos de la 00-05 no viajen en el despliegue de la 00-04.
- **`v0.0-inicial`:** etiqueta sobre el commit que está hoy en producción, como destino de retroceso con nombre.
- **Verificación en tres pantallas:** panel, listado de pedidos y detalle de un pedido. Se excluye «Estadísticas» porque escribe en `pedidos_historialbd` (AUD-01-006).
- **Ensayo sin `mysql`:** el estado de la tabla y de `django_migrations` se comprueba con `manage.py shell -c` (introspección y `MigrationRecorder`), sin consola de MySQL.

## Pendientes y riesgos

- **Correlativo:** en la consulta, el ejemplo de la opción mostraba `v1.0-observabilidad`. Si prefieres que cada fase empiece en `.0`, se cambia una línea de `despliegue.md`, sección 1.
- **Cambios hechos a mano en el servidor:** si `git status` en el servidor muestra archivos modificados, el despliegue se detiene (B4). Hoy no se sabe.
- **`.env` del servidor:** si `DATABASE_URL` no está en el `.env` (puede venir del archivo WSGI), B6 se detiene antes de cambiar nada.
- **El `checkout` borra la captura de `media/pedidos/`:** previsto; B5 lo comprueba antes.
- RDA-007 no cambia: remite el formato a `despliegue.md`.

## Commit sugerido

`Épica 0 - Iteración 00-05: agrega los procedimientos de despliegue y retroceso, etiquetas v<fase>.<correlativo> y la evidencia del ensayo y del despliegue de 00-04`
