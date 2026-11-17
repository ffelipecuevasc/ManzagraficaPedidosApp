# Bitácora 04-03 · Cierre documental de la redacción (D1 a D5)

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-03 queda **Pendiente (redactada, decisiones resueltas)**. Solo documentos; ningún valor de clave ni contraseña escrito.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

| # | Resuelta como |
| :- | :------------ |
| D1 | `--defaults-extra-file` temporal para `mysqldump` y `mysql`, borrado siempre en `finally`. |
| D2 | `SECRET_KEY` obligatoria; con `SEGURIDAD_PRODUCCION` activa se rechazan `django-insecure-` y las cortas. |
| D3 | Sin rotación ahora (la 00-01 midió que la clave de producción no coincide con la expuesta). |
| D4 | Riesgo aceptado y documentado para la contraseña local del historial (`08a1a44` a `da0cbcd`). **Dicho por el desarrollador, no verificado por el agente:** comparó producción y desarrollo y no coinciden. Nunca se reescribe el historial. |
| D5 | Solo registro por rol de quién accede al panel; contraseñas y verificación en dos pasos fuera del alcance (13-02). |
| Variable | `SEGURIDAD_PRODUCCION`, unificada en la 04-02, la 04-03, el registro y las bitácoras. |

## Ajustes en la iteración

- Alcance, pasos, pruebas, verificación, retroceso, criterio y riesgos reescritos según D1 a D5: sin rotación que deshacer; prueba de que el archivo de opciones no existe después de la llamada, también ante `CalledProcessError` y `FileNotFoundError`; riesgo nuevo del archivo huérfano si el proceso muere entre crearlo y borrarlo.
- Inferido, se confirma en la réplica: `--defaults-extra-file` debe ser el primer argumento.

## Archivos

`iteracion-04-03-credenciales-y-secretos.md`, `iteracion-04-02-configuracion-de-produccion.md` (nombre de la variable), `definicion-epica-04.md`, `00_producto/registro-pendientes.md` (editado por bytes, CRLF intacto), `bitacora-04-02-cierre.md`, `bitacora-04-03-redaccion.md` y esta bitácora.
