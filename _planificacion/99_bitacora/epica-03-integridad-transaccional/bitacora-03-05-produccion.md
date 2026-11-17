# Bitácora 03-05 · Producción: despliegue y día 0

- **Fecha:** 2026-11-17 (registra el despliegue del 2026-11-16)
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** la iteración 03-05 queda **En curso (subestado: en vigilancia, día 0 hecho)** (nota del 2026-11-17: «En vigilancia» es un subestado de «En curso»). Esta bitácora queda En revisión. La Épica 03 **no** se marca Terminada: faltan la lectura del día 7 y la limpieza de la réplica. Ningún hallazgo pasa a «Resuelto». Solo documentos: sin cambios de código, sin commit, sin etiqueta y sin tocar PythonAnywhere.

## Resumen

El desarrollador desplegó `v3.1-integridad` la noche del **lunes 2026-11-16**, un día antes de lo reprogramado ([bitacora-03-05-reprogramacion](bitacora-03-05-reprogramacion.md)), con el reinicio efectivo `R` = **23:48:12** (hora de Chile; 2026-11-17 02:48:12 UTC), fuera de la ventana de 20:00 a 23:00 por decisión suya. El día 0 salió sin 500, con `token_envio` en los tres formularios y la línea `INFO` del rechazo verificada. La medición de la 00-07, precondición, se hizo antes y cumple. Apareció un hallazgo ajeno a la Fase 3 (AUD-05-009). Todo lo de abajo es **dicho por el desarrollador, de sus consolas**; el agente no vio ninguna salida.

## Hechos del 2026-11-16 (hora de Chile)

| Paso | Resultado | Dónde queda |
| :--- | :-------- | :---------- |
| 00-07, parte D (A0), hacia las 23:13 | 12 días con registro (2026-11-04 a 2026-11-16), todos con `segundos_repetidos=0`; 2026-11-08 y 2026-11-17 (UTC) con `lineas=0`: sin medir. **Cumple** | [evidencia-00-07](../../10_epicas/epica-00-blindaje/evidencia-00-07.md), parte D |
| Pruebas y comprobaciones en el PC (A1) | 267 pruebas, `OK (expected failures=9)`; `check --deploy` con `W004 W008 W009 W012 W016`; `makemigrations` sin cambios; sin diferencias en migraciones, `requirements.txt` ni `settings.py` | [evidencia-03-05](../../10_epicas/epica-03-integridad-transaccional/evidencia-03-05.md), A1 |
| Respaldo (A2), 23:34:18 | `respaldo_16-11-2026_23-34-18.sql`, 1.525.277 bytes, SHA-256 `74e6e2a352d6b74eac5306edc34def597947bad01c45243abdac08cdeb0c3e1c`, 19 de 19, `VÁLIDO`, código 0 | evidencia A2; `respaldo.md`, sección 6 |
| Etiqueta (A3) | `v3.1-integridad` sobre `7e14398` (objeto `c05a16b8fde34cd5f9438055f9f950e826009e96`); retroceso `v0.3-doble-envio` (objeto `e68f87212245679d68ba8340db46cd9c3218419d`) | evidencia A3 |
| Servidor antes (B2), 23:43:18 | Commit `5dc82a8`, 106 sesiones | evidencia B2 |
| Servidor después (B4 y B5) | `collectstatic` copió 1 archivo; `check` limpio | evidencia B4 y B5 |
| **`R` (B6)** | **2026-11-16 23:48:12** (2026-11-17 02:48:12 UTC) | evidencia B6 |
| C1 | Sin 500; `token_envio` en `/pedidos/nuevo/`, `/cotizaciones/nueva/` y `/pagos/ingresar/` | evidencia C1 |
| C2 | `bloqueado=true` y «Guardando…», en ventana privada (**no prueba el caché**) | evidencia C2 |
| C4, 23:58:23 | Línea `INFO` «Envío sin token válido» verificada; ningún pago creado | evidencia C4; `despliegue.md`, 3.9 |
| C5 | 1 `ERROR` (`root`, `OSError: write error`, 23:55:10, AUD-04-004) y 1 `INFO` | evidencia C5 |
| C6 | Ningún `POST /pedidos/nuevo/`; `pedidos_nuevos`, `eventos_creado`, `eventos_duplicado`, `eventos_convertida` y `grupos_repetidos` en 0 | evidencia C6 |

## Desviaciones

1. **Día:** el despliegue fue el lunes 2026-11-16, no el martes 2026-11-17 reprogramado.
2. **Hora de `R`:** 23:48:12, 48 min después del cierre de la ventana de 20:00 a 23:00 (decisión del desarrollador).
3. **Aviso:** decía 22:30; `R` fue 23:48:12, **1 h 18 min 12 s** después. El cliente fue avisado antes de `R` (dicho). Canal, día y hora del envío: no informados (`PENDIENTE_DESARROLLADOR`).
4. **Comando de A3:** el `git diff --stat` falló en PowerShell y se repitió con comillas. No se informó el error ni el resultado de la repetición; no investigué la causa. Los comandos de la evidencia no se cambiaron.
5. **C2 en ventana privada:** el bloqueo del botón quedó probado, el caché del navegador no. El cliente hará Ctrl+F5 el martes 2026-11-17 de día (dicho).
6. **Salidas no informadas** (quedaron como «No informado» en la evidencia; no se completaron por inferencia): A1 filas 1, 2, 6 y 8; B2 (migraciones, `migrate --plan`, `check --deploy` antes); B3; B4 (`migrate --plan` y `bloquearBoton`); B5 (`check --deploy` después); B6 (clic de Reload y número de reinicios); el mensaje de la etiqueta; D0 de la 00-07 (rotación).

## Hallazgo nuevo: AUD-05-009

`pago_form.html` usa `$(document).ready` antes de que `base.html` cargue jQuery y la consola dice «$ is not defined» (observado por el desarrollador el 2026-11-16; el paso exacto no se informó). El desarrollador verificó que en `v0.3-doble-envio` es idéntico: **no es una regresión de la Fase 3**. Registrado como **Baja, Épica 08** ([auditoria-tecnica](../../00_producto/auditoria-tecnica.md)). Lectura del código, no ejecutada: el script está en `pago_form.html:141-152`, dentro de `{% block content %}`, y `base.html` pinta ese bloque (`:275-276`) antes de cargar jQuery (`:325`); es el único `$(document).ready` de las plantillas. Efecto probable (hipótesis, no probada en pantalla): solo el error en consola, porque `index.js:78-79` ya inicializa `.select2`. No se corrige en la Épica 03.

## Calendario corregido

- **`R` + 7 días** = lunes 2026-11-23 a las 23:48:12 (Chile) = martes 2026-11-24 a las 02:48:12 UTC. **El día 7 se lee desde esa hora, o el martes 2026-11-24.** Reemplaza «martes 2026-11-24 por la noche».
- **Informe C2 de la 00-06, viernes 2026-11-20** (a mitad de la vigilancia): la recarga de `R` (2026-11-17 02:48:12 UTC, con sus unos 10 s de 502, AUD-04-002) entra en sus conteos; se separa usando `R`. El `OSError: write error` de las 23:55:10 (AUD-04-004) también cae en ese periodo.
- **Martes 2026-11-17, de día:** el cliente hace Ctrl+F5 y empieza el uso real. Lectura a demanda como sugerencia, sin decidir.
- **Web app:** renovada hasta el 2026-12-13 (dicho). Fecha de la renovación y fecha para volver a renovar: `PENDIENTE_DESARROLLADOR`.

## Archivos creados o modificados (solo documentos)

- `_planificacion/99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-produccion.md` (nuevo, esta bitácora).
- `_planificacion/10_epicas/epica-03-integridad-transaccional/evidencia-03-05.md`: partes A, B y C rellenadas, desviaciones, calendario vigente (el anterior queda como registro), parte D con la hora corregida, «Respuesta del desarrollador».
- `_planificacion/10_epicas/epica-03-integridad-transaccional/iteracion-03-05-validacion-y-despliegue-de-la-integridad.md`: estado «En curso (subestado: en vigilancia, día 0 hecho)», sección «Ejecución del día 0», criterios, fechas de operación, riesgos y notas.
- `_planificacion/10_epicas/epica-03-integridad-transaccional/definicion-epica-03.md`: nota fechada (la épica no está Terminada).
- `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-07.md` e `iteracion-00-07-correcciones-tempranas-ii.md`: resultado de la medición (sin cerrar la iteración; el cierre vino el 2026-11-17, ver la nota fechada).
- `_planificacion/00_producto/registro-pendientes.md`: cabecera, filas 00-07 y 03-05, informe C2, Épica 08, por confirmar e historial.
- `_planificacion/00_producto/auditoria-tecnica.md`: AUD-05-009 y su nota de origen.
- `docs/operacion/despliegue.md`: fila en la sección 5 y línea `INFO` verificada en 3.9.
- `docs/operacion/respaldo.md`: fila en la sección 6.

No toqué `AGENTS.md`, `DESIGN.md`, `README.md`, `_planificacion/README.md`, el código ni otras bitácoras. Sin nombres de personas.

## Verificación

Solo lectura y comprobaciones de texto; no ejecuté nada de la 03-05, ni pruebas, ni `manage.py`, ni `git` más allá de `status` y `diff`.

- **Tachados:** ninguna línea con `~~` impar en los nueve archivos modificados.
- **Finales de línea:** se conservaron (CRLF en el registro, la auditoría, `despliegue.md`, la iteración 03-05 y la evidencia 03-05; LF en el resto).
- **Nombres de personas:** ninguna línea agregada contiene nombres.
- **Coherencia entre iteración, evidencia y registro:** búsqueda de `martes 2026-11-17`, `martes 2026-11-24`, `2026-11-12`, `2026-11-13`, `2026-11-19`, «jueves» y «vence el 2026-11-20» sobre el texto sin tachar. Lo que queda son notas que nombran la fecha vieja para decir que cambió, la sección «Reprogramación del 2026-11-16» (con una nota que dice que vale «Ejecución del día 0»), las tablas rotuladas como anteriores o superadas y las filas de decisiones ya resueltas. No encontré contradicciones en el texto vigente: despliegue lunes 2026-11-16, `R` 23:48:12, día 7 desde el 2026-11-23 a las 23:48:12 o el 2026-11-24, informe C2 el 2026-11-20 con la recarga de `R`, web app hasta el 2026-12-13.
- **Líneas del código citadas** (`pago_form.html:141-152`, `base.html:275-276`, `:325`, `:331`, `index.js:78-79`, `pago_form.html:80`) leídas en el árbol de trabajo, que corresponde al código de la etiqueta (sin cambios de código desde `7e14398`).

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] Partes A, B y C de la evidencia rellenadas con lo informado; lo no informado queda como «No informado».
- [x] Desviaciones anotadas: día, hora de `R`, aviso con 22:30, `diff` de A3 en PowerShell, C2 en ventana privada.
- [x] Fila en `despliegue.md` (sección 5) y en `respaldo.md` (sección 6); línea `INFO` confirmada en `despliegue.md`, 3.9.
- [x] AUD-05-009 registrado como Baja, Épica 08.
- [x] Calendario corregido: día 7 desde el lunes 2026-11-23 a las 23:48:12 (o el martes 2026-11-24) e informe C2 del 2026-11-20 con la recarga de `R`.
- [x] La 03-05 queda «En curso (subestado: en vigilancia, día 0 hecho)»; la Épica 03 no se marca Terminada; ningún hallazgo pasa a «Resuelto».
- [x] Registro de pendientes actualizado; sin nombres de personas; sin tocar `README.md` ni `DESIGN.md`.

## Decisiones tomadas

- **Del desarrollador (dichas por él):** desplegar el 2026-11-16; `R` fuera de las 20:00 a 23:00; día 7 desde el lunes 2026-11-23 a las 23:48 o el martes 2026-11-24; AUD-05-009 como Baja, Épica 08; estado de la 03-05 y de la Épica 03.
- **Mías, a confirmar:** (1) (superado el 2026-11-17: la 00-07 pasó a Terminada) la 00-07 queda En revisión con su medición anotada y el cierre lo decide el desarrollador (`_planificacion/README.md`, regla 8); (2) (resuelto el 2026-11-17: subestado de «En curso») el estado «En vigilancia» no figura en la lista de estados de `_planificacion/README.md` (`Pendiente`, `En curso`, `Bloqueada`, `En revisión`, `Terminada`, `Descartada`); lo escribí como pediste y, si se quiere mantener, el README (protegido) necesitaría una propuesta; (3) no marqué el respaldo como semanal.

## Nota del 2026-11-17 (decisiones del desarrollador)

Tres decisiones del desarrollador del 2026-11-17 (dichas por él; no verificadas en servidor) ajustan lo anterior. Esta bitácora ya estaba entregada: lo de arriba se conserva como registro y vale esta nota.

1. **00-07 Terminada.** La medición del 2026-11-16 cumple: 12 de 13 días con registro y `segundos_repetidos=0` en todos. Salvedad: el 2026-11-08 (domingo) salió con `lineas=0` y no se sabe si fue falta de uso o de registro. Reemplaza «la 00-07 queda En revisión» y «cerrar o no la 00-07».
2. **«En vigilancia» es un subestado de «En curso».** El estado de la 03-05 es **En curso (subestado: en vigilancia, día 0 hecho)**; no se agrega a la lista de estados de `_planificacion/README.md` (protegido). Donde arriba dice «En vigilancia» como estado, léase así.
3. **La cabecera «Estado: Pendiente» de `definicion-epica-03.md` no se corrige ahora**; se corrige en el cierre de la Épica 03 (pendiente en `registro-pendientes.md`, sección 3).

**Verificado en documentos (2026-11-17):** la lista de estados de `_planificacion/README.md` (línea 72) no incluye «En vigilancia»; la cabecera de `definicion-epica-03.md` dice «Estado: Pendiente»; la de `definicion-epica-00.md` dice «Reabierta el 2026-10-27 solo para la 00-07». **Dicho por el desarrollador:** las tres decisiones y la medición.

## Pendientes y riesgos

- **`PENDIENTE_DESARROLLADOR`:** ~~cerrar o no la 00-07~~ (resuelto el 2026-11-17: Terminada); salidas no informadas (desviación 6); canal, día y hora del aviso; si el semanal de hacia el 2026-11-10 u 11 se hizo; fecha de la renovación de la web app y de la próxima; fuente del respaldo para la réplica (F1); cuántos días conserva la rotación de `access.log` (D0) y por qué el 2026-11-08 salió con `lineas=0`.
- **Riesgo:** el día 0 fue de noche y sin tráfico en `/pedidos/nuevo/`; el criterio de duplicados (iii) solo se pone a prueba con el uso real (día 7 y, si se hace, una lectura a demanda tras el primer uso del martes 2026-11-17).
- **Riesgo:** hasta el Ctrl+F5 del cliente su navegador puede tener el `index.js` anterior (inferido; el caché no se probó).
- **Riesgo:** la medición de la 00-07 cubre 12 de 13 días; el 2026-11-08 queda sin medir (domingo; `lineas=0`: no se sabe si fue falta de uso o de registro).

## Lo que no pude ver ni verificar

- **Todo el servidor y los registros:** las salidas, `server.log`, `access.log`, el estado de GitHub y el panel de PythonAnywhere. Todo lo del 2026-11-16 es dicho por el desarrollador.
- **El texto exacto de la línea `INFO`** y su cabecera: el desarrollador la verificó; no se copió.
- **El mensaje de la etiqueta** (`git tag -n`) y la causa del fallo de PowerShell.
- **El efecto real de AUD-05-009** en pantalla.

## Commit sugerido

`Épica 3 - Iteración 03-05: registra el día 0 de v3.1-integridad (R 2026-11-16 23:48:12), AUD-05-009 y el calendario del día 7; solo documentos`
