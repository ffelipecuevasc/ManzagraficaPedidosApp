# Bitácora 03-05 · Redacción de la iteración

- **Fecha:** 2026-11-06
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (la redacción). La iteración 03-05 queda «Pendiente (redactada)»: no se ejecutó. La Épica 03 no cambia de estado. Solo documentos: sin cambios de código, de pruebas ni de plantillas, sin despliegue, sin etiqueta y sin tocar PythonAnywhere.

## Resumen

Se dejó limpia la 03-04 en `definicion-epica-03.md` y se redactó la iteración 03-05 · Validación y despliegue de la integridad (alcance 5 de la épica, subfase 3.5 del plan). La iteración dice qué viaja (medido con `git diff`), qué cambia para el usuario y en los registros, qué dice el procedimiento y cuándo puede desplegarse (no antes de la medición de la 00-07 del 2026-11-11). Deja **ocho decisiones** `PENDIENTE_DESARROLLADOR`, cada una con opciones, ventajas, riesgos y una recomendada, más nueve avisos y la lista de lo que no se pudo verificar. Ninguna decisión está tomada.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-05-validacion-y-despliegue-de-la-integridad.md` | Nuevo: iteración «Pendiente (redactada)». |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-redaccion.md` | Esta bitácora (nueva). |
| `10_epicas/epica-03-integridad-transaccional/definicion-epica-03.md` | «Última revisión» al 2026-11-06 y nota fechada del cierre de la 03-04 y la redacción de la 03-05. El estado de la épica y la tabla de iteraciones no cambian. |
| `00_producto/registro-pendientes.md` | Cabecera (iteración activa, próximo hito y fechas vigentes), fila 03-05 de la sección 1, fila de las ocho decisiones en la sección 3 e historial. |

No se tocaron `DESIGN.md`, `README.md`, `AGENTS.md`, `_planificacion/README.md`, `plan-de-trabajo.md`, `decisiones.md`, `auditoria-tecnica.md`, `despliegue.md`, `retroceso.md`, `pruebas.md` ni ninguna iteración anterior.

## Parte A · La 03-04, limpia

- `definicion-epica-03.md`: «Última revisión» ahora dice 2026-11-06 (03-04 Terminada, 03-05 redactada) y corrige el «En revisión» de la anterior; nota fechada al final con el cierre y los enlaces. Como al cerrar la 03-03, **la tabla de iteraciones no tiene columna de estado y no se tocó**: los estados viven en `registro-pendientes.md`.
- `registro-pendientes.md`: la fila 03-04 ya decía Terminada (2026-11-06) con la cifra de 267 pruebas; se corrigió el «Próximo hito» (decía «el inicio de la Épica 03») y se agregó la 03-05.
- **No existe un «README de la épica»**: la carpeta solo tiene `definicion-epica-03.md` y las iteraciones. `_planificacion/README.md` (protegido) no lleva estados de iteraciones (búsqueda de `03-0`). La comparación se hizo entre la definición, el registro y la iteración 03-04: coinciden en Terminada (2026-11-06) y en la excepción de AUD-05-006 y AUD-05-007.

## Verificación

Solo lectura. No se ejecutaron pruebas, `check`, `makemigrations`, `docker`, `mysql` ni `manage.py`.

- **Planificación leída:** `definicion-epica-03.md`, `plan-de-trabajo.md:300-390`, las secciones «Despliegue» de la 03-01 a la 03-04, `registro-pendientes.md`, `decisiones.md` (RDA-007, RDA-013 y RDA-019), `auditoria-tecnica.md` (estado de AUD-01-001, AUD-01-002, AUD-02-004, AUD-02-005, AUD-02-006, AUD-02-008, AUD-02-021, AUD-02-023, AUD-02-027, AUD-02-029, AUD-04-002 y AUD-05-002), `evidencia-00-07.md` (parte D y respuesta del desarrollador), `iteracion-01-09` (sección «Despliegue»), `bitacora-03-04-redaccion` (formato), `bitacora-03-04-cierre`.
- **Operación leída:** `despliegue.md` completo (secciones 0 a 5), `retroceso.md` completo, `respaldo.md` (secciones 1, 5 y 6), `pruebas.md` (secciones 2, 7 y 7.1) y `replica-local.md` (sección 9).
- **Medido con `git` (solo lectura):**
  - `git diff --stat 5dc82a8..HEAD -- . ":(exclude)_planificacion" ":(exclude)docs"` → 30 archivos, 1.957 inserciones y 456 eliminaciones. Entre ellos, `index.js` (cambian los estáticos) y `decorators.py` (eliminado); ninguna migración, ni `requirements.txt` ni `settings.py`.
  - `git diff --stat 7e14398..HEAD` con la misma exclusión → sin salida: desde el último commit de código solo cambian documentos.
  - `git status --short` vacío al empezar, y `HEAD` igual a `origin/main` (`c9db60e`).
- **Búsquedas:** `clearsessions` en el repositorio (sin resultados), `STATIC`/`STORAGES` en `settings.py` (`STATIC_URL` y `STATIC_ROOT` solamente: almacenamiento por defecto, sin nombres con hash), `index.js` en `base.html`.
- **Fechas:** días de la semana calculados con Python (2026-11-01 domingo, 11-04 miércoles, 11-10 martes, 11-11 miércoles, 11-13 viernes, 11-14 sábado, 11-20 viernes).
- **Comandos denegados:** `git tag -n` (la sección 6 de `AGENTS.md` reserva `git tag` al desarrollador) y un `git diff` que incluía `.env.example` en la lista de rutas. No se repitieron ni se buscaron rodeos.
- **Terminaciones de línea:** `registro-pendientes.md` es CRLF. Quedó un final de línea suelto (LF) en una fila de historial de la tarea anterior; se normalizó a CRLF. `git diff --stat` muestra por eso 2 líneas más de las 6 inserciones y 4 eliminaciones reales (con `--ignore-cr-at-eol` salen 6 y 4).

## Hallazgos de la lectura que importan

1. **La semana de vigilancia tiene una fecha tope.** Para terminar el 2026-11-20 (vencimiento de la web app e informe C2), el reinicio debe ser hasta el 2026-11-13. Un fin de semana (desde el sábado 11-14) la deja pasar esa fecha.
2. **Hay dos precedentes de ventana en los documentos:** el domingo 2026-10-25 («el negocio cierra el sábado en la tarde y no hay uso hasta el lunes», decisión de la 01-06) y la madrugada del miércoles 2026-11-04 (00:11 y 01:32). La iteración los usa en la decisión 3 y deja `PENDIENTE_CLIENTE` solo las horas de entre semana.
3. **`access.log` ya no basta para el criterio de duplicados.** Con el token, el segundo POST de un doble envío también responde 302. Por eso la decisión 5a propone comparar los `POST` con 302 contra los pedidos nuevos de la base. El guion de la 00-07 queda como señal, no como prueba.
4. **Esta vez sí hay `collectstatic`.** Los dos despliegues anteriores (`v1.2-capturas` y `v0.3-doble-envio`) no lo necesitaron; `index.js` cambió desde `5dc82a8`. El retroceso también lo exige (`retroceso.md`, caso 1, paso 3).
5. **El respaldo previo lo piden los procedimientos, no solo las iteraciones.** `respaldo.md`, sección 5 («uno antes de cada despliegue de fase») y `despliegue.md`, lista de comprobación, punto 5. Las iteraciones 03-01 a 03-04 lo dejaron «a decidir en la 03-05».
6. **Sin purga de sesiones en el repositorio.** El token agrega hasta 20 entradas por sesión. No se encontró `clearsessions`. El tamaño es pequeño (inferido, no medido), pero el disco es escaso y las sesiones duran 14 días.
7. **Los estáticos no tienen nombre con hash**, así que el navegador puede conservar el `index.js` anterior con la plantilla nueva (inferido, no probado). La decisión 4 incluye pedir Ctrl+F5.
8. **La línea `INFO` del rechazo** puede no verse sola si nadie tiene un formulario abierto al reiniciar. La decisión 5b ofrece una verificación deliberada y sin escritura.
9. **La limpieza de la réplica tiene una pieza oculta:** el refresco obliga a repetir el conteo de pedidos sin ítems de la 03-02 (registro, sección 3) y la comprobación de cifrado, que hoy no pasa.

## Decisiones abiertas (`PENDIENTE_DESARROLLADOR`)

| # | Tema | Recomendada |
| :- | :--- | :---------- |
| 1 | Qué viaja | A. 03-01 a 03-04 en una sola etiqueta, sin migraciones, con `collectstatic` |
| 2 | Respaldo previo | A. Nuevo el día del despliegue, verificado antes de recargar |
| 3 | Ventana y etiqueta | A. De madrugada, después de la medición del 2026-11-11 y con el reinicio hasta el 2026-11-13; etiqueta sugerida `v3.1-integridad` |
| 4 | Aviso al cliente | A. Aviso breve antes (texto propuesto, por aprobar) y Ctrl+F5 después |
| 5 | Vigilancia | 5a-A. Siete días desde el reinicio, cuatro lecturas y duplicados con `access.log` y conteo de pedidos; 5b-A. Verificación deliberada de la línea `INFO` el día 0 |
| 6 | Retroceso y `ERROR` nuevo | A. Regla escrita antes (datos incorrectos, 5xx repetido, `ERROR` aislado, `INFO`) |
| 7 | Limpieza de la réplica y AUD-05-002 | A. Paso final de la 03-05, después de cerrar la vigilancia |
| 8 | Regresiones al desplegar | A. Una ejecución el día, `OK (expected failures=9)`, 267 pruebas, `check --deploy` y `makemigrations` |

Figuran en la sección 3 de `registro-pendientes.md`. `PENDIENTE_CLIENTE`: horas de menor uso entre semana (sin fila propia en la sección 2: se anotó dentro de la iteración).

## Avisos (contradicciones o tensiones, sin corregir)

1. **Criterio de término contra `access.log`.** La definición pide que `access.log` no muestre duplicados; con el token ya no los distingue (hallazgo 3).
2. **Plan 3.5 contra RDA-013.** El plan pide vigilar con «las tablas de registro de la Fase 1»; RDA-013 las descartó. La definición de la épica ya habla de `server.log`.
3. **RDA-007 «un despliegue, un propósito».** `despliegue.md` lo permite para «una fase cerrada», pero la 03-04 ya mezcló dos propósitos (su decisión 10) y esta etiqueta suma tres iteraciones más. La opción B de la decisión 1 es la salida.
4. **Respaldo:** las iteraciones lo dejaron abierto y los procedimientos ya lo piden (hallazgo 5).
5. **AUD-05-002, «sin respaldo nuevo».** Si la decisión 2 es A, ese respaldo existirá y podría ser la fuente del refresco: cambia el texto de la decisión del 2026-11-04.
6. **La 03-02 describe un comportamiento que la 03-04 cambió** (ítem fallido: página 500 contra formulario 200 con `ERROR` de `pedidos.views`). Vale la 03-04 y `despliegue.md`, 3.9.
7. **R15:** la 03-04 dice que la corrigen «04-01, 04-06, 06-01 y 07-02»; `pruebas.md` dice 06-05.
8. **La Épica 03 sigue «Pendiente»** con cuatro iteraciones Terminadas: se mantiene el criterio de las notas anteriores hasta cerrar la 03-05.
9. **El texto del aviso al cliente es nuevo** y no está entre los «Textos aprobados» de la 03-04.

Además, el encargo decía que la tabla de iteraciones de la definición se actualizara «como hizo la 03-03». La 03-03 no la tocó (no tiene columna de estado), así que se siguió ese precedente y se dejó la nota.

## Lo que no pude ver ni verificar

- **Producción:** qué etiqueta corre hoy, `server.log` y `access.log`, horas de uso de entre semana, si la renovación del 2026-11-10 se hizo y cuánto extiende.
- **Etiquetas:** no pude listarlas (`git tag` es del desarrollador); la lista sale de `despliegue.md` y de las evidencias. No comprobé que `v3.1-integridad` esté libre ni que `v0.3-doble-envio` exista en GitHub.
- **Pruebas, `check` y `makemigrations`:** no se corrieron; el 267 y el `expected failures=9` salen de [bitacora-03-04-correccion-abono](bitacora-03-04-correccion-abono.md).
- **Cache de `index.js`**, **línea `INFO` en producción**, **retroceso con sesiones que traen `tokens_envio`** y **costo de las +3 consultas en producción:** inferidos o medidos solo en la réplica.
- **La fecha y hora de la medición de la 00-07** (2026-11-11, ~01:32 hora de Chile): consta en `evidencia-00-07.md` y `registro-pendientes.md` y coincide con lo dicho; no la puedo medir.

## Migraciones

- Ninguna. Verificado por el `diff` de la sección «Verificación»; `makemigrations --check --dry-run` queda para el día del despliegue.

## Criterios de aceptación de la redacción

- [x] La iteración 03-05 existe con el formato de la 03-04, en estado «Pendiente (redactada)».
- [x] Las ocho decisiones pedidas figuran con tabla de opciones y la recomendada primero.
- [x] Distingue lo documentado, lo medido hoy y lo inferido, y lista lo no verificado.
- [x] Lista las fechas de operación (2026-11-10, 2026-11-11, 2026-11-20) con su fuente.
- [x] Los avisos nombran las tensiones con RDA, plan y decisiones previas.
- [x] La 03-04 consta como Terminada en la definición de la épica y en el registro.
- [x] Sin nombres de personas, sin `DESIGN.md` ni `README.md`, sin commit ni push.

## Decisiones tomadas

- Etiqueta sugerida `v3.1-integridad` por la convención de `despliegue.md`, sección 1; es una sugerencia, no se creó.
- Se dejó la fila de `PENDIENTE_CLIENTE` dentro de la iteración y no en la sección 2 del registro, porque la pregunta depende de la decisión 3.

## Pendientes y riesgos

- Tomar las ocho decisiones. La 3 tiene fecha: hasta el 2026-11-13 si se quiere que la semana termine el 2026-11-20.
- Crear `evidencia-03-05.md` al empezar la ejecución (la redacción no la crea porque depende de las decisiones 2, 3 y 5).
- No empezar la 03-05 sin la medición de la 00-07.

## Commit sugerido

`Épica 3 - Iteración 03-05: redacta la validación y el despliegue de la Fase 3 con ocho decisiones abiertas y deja la 03-04 Terminada; solo documentos`
