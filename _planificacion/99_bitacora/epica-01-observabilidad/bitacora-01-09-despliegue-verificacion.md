# Bitácora 01-09 · Verificaciones posteriores al despliegue de `v1.2-capturas`

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** sin cambio de estado: la 01-07, la 01-08, la 01-09 y la Épica 01 siguen Terminadas (2026-11-04). Esta nota complementa y no corrige [bitacora-01-09-despliegue](bitacora-01-09-despliegue.md), que ya está entregada y no se edita (regla 5.4 de `_planificacion/README.md`).

Solo se citan conteos, horas, códigos de estado y rutas sin parámetros (con `<id>` y `<estado>` en lugar de valores). No hay direcciones IP, cadenas de consulta ni líneas crudas de registro, y la carpeta de respaldos solo se nombra, sin ruta. Todas las horas son de Chile, salvo que diga UTC. Los datos vienen de consultas de solo lectura que ejecutó el desarrollador el 2026-11-04 hacia las 01:19; el agente no tiene acceso al servidor y los toma tal como se los entregaron.

## Resumen

Se cierran con datos tres cosas que la bitácora anterior dejó abiertas o como hipótesis: (1) la **ventana del incidente** del `git checkout main` (2026-11-03 23:41 a 2026-11-04 00:09) pasa de «no verificada» a **verificada**: ninguna petición ni línea de la aplicación, y un solo reinicio de uWSGI, el de las 00:11:49; (2) las **8 líneas `root` con `OSError: write error`** quedan clasificadas como desconexiones del cliente (AUD-04-004), sin acción; (3) la hipótesis de **AUD-03-002** (la recarga de la página a los 2 segundos corta la descarga del respaldo) queda **respaldada por dos casos**, sin reproducirla a propósito. Además se anotan una observación para AUD-01-003, el seguimiento de `robots.txt` y la rotación de respaldos.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/99_bitacora/epica-01-observabilidad/bitacora-01-09-despliegue-verificacion.md` | Esta nota |

Los demás archivos de esta ronda (`evidencia-01-09.md`, `respaldo.md`, `auditoria-tecnica.md`, `registro-pendientes.md`) están en [bitacora-00-07-despliegue](../epica-00-blindaje/bitacora-00-07-despliegue.md).

## 1. Ventana del incidente (2026-11-03 23:41 a 2026-11-04 00:09): verificada

Conteos de solo lectura, ejecutados el 2026-11-04 hacia las 01:19:

| Conteo | Ventana consultada | Resultado |
| :----- | :----------------- | :-------- |
| Peticiones en `access.log` | 22:34:11 a 00:12:02 (01:34:11 a 03:12:02 UTC) | **0** |
| Líneas `Starting uWSGI` | desde 2026-11-03 23:30:00 | **1**: la de las 00:11:49. La anterior es del 2026-11-02 15:09:17 |
| Líneas con `nivel=` en `server.log` | 22:34:10 a 00:11:44 | **0** |

**Conclusión:** ninguna petición ni línea de la aplicación en la ventana, y no hubo reinicio entre las 23:41 y el Reload; el código viejo del disco no llegó a servirse. Las tres cifras salen de registros de producción. La ventana consultada es más ancha que la del incidente (empieza en el respaldo de las 22:34 y llega hasta antes del reinicio), así que la cubre completa. Con esto, la inferencia de la bitácora anterior («la web app tenía el código de `v1.1-observabilidad` en memoria») deja de ser necesaria: no hubo peticiones que sirvieran código.

## 2. Las 8 líneas `root` (`OSError: write error`) y AUD-04-004

| # | Fecha y hora | Ruta | Líneas de uWSGI del mismo segundo | Clasificación |
| :- | :----------- | :--- | :-------------------------------- | :------------ |
| 1 | 2026-10-26 12:01:10 | No informada | Solo el `OSError` en `error.log` | Desconexión del cliente (inferencia, por la misma familia) |
| 2 | 2026-10-26 16:53:18 | No informada | Solo el `OSError` en `error.log` | Ídem |
| 3 | 2026-10-27 14:35:49 | No informada | Solo el `OSError` en `error.log` | Ídem. Coincide al minuto con la recarga manual de AUD-04-002 (14:35), sin concluir nada |
| 4 | 2026-10-29 13:46:48 | No informada | Solo el `OSError` en `error.log` | Ídem |
| 5 | 2026-10-31 13:08:48 | No informada | Solo el `OSError` en `error.log` | Ídem |
| 6 | 2026-11-03 11:22:59 | `GET /` | `SIGPIPE` («writing to a closed pipe/socket/fd (probably the client disconnected)») y `Broken pipe` | Desconexión del cliente |
| 7 | 2026-11-03 18:58:48 | `GET /pedido/<id>/cambiar/<estado>/` | `SIGPIPE` y `Broken pipe` | Desconexión del cliente |
| 8 | 2026-11-04 00:12:39 | `GET /base_datos/respaldar_bd/accion/` | `SIGPIPE`, `Broken pipe` y un 499 | Desconexión del cliente |

- **Las 3 últimas (6, 7 y 8)** tienen en el mismo segundo las líneas de uWSGI que describe AUD-04-004: es evidencia directa de que el cliente cerró la conexión.
- **Las 5 primeras** solo tienen el `OSError` en `error.log`: se clasifican por la misma familia, **como inferencia**, no por evidencia directa.
- **Clasificación:** desconexión del cliente (AUD-04-004). **Sin acción.** No se concluye la causa de cada desconexión: la 8 tiene explicación probable (sección 3); las otras 7, no.
- Nota fechada en `auditoria-tecnica.md`.

## 3. AUD-03-002: dos casos que respaldan la hipótesis

AUD-03-002 dice que `respaldar_bd.html` recarga la página 2 s después del clic (`location.reload()`) y que, si `mysqldump` tarda más, la recarga corta la descarga. Con datos de `access.log`:

| Caso | Hora | Respuesta del `GET` a la ruta de descarga | Qué pasó después |
| :--- | :--- | :---------------------------------------- | :--------------- |
| 1: respaldo de la parte A (`respaldo_03-11-2026_22-34-09.sql`) | 2026-11-03 22:34 | **200**, 1.481.608 bytes (igual al tamaño del archivo), en **0,861 s** | La página se recargó 1 s después; sin `ERROR` |
| 2: respaldo de E2 (`respaldo_04-11-2026_00-12-37.sql`) | 2026-11-04 00:12:39 | **499**, 0 bytes, a los **1,994 s**, justo antes de la recarga | `SIGPIPE`, `Broken pipe` y la línea `root` del mismo segundo; el archivo se descargó desde Files y verificó 19 de 19 |

- **Hipótesis respaldada, no reproducida a propósito:** si el respaldo tarda más de ~2 s, la recarga automática de la página corta la descarga. En el caso 1 el volcado tardó menos de 2 s y llegó completo; en el caso 2 tardó casi 2 s y se cortó. Son dos observaciones: respaldan la hipótesis, no la prueban.
- **Corrección:** la 04-01 (retirar la recarga al convertir el enlace en formulario POST). No cambia el destino de AUD-03-002.
- **Inferencia (no comprobada):** la diferencia de 2 s entre el nombre del respaldo de E2 (00:12:37) y el `INFO` (00:12:39), que la bitácora anterior dejó sin explicar, es compatible con la duración de esa petición (1,994 s); en el respaldo de las 22:34:09, con 0,861 s, nombre y registro coincidían al segundo.
- **Por qué no es sistemática la línea `root` ligada a respaldos:** de los dos respaldos de la medición (22:34 y 00:12), solo el segundo cortó la descarga.

## 4. Observación para AUD-01-003 (sin concluir)

El 2026-11-03 a las 18:58:48, un `GET /pedido/<id>/cambiar/<estado>/` terminó en **499** y, **en el mismo segundo**, el navegador repitió la petición y obtuvo **302**. **No se sabe** si la primera alcanzó a ejecutar el cambio de estado. Es una observación, no un hallazgo nuevo: AUD-01-003 ya dice que el cambio de estado modifica datos con `GET`, y su corrección es la 04-01. No se consultó el registro de eventos (`pedido_estado_cambiado`) para esa hora; sería una consulta de solo lectura posible, a decisión del desarrollador.

## 5. Seguimiento de `robots.txt` (AUD-01-020)

El 2026-11-03 a las 14:19 (hora de Chile), un rastreador real (Googlebot) recibió **200** en `/robots.txt`, y otro rastreador también. Eso cubre la parte «un rastreador real recibe 200» del seguimiento de AUD-01-020. **Queda pendiente solo** la tasa diaria de `Broken pipe` a 28 días (parte C2 de la 00-06, 2026-11-20).

## 6. Rotación de respaldos (evidencia para la 06-03, sin hallazgo nuevo)

Entre las 22:34 del 2026-11-03 y las 00:12 del 2026-11-04, el servidor borró los dos respaldos más antiguos (los de las fechas 05-05 y 22-06, día-mes, como se informó), **uno por cada clic**. Es el comportamiento de `limpiar_backups_antiguos` (`mantener=5`) descrito en AUD-02-019 y en `respaldo.md`, sección 1. Se anota como evidencia para la 06-03 (rotación por antigüedad); no se crea hallazgo.

## Migraciones

- Ninguna. Esta nota solo toca documentos `.md`.

## Verificación

- Los tres conteos de la sección 1, la clasificación de la sección 2 y los casos de la sección 3 vienen de registros de producción entregados por el desarrollador: el agente no los pudo comprobar.
- Cálculos del agente: las ventanas y diferencias de tiempo se tomaron de las horas informadas.
- Pruebas: no se ejecutaron; no hay cambios de código. Pantallas: no aplica.
- Sin direcciones IP, cadenas de consulta ni líneas crudas en este archivo.
- Lo que el agente **no** pudo comprobar: la ruta de las líneas 1 a 5 de la sección 2 (no informada), si el cambio de estado de la sección 4 llegó a ejecutarse, y la causa de las desconexiones de las líneas 1 a 7.

## Criterios de aceptación

- [x] La ventana del incidente de la parte D de la evidencia-01-09 está verificada con conteos (sección 1). Sustituye a «no verificada» del 2026-11-04.
- [x] Las 8 líneas `root` están clasificadas (sección 2), sin acción.
- [x] Sin criterios propios nuevos: el cierre de la 01-07, la 01-08, la 01-09 y la Épica 01 no cambia.

## Decisiones tomadas

- **2026-11-04 (desarrollador):** la ventana del incidente pasa a «verificada» con estos conteos, y el respaldo de E2 se descargó desde Files (la descarga automática se cortó).
- **Clasificación de las 5 primeras líneas `root`:** por la misma familia, marcada como inferencia, a pedido del desarrollador.

## Pendientes y riesgos

- **La corrección de AUD-03-002 y AUD-01-003 es de la 04-01.** Hasta entonces, un respaldo que tarde más de ~2 s se corta y hay que bajarlo desde Files, y un `GET` de cambio de estado cortado puede repetirse.
- **Cambio de estado con 499 seguido de 302 (sección 4):** sin saber si se ejecutó; una consulta de solo lectura al registro de eventos de esa hora lo aclararía.
- **Tasa de `Broken pipe` a 28 días:** 2026-11-20.

## Commit sugerido

Va en la bitácora [bitacora-00-07-despliegue](../epica-00-blindaje/bitacora-00-07-despliegue.md), que agrupa esta entrega.
