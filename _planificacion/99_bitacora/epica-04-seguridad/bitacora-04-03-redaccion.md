# Bitácora 04-03 · Redacción de la iteración

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-03 queda **Pendiente (redactada, decisiones abiertas D1 a D5)**. Solo documentos; sin código, pruebas ni `manage.py`.

## Resumen

Se redactó [iteracion-04-03](../../10_epicas/epica-04-seguridad/iteracion-04-03-credenciales-y-secretos.md): contraseña fuera de los argumentos de `mysqldump` y `mysql`, clave secreta obligatoria coordinada con la variable y la regla de arranque de la 04-02, revisión del historial sin reescribirlo y registro de quién tiene acceso al panel. Orden de despliegue: 04-01 → 04-02 → 04-03.

## Verificación (solo lectura, sin mostrar valores)

- `pedidos/utils.py`: `--password=` en `:48` (`mysqldump`) y `:117` (`mysql`).
- `settings.py:37`: `SECRET_KEY` sin comprobación.
- `git log -S` y `-G` (solo commits, sin valores): la clave literal está en `713260c` y sale en `c9d58cc`; una contraseña literal de la base local está en `settings.py` desde `08a1a44` hasta `da0cbcd`; `.idea/dataSources.xml` (`08a1a44`, retirado en `965227d`) solo trae la URL de conexión.
- `auditoria-tecnica.md` (AUD-02-010, medido en la 00-01: la clave de producción no coincide; AUD-04-002), `bitacora-00-01.md` (método de hash sin revelar la clave), `definicion-epica-04.md`, `definicion-epica-13.md` (13-02), `replica-local.md`, `despliegue.md`.

## Qué no se pudo ver

- Si la contraseña local del historial coincide con la de producción o con la local actual.
- Coincidencias del patrón `mysql://usuario:clave@` en commits de documentación (`cfe5e26`, `27f7ff9`, `da0cbcd`): la revisión automática fue **denegada por permisos**; probablemente ejemplos, no verificado.
- Si dos de las tres líneas con `PASSWORD` de `compose.yaml` son literales (solo una usa `${…}`).
- La visibilidad real de los argumentos en el servidor de PythonAnywhere, si ofrece verificación en dos pasos y quién tiene hoy las credenciales del panel.
- El efecto de rotar la clave en las sesiones: inferido de la documentación de Django, no probado.

## Decisiones abiertas

D1 cómo recibe la contraseña el cliente de MySQL; D2 cuándo se exige la clave; D3 rotar o no la clave de producción; D4 qué hacer con la contraseña local del historial; D5 credenciales del panel. Fila en la sección 3 del registro.

## Archivos

Nuevo `iteracion-04-03-credenciales-y-secretos.md`; `definicion-epica-04.md`; `00_producto/registro-pendientes.md` (fila, decisiones, próximo hito 04-04, historial); esta bitácora.
