# Bitácora 03-05 · Decisiones del desarrollador y evidencia de producción

- **Fecha:** 2026-11-06
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (el cierre de la redacción). La iteración 03-05 queda «Pendiente (redactada, decisiones resueltas)»: **no se ejecutó**. La Épica 03 no cambia de estado. Solo documentos: sin cambios de código, de pruebas ni de plantillas, sin despliegue, sin etiqueta y sin tocar PythonAnywhere.

## Resumen

El desarrollador resolvió el 2026-11-06 las ocho decisiones de la 03-05 (dichas por él; el agente no las verificó). Se registraron en la iteración con su fecha y se creó [evidencia-03-05](../../10_epicas/epica-03-integridad-transaccional/evidencia-03-05.md) con las partes A a F, comandos exactos y casillas. Se corrigió AUD-05-005 (el campo que parte en 0 es el **precio**, no la cantidad) y se anotó su cercanía con la propuesta del candado de precio. Se resolvieron o anotaron los avisos de la redacción. Esa primera ronda dejó abiertos la aprobación literal del texto del aviso, el día del despliegue y unos umbrales. **La ronda final del mismo día los cerró** (ver «Ronda final»): solo falta elegir la fuente del respaldo para refrescar la réplica (parte F1 de la evidencia).

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `10_epicas/epica-03-integridad-transaccional/evidencia-03-05.md` | Nuevo: partes A (PC), B (servidor), C (día 0), D (día 7 y cierre), E (retroceso) y F (limpieza de la réplica), con casillas y tablas por rellenar. |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-05-validacion-y-despliegue-de-la-integridad.md` | Estado «Pendiente (redactada, decisiones resueltas)»; las ocho decisiones registradas con fecha; cabecera, tareas, criterios, fechas, riesgos (dos nuevos) y «No pude ver» ajustados; avisos 1 a 7 y 9 con su resolución; la `PENDIENTE_CLIENTE` de las horas de uso, tachada. Las tablas de opciones se conservan. |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-02-erradicacion-supresion-silenciosa.md` | Nota fechada en «Despliegue»: la 03-04 cambió el ítem fallido a formulario con aviso. El texto original no se tocó. |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-04-contrato-de-error-hacia-el-usuario.md` | Nota de corrección fechada junto a AUD-05-005 (el campo es el precio). |
| `00_producto/auditoria-tecnica.md` | AUD-05-005 corregido (precio, con el cambio a la lectura del código y su cercanía con el candado de precio); tres notas nuevas al final de las notas de la Auditoría 05 (corrección de AUD-05-005, ajuste propuesto de AUD-05-002 y seguimiento de AUD-04-001). |
| `00_producto/registro-pendientes.md` | Cabecera, fila 03-05 de la sección 1, fila de las ocho decisiones tachada y resuelta, fila nueva con los pendientes que quedan, filas de AUD-05-005 y de AUD-05-002, propuesta del candado de precio e historial. |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-decisiones.md` | Esta bitácora (nueva). |

No se tocaron `DESIGN.md`, `README.md`, `AGENTS.md`, `_planificacion/README.md`, `plan-de-trabajo.md`, `decisiones.md`, `despliegue.md`, `retroceso.md`, `pruebas.md`, `bitacora-03-04-cierre.md` ni código alguno.

## Verificación

Solo lectura y pruebas de los guiones nuevos en el scratchpad. No se ejecutaron pruebas del proyecto, `check`, `makemigrations`, `docker`, `mysql` ni `manage.py`.

- **Leído:** `registro-pendientes.md`, la iteración 03-05, `bitacora-03-05-redaccion`, `evidencia-01-06` (formato y comandos), `evidencia-00-07` (parte D), `despliegue.md` (secciones 0 a 5), `retroceso.md`, `respaldo.md` (sección 6), `replica-local.md` (secciones 2 y 9), `bitacora-03-operacion-replica`, `pruebas.md` (R15), RDA-014 en `decisiones.md` y las notas de la Auditoría 05.
- **Código leído (no ejecutado):** `views.py` (`crear_pedido`, `ingresar_pago`, `_avisar_formulario_vencido`, el mensaje `INFO`), `envio_unico.py`, `forms.py` (`fecha_solicitud` excluida del formulario), `models.py` (`Pedido`, `RegistroEvento`), `index.js` (`bloquearBoton`, `initBloqueoEnvio`, el flujo del precio), las plantillas con `token_envio` y `data-bloquear-envio`, `settings.py` (`STATIC_ROOT`).
- **Guiones de la evidencia, probados solo con datos sintéticos:** el filtro de `access.log` por instante UTC (`ventana`), probado con GNU awk 5.0 sobre siete líneas inventadas (incluye bordes: una línea un segundo antes de la ventana y otra después); el `sed` de rutas por método y código, y el cálculo de mediana de tiempos, probados con cuatro líneas inventadas; la sintaxis del script de Python (`ast.parse`, Python 3.13). El script de Python **no se ejecutó contra ninguna base**.
- **No probado:** el formato real de `access.log` (la hora entre corchetes se supone igual al que usa la parte D de la 00-07), el nombre `response-time=`, y la conversión Chile → UTC contra la base de zonas horarias (se usa una suma de 3 horas).

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] Las ocho decisiones, con fecha, en la iteración 03-05 y su estado en «Pendiente (redactada, decisiones resueltas)».
- [x] `evidencia-03-05.md` con partes A a F, comandos exactos y casillas.
- [x] AUD-05-005 corregido (precio) y su cercanía con el candado de precio anotada, sin decidir.
- [x] Avisos resueltos: el 2 (vigilancia en `server.log`, plan sin tocar), el de AUD-05-002 (ajuste propuesto, sin decidir), el de la 03-02 (nota) y el de R15 (alineado).
- [x] `registro-pendientes.md` actualizado y esta bitácora creada.
- [x] Sin nombres de personas; `README.md` y `DESIGN.md` intactos; sin commit, sin push y sin ejecutar la 03-05.
- [x] Ronda final registrada (aviso, día, tiempos y retroceso) en la iteración, la evidencia, el registro y esta bitácora, sin contradicciones entre ellos (ver «Ronda final» y el informe de la tarea).

## Decisiones tomadas

Las ocho del desarrollador (2026-11-06), tal como constan en la iteración:

1. **Qué viaja: A.** 03-01 a 03-04 en una sola etiqueta, sin migraciones. Aviso de RDA-007 anotado.
2. **Respaldo: A.** Nuevo el día del despliegue.
3. **Ventana y etiqueta:** `v3.1-integridad`, de **20:00 a 23:00** (hora de Chile; menor uso, dicho por el desarrollador; reemplaza «de madrugada»), un día entre el 2026-11-11 (después de anotar la medición de la 00-07) y el 2026-11-13. Se quitó la `PENDIENTE_CLIENTE`. **El día se fijó en la ronda final: jueves 2026-11-12.**
4. **Aviso: A.** Breve antes y Ctrl+F5 después, con el texto de la iteración; **aprobado en la ronda final**, con una frase más.
5. **Vigilancia: lecturas solo los días 0 y 7** (no la recomendada). Riesgo anotado y lectura extra a demanda sugerida, sin decidir. **El umbral de tiempos se fijó en la ronda final.**
6. **Retroceso:** datos incorrectos o 5xx repetido, sí; un `ERROR` aislado de ítem fallido, no. **Los números se fijaron en la ronda final.**
7. **Limpieza de la réplica y AUD-05-002:** último paso, después de la vigilancia.
8. **Regresiones:** una ejecución con `OK (expected failures=9)` y 267 pruebas, más `check --deploy` y `makemigrations`.

**Decisiones del agente (propuestas, no del desarrollador):** la prueba del botón (C2) se hace con un `preventDefault` en la consola, sin enviar nada; el envío sin token (C4) se hace en `/pagos/ingresar/` con el formulario vacío y `noValidate`, no en `/pedidos/nuevo/`; el criterio provisorio de «duplicado» (`grupos_repetidos`) y la fuente «pedidos nuevos» (eventos y `fecha_solicitud`). Las razones están en la evidencia.

## Ronda final (2026-11-06, más tarde ese día)

Cuatro decisiones del desarrollador (dichas por él; el agente solo las registró). Se actualizaron la iteración, la evidencia, el registro y esta bitácora; no hay archivos nuevos.

| # | Decisión | Dónde quedó |
| :- | :------- | :---------- |
| R1 | **Aviso aprobado:** el texto propuesto más la frase «Si habías elegido una imagen de referencia, vuelve a elegirla: el navegador no la conserva.» (el texto decía que no se pierde nada, y la imagen sí se pierde). Se quita el `PENDIENTE_DESARROLLADOR` de la aprobación | Iteración (decisión 4 y «Decisiones del desarrollador»); evidencia A4 con el texto final listo para copiar |
| R2 | **Día:** jueves 2026-11-12, de 20:00 a 23:00 (hora de Chile). Día 7: 2026-11-19 por la noche | Iteración (cabecera, decisión 3, fechas, riesgos); evidencia (calendario, A0, D); registro |
| R3 | **Tiempos:** ninguna respuesta de `GET` o `POST` de crear pedido, crear cotización e ingresar pago pasa de 2 s, sin contar la recarga. Si `access.log` no trae `response-time=`, se anota y el criterio queda en los 5xx | Iteración (criterio de cierre 5a); evidencia D3 y D5 (iv) |
| R4 | **Retroceso:** 5xx repetido = 2 o más en 24 h en la misma ruta, sin contar la recarga de unos 10 s ni las líneas ya clasificadas (`OSError`); un 5xx suelto es aislado: se investiga y no se retrocede. `ERROR` de ítem fallido: 3 o más en 24 h sin causa explicada, se reproduce en la réplica antes de decidir; los de causa explicada no cuentan | Iteración (decisión 6); evidencia E1 y D5 |

**`response-time=`, comprobado:** consta como nombre de campo en `definicion-epica-13.md` (la guía de lectura de `access.log`, por escribir) y como medición en AUD-04-005 (0,03 a 1,13 s; 5,6 a 9 s tras una recarga), pero **no hay formato ni línea de ejemplo documentados**. La evidencia lo trata como «se anota si falta»: el comando imprime `con_response_time` y `sin_response_time`.

**Lectura del agente, a confirmar por el desarrollador:**

1. «Sin contar la recarga» se opera como los primeros 60 s después de `R` o de otro reinicio (D2 los lista). El número es del agente; la decisión no lo fija.
2. La regla de 5xx se aplica a las rutas de las vistas modificadas (como decía la regla del mismo día), no a cualquier ruta.
3. Con lecturas solo los días 0 y 7, las ventanas de 24 h se evalúan al leer: un 5xx repetido del día 3 se vería el día 7. Es una consecuencia de la decisión 5, no una contradicción.
4. El cierre (ii) pedía «ningún 5xx»; con R4, un 5xx suelto se investiga y, si queda explicado, es una excepción explicada (el criterio ya admitía «o cada excepción explicada»).
5. Un `OSError` no aparece como 5xx en `access.log` (se vio como 499 o `SIGPIPE`), así que queda fuera de la regla sin hacer nada.
6. El `POST` de crear pedido con imagen podría pasar de 2 s sin ser un defecto; no hay medición previa. Anotado como riesgo.
7. «3 o más `ERROR` de ítem fallido sin causa explicada» no es un retroceso automático: se reproduce en la réplica «antes de decidir».

**Comandos probados con líneas sintéticas (GNU awk 5.0):** el filtro de respuestas de más de 2 s (con y sin `response-time=`), el listado de 5xx con hora y ruta y el listado de `ERROR` de ítem fallido con hora y ruta. El primer intento falló porque la variable `sin` choca con la función `sin` de awk; se renombró. Todos filtran por **instante** (UTC en `access.log`, hora de Chile en `server.log`): desde las 21:00 de Chile la fecha UTC cambia, y con `R` el 11-12 entre las 20:00 y las 23:00 el día 7 cae entre las 23:00 UTC del 11-19 y las 02:00 UTC del 11-20.

## Avisos de la redacción: cómo quedaron

La numeración de tu encargo (2, 4, 5 y 6) corresponde a los avisos **2, 5, 6 y 7** de la iteración (el 4 de la iteración, sobre el respaldo, lo resolvió la decisión 2). Se resolvieron según el contenido.

| Aviso | Resolución |
| :---- | :--------- |
| 1. Criterio de término contra `access.log` | Resuelto por la decisión 5: comparar los `POST` 302 con los pedidos nuevos (C6 y D4). |
| 2. Plan 3.5 contra RDA-013 | La vigilancia usa `server.log`; el plan no se tocó; nota en la iteración. |
| 3. RDA-007, cuatro iteraciones | Resuelto por la decisión 1; aviso anotado. |
| 4. Respaldo | Resuelto por la decisión 2. |
| 5. AUD-05-002, «sin respaldo nuevo» | **Ajuste propuesto, sin decidir**: elegir la fuente al refrescar (despliegue, semanal más reciente o 2026-11-04). Nota en la auditoría y en el registro; los textos no se cambiaron. |
| 6. La 03-02 describe la página 500 | Nota fechada en la 03-02, «Despliegue». |
| 7. R15, 07-02 contra 06-05 | **Verificado: no hay contradicción.** La tabla de equivalencias de RDA-014 (`decisiones.md`) hace la antigua 06-05 la 07-02, y el registro (sección 3) lo dice. `pruebas.md` y el comentario de `test_regresiones.py` conservan «06-05» por la regla de [bitacora-02-cierre-epica](../epica-02-red-seguridad/bitacora-02-cierre-epica.md) (lo escrito antes de RDA-014 no se reescribe). La 03-05 usa «07-02 (antes 06-05)». No se tocó el comentario del código. |
| 8. La Épica 03 sigue «Pendiente» | Sin cambio. |
| 9. Texto nuevo del aviso | Aprobado en la ronda final, con una frase más sobre la imagen de referencia. |

## Hallazgos de la lectura que importan

1. **Con la ventana de 20:00 a 23:00, la fecha UTC cambia a las 21:00 de Chile.** Por eso los guiones de C y D filtran por instante y no por día (el guion de la 00-07 cuenta por día UTC).
2. **El día 7 a la misma hora:** un reinicio el 11-13 deja la lectura final el 11-20 por la noche, el día del vencimiento de la web app y del informe C2. El 11-11 o el 11-12 dejan margen. Queda anotado, sin decidir; el día lo elige el desarrollador.
3. **«Nuevo pedido» no usa el `index.js` nuevo para el bloqueo del botón:** `pedido_form.html` conserva su script de la 00-07 (decisión 8-C de la 03-04). El Ctrl+F5 solo importa para los formularios con `data-bloquear-envio` (cotización, pago, cliente, producto y las confirmaciones). La prueba de C2 se hace en `/pagos/ingresar/` por eso.
4. **El servidor revisa el token antes de validar el formulario** (`views.py`, `crear_pedido` y `ingresar_pago`): un envío sin token con el formulario vacío no puede crear nada, y es la base de la prueba segura de C4. Un envío con un token ya usado (`USADO`) redirige (302) al registro creado.
5. **`fecha_solicitud` no está en el formulario** (se excluye) y se asigna al crear, igual por `crear_pedido`, `duplicar_pedido` y la conversión: sirve para contar pedidos nuevos en una ventana. Los eventos `pedido_creado`, `pedido_duplicado` y `cotizacion_convertida` permiten cuadrar los tres caminos.
6. **El riesgo de la decisión 5 es real y se anotó** en la iteración y en la evidencia: lecturas solo los días 0 y 7 dejan sin mirar de los días 1 a 6; la del día 0 ocurre antes del primer uso real. Se sugiere, sin decidir, una lectura extra a demanda.
7. **AUD-05-005:** la lectura de la cantidad (`value="1"`) quedó descartada. Hipótesis nueva, **no probada**: `index.js:461-462` asigna `parseInt(data-precio)` y el texto «0» cuenta como verdadero, así que un producto con valor 0 dejaría el precio en 0. Además, `index.js:503-531` no rechaza un precio 0: un campo vacío agregaría un ítem de $0 sin aviso.

## Pendientes y riesgos

- **`PENDIENTE_DESARROLLADOR`:** solo la fuente del respaldo para refrescar la réplica (parte F1 de la evidencia). Quedaron resueltos en la ronda final: el texto del aviso, el día, el umbral de tiempos y los números del retroceso. Sigue como sugerencia, sin decidir, la lectura extra a demanda, y la propuesta de ver juntos AUD-05-005 y el candado de precio es de la Épica 08.
- **La 03-05 sigue bloqueada hasta el 2026-11-11:** no iniciarla sin la medición de la 00-07 anotada (hacia las 01:32) y la renovación de la web app (2026-11-10). Ejecución: jueves 2026-11-12, de 20:00 a 23:00.
- **Los guiones de las partes C y D** deben probarse en la primera lectura real; el agente ajusta el filtro si el formato difiere.
- **El texto del aviso** y las horas de uso siguen sin dato del cliente (la ventana es dicha por el desarrollador).

## Lo que no pude ver ni verificar

- **Producción:** qué etiqueta corre hoy, el contenido de `server.log` y `access.log`, el formato real de `access.log` y `response-time=`, si la renovación del 2026-11-10 se hizo.
- **Etiquetas:** `git tag` es del desarrollador; no comprobé que `v3.1-integridad` esté libre ni que `v0.3-doble-envio` exista en GitHub (A3 lo comprueba).
- **Pruebas, `check` y `makemigrations`:** no se ejecutaron; el 267 y el `expected failures=9` salen de [bitacora-03-04-correccion-abono](bitacora-03-04-correccion-abono.md).
- **El script de Python de C6 y D4** contra una base, y las rutas del disco de Docker de la parte F.
- **`response-time=`:** formato y unidad (se supone segundos) no documentados; el comando y el umbral de 2 s no se probaron contra el archivo real.
- **Las decisiones:** son dichas por el desarrollador; el agente solo las registró.

## Commit sugerido

`Épica 3 - Iteración 03-05: fija el aviso final, el jueves 2026-11-12 y los umbrales de tiempos y retroceso; actualiza la evidencia; solo documentos`
