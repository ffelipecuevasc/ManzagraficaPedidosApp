# Bitácora 03-05 · Reprogramación del despliegue

- **Fecha:** 2026-11-16
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (la reprogramación). La iteración 03-05 sigue «Pendiente (redactada, decisiones resueltas)»: **no se ejecutó nada de ella**. La Épica 03 no cambia de estado. Solo documentos: sin cambios de código, de pruebas ni de plantillas, sin commit, sin etiqueta y sin tocar PythonAnywhere.

## Resumen

El despliegue de la 03-05 previsto para el jueves 2026-11-12 no se hizo, y la medición de `access.log` de la 00-07, que era su precondición, tampoco. El desarrollador decidió el 2026-11-16 una ventana nueva: **martes 2026-11-17, de 20:00 a 23:00 (hora de Chile)**, con el día 7 el **martes 2026-11-24** por la noche; las demás decisiones no cambian. También dijo que la web app vence el **2026-12-13** y no el 2026-11-20 que decían los documentos (el 2026-11-20 queda solo para el informe C2). Se actualizaron la iteración, su evidencia, la evidencia de la 00-07 (cuyo guion de medición no servía con más de siete días) y el registro, con notas fechadas y sin borrar lo anterior.

## Hechos del 2026-11-16

| Hecho | Fuente |
| :---- | :----- |
| La etiqueta `v3.1-integridad` no existe y no hay commits posteriores a `a1653dd` (2026-11-06): el despliegue del 11-12 no se hizo | Verificado en GitHub, dicho por el desarrollador. En local lo confirmé: `HEAD` es `a1653dd`, `git log a1653dd..HEAD` no lista nada y `git diff --stat 7e14398..HEAD` (sin `_planificacion` ni `docs`) no da salida |
| La medición de la 00-07 no se hizo | Dicho por el desarrollador |
| La web app vence el 2026-12-13 | Dicho por el desarrollador; no visto en el panel |
| Producción sigue en `v0.3-doble-envio` | **Por confirmar por el desarrollador en el servidor** (`git status` y `Starting uWSGI`). `PENDIENTE_DESARROLLADOR` |

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-05-validacion-y-despliegue-de-la-integridad.md` | Estado, «Depende de» y «Etiqueta y ventana» con las fechas nuevas; sección nueva «Reprogramación del 2026-11-16»; decisión 3 y «Decisiones del desarrollador» (3 y R2) con nota fechada, sin borrar lo anterior; tareas 0, 4 y 7 y criterios; tabla «Fechas de operación» con las vigentes y las anteriores conservadas; riesgos (el del 11-20 superado y cuatro nuevos); «No pude ver»; aviso 10 |
| `10_epicas/epica-03-integridad-transaccional/evidencia-03-05.md` | Estado, tabla de decisiones, calendario del 2026-11-16 al 2026-11-25 (el anterior se conserva), precondiciones A0 y cuenta de días, fecha del respaldo semanal (A2), aviso (A4), lectura a demanda (C7), día 7 (parte D) y «Lo que no se pudo verificar» |
| `10_epicas/epica-00-blindaje/evidencia-00-07.md` | Nota fechada de cabecera; parte D reprogramada y **guion ajustado** (D0, D1 y D2); el guion original se conserva como referencia; fecha de medición y casillas con la tachadura y la fecha nueva |
| `10_epicas/epica-00-blindaje/iteracion-00-07-correcciones-tempranas-ii.md` | Estado y criterio de la medición: nota fechada |
| `00_producto/registro-pendientes.md` | Cabecera (última actualización, iteración activa, próximo hito y «Fechas vigentes», con las anteriores tachadas), estado de épicas, filas 00-07 y 03-05 de la sección 1, tres filas de la sección 3 (C2, renovación de la web app, nueva fila «Por confirmar tras la reprogramación») y una fila de historial |
| `00_producto/linea-base-produccion.md` | Nota fechada junto a la fecha de expiración de la web app (la medición del 2026-10-20 no se reescribe) |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-reprogramacion.md` | Esta bitácora (nueva) |

No se tocaron `AGENTS.md`, `DESIGN.md`, `README.md`, `_planificacion/README.md`, código, plantillas, pruebas, `despliegue.md`, `retroceso.md`, `respaldo.md`, `pruebas.md` ni bitácoras anteriores (no se editan después de entregadas).

## La medición de la 00-07: qué se ajustó y por qué

El guion de la parte D recorría `for i in 7 6 5 4 3 2 1 0`: los **8 últimos días UTC contados desde hoy**. Con el reinicio efectivo del 2026-11-04 (01:32:51 de Chile, 04:32:51 UTC), medir el 2026-11-16 o el 11-17 son 12 o 13 días, y el guion habría dejado fuera del 11-04 al 11-08 (o al 11-09): justo los primeros días después del despliegue, sin avisar. Cambios:

- Parte de la fecha UTC del despliegue (`INI=2026-11-04`) y llega hasta la fecha UTC de hoy (`N` se calcula solo; desde las 21:00 de Chile la fecha UTC ya es la del día siguiente).
- Agrega `lineas=` por día para distinguir un día sin `POST` de un día sin registro, y D0 (`ls -l` de los archivos de `access.log`: nombres, tamaños y fechas) para ver si la rotación cubre todos los días.
- Lee los archivos una vez por día (14 lecturas en lugar de 8; CPU no medida) y agrega D2, que solo se corre si el 2026-11-04 sale con segundos repetidos: imprime las horas UTC para separar lo anterior a 04:32:51.
- Sigue sin imprimir IP, cadena de consulta ni datos de clientes.
- **Cuándo:** hoy por la noche o el 2026-11-17 durante el día, **antes de empezar cualquier paso de la 03-05** (parte A1). El límite duro es el Reload del despliegue (B6): después de él, el día UTC del 11-17 mezclaría la 03-05, con la que un envío repetido también responde 302.
- «Una semana» pasa a 12 o 13 días. Medir más días hace el criterio más exigente, no menos; el criterio de la 00-07 queda con una nota fechada.

## Verificación

Solo lectura y pruebas del guion en el scratchpad. No se ejecutaron pruebas del proyecto, `check`, `makemigrations`, `docker`, `mysql` ni `manage.py`, ni nada de la 03-05.

- **Guion de la medición, con registros sintéticos** (14 días, un archivo actual, uno rotado sin comprimir y uno `.gz`, IP inventada; GNU `date`, `grep`, `sed` y `awk` de Git Bash): imprime una línea por día del 2026-11-04 al 2026-11-17 con `lineas`, `post_nuevo`, `segundos_repetidos` y `envios_extra`; detecta un segundo repetido en el primer día y en uno intermedio, y D2 lista la hora de ese segundo. No se probó contra el servidor ni contra el formato real de `access.log` (se supone el mismo que usa la parte D original).
- **Días de la semana** calculados con Python: 2026-11-16 lunes, 11-17 martes, 11-24 martes, 11-18 miércoles, 11-23 lunes y 12-13 domingo.
- **Git, solo lectura:** `git log -1` → `a1653dd`; `git log a1653dd..HEAD` → 0 commits; `git diff --stat 7e14398..HEAD -- . ":(exclude)_planificacion" ":(exclude)docs"` → sin salida.
- **Coherencia entre iteración, evidencia y registro:** una búsqueda sobre las tres, quitando lo tachado, de `2026-11-10`, `-11`, `-12`, `-13`, `-19`, `-20`, «jueves» y «vence». Lo que queda sin tachar son: (a) las notas nuevas que nombran la fecha vieja para decir que cambió; (b) las tablas de opciones y las filas ya resueltas del 2026-11-06, que la iteración declara «registro de las opciones» y que llevan una nota de reprogramación (decisión 3, R2, fila 198 del registro); (c) las tablas «Anteriores» y «Calendario anterior», rotuladas como superadas; (d) el historial del registro, que no se reescribe. No encontré contradicción en el texto vigente: despliegue martes 2026-11-17, día 7 martes 2026-11-24, informe C2 el 2026-11-20 y vencimiento el 2026-12-13 coinciden en los tres.
- **Finales de línea:** `registro-pendientes.md`, la iteración 03-05, la evidencia 03-05 y esta bitácora conservan CRLF; el resto, LF, como estaban.

## Revisión del texto del aviso

El texto aprobado el 2026-11-06 («Hoy a las HH:MM vamos a actualizar el sistema…») **sigue valiendo sin cambios si se envía el martes 2026-11-17 antes de la actualización**, porque «hoy» es el día del despliegue. No menciona ningún día ni fecha más. Si se enviara otro día, «Hoy» sería falso y habría que escribir el día: es un cambio de una palabra sobre un texto aprobado y lo confirma el desarrollador (aviso 10 de la iteración). No consta si el cliente recibió algún aviso para el 2026-11-12; si lo recibió, conviene decirle que cambió.

## Informe C2 del 2026-11-20

Cae a mitad de la vigilancia (martes 11-17 a martes 11-24). **La recarga del 2026-11-17 entrará en sus conteos** de reinicios y de desconexiones a 28 días. Se anota en la iteración (sección nueva, fechas y riesgos), en la evidencia (calendario) y en el registro (sección 3, fila de C2) que hay que separarla usando `R`, la hora oficial de `Starting uWSGI` que se anota en B6, y marcar aparte la recarga y sus unos 10 s de 502 (AUD-04-002).

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] La decisión 3 reprogramada (martes 2026-11-17, de 20:00 a 23:00; día 7 el martes 2026-11-24) con nota fechada y sin borrar lo anterior, en la iteración y en la evidencia.
- [x] La medición de la 00-07 sigue como precondición, con el guion ajustado a más de siete días y probado con registros sintéticos.
- [x] Calendario del 2026-11-16 al 2026-11-25 (medición, aviso, respaldo, pruebas, etiqueta, despliegue, día 0, día 7 y cierre) en la evidencia y las fechas de operación de la iteración.
- [x] La fecha del vencimiento de la web app corregida donde es vigente (registro, iteración, evidencia, línea base con nota fechada); el 2026-11-20 queda solo para C2.
- [x] Iteración, evidencia y registro sin contradicciones en el texto vigente (búsqueda descrita arriba).
- [x] Nada de la 03-05 ejecutado; sin código, sin commit, sin `README.md` ni `DESIGN.md`; sin nombres de personas.

## Decisiones tomadas

- **Del desarrollador (2026-11-16, dichas por él):** ventana del martes 2026-11-17 de 20:00 a 23:00 y día 7 el martes 2026-11-24; las demás decisiones no cambian; la medición de la 00-07 sigue siendo precondición.
- **Propuestas del agente, sin decidir:** (1) aprovechar la lectura de registros del informe C2 del 2026-11-20 para una lectura a demanda de la 03-05 (C5 y C6); (2) contar el respaldo del despliegue también como semanal si el de hacia el 2026-11-10 u 11 no se hizo (ya lo permite la decisión 2-A); (3) cambiar «Hoy» por el día si el aviso se envía otro día que el martes 2026-11-17.
- **Quedó sin efecto, con nota:** el tope «`R` hasta el 2026-11-13» (venía del vencimiento del 2026-11-20).

## Pendientes y riesgos

- **`PENDIENTE_DESARROLLADOR`:** (1) confirmar en el servidor que producción sigue en `v0.3-doble-envio`; (2) si se hizo el respaldo semanal de hacia el 2026-11-10 u 11; (3) si el cliente recibió un aviso para el 2026-11-12; (4) la fecha para renovar la web app (vence el 2026-12-13); (5) cuántos días conserva la rotación de `access.log` (D0 lo muestra). Registrados en `registro-pendientes.md`, sección 3.
- **Riesgo:** la medición de la 00-07 puede volver a atrasarse y arrastrar el despliegue; sin su resultado anotado no se despliega el martes. Hay margen hasta el 2026-12-13.
- **Riesgo:** si la rotación no conserva los registros desde el 2026-11-04, algunos días quedarán sin medir; D0 y `lineas=` lo muestran y el desarrollador decide qué hacer.
- El primer día UTC (2026-11-04) mezcla unas 4,5 h anteriores al despliegue: D2 lo separa.

## Lo que no pude ver ni verificar

- **Producción entera:** que siga en `v0.3-doble-envio`, el contenido y la rotación de `access.log` y `server.log`, el formato real de las líneas de `access.log` y la fecha de vencimiento en el panel. Todo es dicho por el desarrollador o sale de documentos.
- **GitHub:** la ausencia de la etiqueta y de commits nuevos la verificó el desarrollador; yo solo vi el repositorio local (no hice `fetch` ni consulté el remoto).
- **Aviso al cliente:** si recibió uno para el 2026-11-12.
- **Respaldo semanal** de hacia el 2026-11-10 u 11.
- **Documentos históricos con el 2026-11-20 como vencimiento** (no se editan: son registros de lo medido o decidido en su fecha): `bitacora-00-07-despliegue.md` (líneas 5, 18, 78 y 81), `bitacora-00-01-produccion.md`, `bitacora-00-01-cierre.md`, `bitacora-00-02.md`, `evidencia-00-01.md`, y la nota del 2026-11-04 en `definicion-epica-03.md` y la decisión 8 de `iteracion-03-04` y su bitácora de redacción, que nombran la medición del 2026-11-11. El registro, la iteración y la evidencia dicen la fecha vigente.

## Commit sugerido

`Épica 3 - Iteración 03-05: reprograma el despliegue al martes 2026-11-17, ajusta la medición de la 00-07 y corrige el vencimiento de la web app; solo documentos`
