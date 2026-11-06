# Iteración 03-05 · Validación y despliegue de la integridad

- **Épica:** 03 · Integridad transaccional
- **Estado:** Pendiente (redactada, 2026-11-06). Sin ejecutar: ni pruebas, ni respaldo, ni etiqueta, ni despliegue ([bitacora-03-05-redaccion](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-redaccion.md)). Las ocho decisiones están abiertas (`PENDIENTE_DESARROLLADOR`).
- **Subfase del plan:** 3.5 «Validación y despliegue» (`plan-de-trabajo.md:364-371`)
- **Depende de:** 03-04 (Terminada el 2026-11-06) y de la medición de la 00-07 (parte D de [evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md), 2026-11-11, hacia las 01:32 hora de Chile)
- **RDA relacionadas:** RDA-007 (rama única y etiqueta anotada antes de cada despliegue; un despliegue lleva un solo propósito), RDA-013 (diagnóstico en `server.log`, sin identificador ni tabla de errores), RDA-019 (los errores de vista los maneja Django).
- **Hallazgos que cierra:** AUD-04-001 en la medición de producción que le faltaba (la parte de servidor ya está «Resuelto en 03-04» en código); confirma en producción los que hoy dicen «se despliega con la 03-05»: AUD-01-001, AUD-01-002, AUD-02-004 (el código; las filas históricas no se reparan), AUD-02-005, AUD-02-008, AUD-02-027 y AUD-02-029.
- **Hallazgos relacionados:** AUD-02-006 (avance de la 03-04; sigue abierto por el GET, 04-01), AUD-02-021 (13 errores de plantilla sin causa conocida: la semana de `server.log` puede aportar evidencia, no se asume), AUD-02-023 (imágenes de `media/` sin copia: no se tocan), AUD-04-002 (cada recarga deja unos 10 s de 502), AUD-04-004 (líneas `OSError: write error`, ya clasificadas), AUD-05-002 (disco de Docker de la réplica en C:).
- **Cambio de esquema:** Ninguno (verificado el 2026-11-06 con `git diff`, ver «Qué viaja»).
- **Respaldo previo al despliegue:** decisión 2.
- **Etiqueta y ventana:** decisión 3. Etiqueta sugerida por la convención de `despliegue.md`, sección 1: `v3.1-integridad`.

## Objetivo

Publicar en producción, en un solo despliegue, el trabajo de las iteraciones 03-01 a 03-04, comprobar que funciona y vigilarlo una semana leyendo `server.log` y `access.log`, hasta poder decir con medición que se cumple el criterio de término de la Épica 03 (alcance 5 de la épica). No agrega funcionalidad ni corrige defectos: si la vigilancia encuentra uno, se registra y se decide aparte.

## Cómo se lee este documento

- **Documentado:** está escrito en el repositorio o en la planificación; se cita el archivo (leídos el 2026-11-06).
- **Medido hoy:** salida de un comando de solo lectura ejecutado el 2026-11-06 (`git diff --stat`, `git status`).
- **Inferido:** sale de leer documentos o código, no de ejecutarlo ni de verlo en producción. Se marca «(inferido)».
- **No verificado:** depende de producción o de datos que solo tiene el desarrollador. Se lista al final.
- Ningún dato personal: solo conteos, horas, códigos y rutas sin parámetros.

## Alcance contra la definición de la épica

Verificado contra `definicion-epica-03.md` (alcance 5, criterio de término y notas) y `plan-de-trabajo.md:364-371`.

| Pieza | Fuente | En esta iteración |
| :---- | :----- | :---------------- |
| Pruebas de regresión en verde (el criterio objetivo de la fase) | Plan 3.5, primer punto | Sí (decisión 8) |
| Ejercitar los flujos completos contra la réplica con datos reales | Plan 3.5, segundo punto | **Ya hecho** en las revisiones manuales de la 03-03 y la 03-04 y en la revisión de servidor ([bitacora-03-03-cierre](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-03-cierre.md), [bitacora-03-04-revision-servidor](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-revision-servidor.md), [bitacora-03-04-cierre](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-cierre.md)). Aquí solo se repite lo que cambie |
| Respaldo descargado, etiqueta creada, despliegue | Plan 3.5, tercer punto | Sí (decisiones 1 a 4) |
| Vigilancia intensiva la primera semana | Alcance 5; plan 3.5, cuarto punto | Sí (decisión 5). El plan dice «mediante las tablas de registro de la Fase 1»: RDA-013 las descartó, la vigilancia se hace en `server.log` (ver «Avisos») |
| «Una semana de producción sin errores nuevos asociados a las vistas modificadas» | Criterio de término, cuarto punto | Sí (decisión 5) |
| R21 en verde y `access.log` sin pedidos duplicados por envío repetido | Criterio de término, quinto punto | R21 ya está en verde (03-04). Lo de `access.log` se mide aquí y **no se decide solo con `access.log`** (decisión 5 y «Avisos») |
| Los nuevos avisos al usuario y los formularios abiertos al desplegar | Notas de la 03-04 (decisión 7) | Sí (decisión 4) |
| Limpieza de la réplica y AUD-05-002 | Registro de pendientes (Operación, al cerrar la Épica 03) | Decisión 7 |
| Corregir defectos hallados en la vigilancia | — | **No**: se registran y se deciden aparte (`AGENTS.md`, sección 10, punto 3) |
| Pendientes de la Épica 08 (AUD-05-005 a AUD-05-008) y el candado de precio | [bitacora-03-04-cierre](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-cierre.md) | **No** |

## Qué hay hoy (evidencia leída el 2026-11-06)

### Qué corre en producción

- **Documentado:** `v0.3-doble-envio`, sobre el commit `5dc82a8`, desplegada el 2026-11-04 con reinicio efectivo a las 01:32:51 hora de Chile, sin retroceso (`despliegue.md`, sección 5; [evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md)). Antes, `v1.2-capturas` (2026-11-04, 00:11:49).
- **No verificado hoy:** que siga siendo la etiqueta en producción. Este documento no puede consultar el servidor.

### Qué viaja

Medido hoy: `git diff --stat 5dc82a8..HEAD -- . ":(exclude)_planificacion" ":(exclude)docs"` → **30 archivos, 1.957 inserciones y 456 eliminaciones**. Y `git diff --stat 7e14398..HEAD` con la misma exclusión → **sin salida**: desde el último commit de código (`7e14398`, corrección del abono) solo cambian documentos. `git status --short` está vacío y `HEAD` es igual a `origin/main` (`c9db60e`).

| Grupo | Archivos | Qué cambia |
| :---- | :------- | :--------- |
| Aplicación | `views.py`, `forms.py`, `envio_unico.py` (nuevo), `decorators.py` (eliminado) | 03-01 a 03-04: sin `@transaccion_segura`, `transaction.atomic` explícito, captura de `ERRORES_DE_ITEM` fuera del bloque, token de envío único en la sesión, formularios que conservan lo escrito |
| JavaScript | `pedidos/static/pedidos/js/index.js` | Bloqueo del botón (`bloquearBoton`, `desbloquearBoton`, `initBloqueoEnvio`). **Hay cambio de estáticos: exige `collectstatic`** (`despliegue.md`, 3.5) |
| Plantillas (13) | `base.html`, `errors/500.html`, `pedido_form.html`, `cotizacion_form.html`, `cotizacion_convertir.html`, `pago_form.html`, `cliente_form.html`, `producto_form.html`, `restaurar_bd.html` y cuatro de confirmar eliminación | Aviso de error visible, errores accesibles, `data-bloquear-envio`, texto de la página 500 |
| Pruebas (12) | `test_contrato_error.py`, `test_envio_unico.py`, `test_bloqueo_envio.py`, `test_fronteras_transaccionales.py` y ocho archivos ajustados | No viajan a producción en la práctica (el servidor no las ejecuta), pero están en la etiqueta |

- **Sin migraciones:** no hay archivos nuevos en `pedidos/migrations/` (la última es `0007_registroevento.py`) y el `diff` no lista `requirements.txt` ni `settings.py`. `makemigrations --check --dry-run` lo confirma el día del despliegue (decisión 8).
- **Sin dependencias nuevas** ni cambios de configuración.
- **Qué ve distinto el usuario:** un error de validación o un ítem que no se puede guardar devuelve el formulario con lo escrito (200) y un aviso rojo, no la página 500; los botones de guardar se bloquean con «Guardando…»; un envío repetido termina en el registro ya creado; un formulario abierto antes del despliegue no se guarda al primer intento (no trae token) y vuelve con «Este formulario venció y no se guardó…»; la página 500 pide pantalla y hora.
- **Qué cambia en los registros:** (a) un ítem que falla ya no deja una línea `django.request` con 500, sino una línea `nivel=ERROR` de `pedidos.views` con la traza y una respuesta 200; (b) el rechazo por token deja una línea `nivel=INFO`; (c) un segundo envío del mismo token responde 302 igual que el primero (ver la decisión 5) ([docs/operacion/despliegue.md](../../../docs/operacion/despliegue.md), sección 3.9). Estas diferencias no son errores del despliegue.
- **Costo ya aceptado (2026-11-04):** +3 consultas por GET y por POST exitoso de crear pedido, crear cotización e ingresar pago. Medido solo en la réplica ([iteracion-03-04](iteracion-03-04-contrato-de-error-hacia-el-usuario.md), «Decisiones del desarrollador»). En producción no se ha medido.

### Qué dice el procedimiento

- **`despliegue.md`:** lista de comprobación previa (sección 2: pruebas, `check --deploy`, `makemigrations`, respaldo, etiqueta), pasos en el servidor (3.1 a 3.8), cómo leer el registro (3.7) y qué hacer si un usuario reporta un error (3.9, creada en la 03-04). Regla de la hora: la oficial de una recarga es la del reinicio efectivo (`Starting uWSGI`).
- **Advertencia del incidente del 2026-11-03** (`despliegue.md`, 3.2): en el servidor solo `git fetch origin --tags` y `git checkout <etiqueta>`; el prompt debe decir `HEAD detached at <etiqueta>`.
- **`retroceso.md`:** sin migraciones es el caso 1 (volver a la etiqueta anterior, `collectstatic` si cambiaron estáticos, `check`, recargar, verificar; meta de menos de 15 minutos). El caso 3 (restaurar el respaldo) pierde lo registrado después de él.
- **Un despliegue, un propósito** (`despliegue.md`, cabecera; RDA-007): «una sola iteración (o una fase cerrada), nunca una mezcla». Esta etiqueta publica la Fase 3 cerrada; ver «Avisos».
- **Precedentes:** la 01-09 se desplegó **después** de la medición de la 01-06 «para que la medición no mezcle versiones» ([iteracion-01-09](../epica-01-observabilidad/iteracion-01-09-capturas-amplias.md), «Despliegue»). La 00-07 se desplegó sin respaldo nuevo porque no tocaba datos ni esquema (`despliegue.md`, sección 5).

### La medición de la 00-07 y por qué espera

- **Documentado:** la parte D de [evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md) se mide el **2026-11-11, hacia las 01:32** (hora de Chile; 04:32 UTC; una semana después del reinicio efectivo del 2026-11-04). Cuenta por día en UTC los `POST /pedidos/nuevo/` y los segundos con dos o más; esperado `segundos_repetidos=0`. Aparece igual en `registro-pendientes.md` (cabecera y «Fechas vigentes»). El desarrollador lo dijo; los tres documentos coinciden.
- **Por qué no se despliega antes (inferido):** esa medición mide el efecto del botón de la 00-07. Con la 03-05 en producción, el segundo POST de un doble envío responde 302 como el primero y `pedido_form.html` cambió (37 líneas), así que dejaría de poder atribuirse el resultado al botón. Es el mismo motivo del precedente de la 01-09.

## Decisiones

Todas `PENDIENTE_DESARROLLADOR` salvo donde se marca `PENDIENTE_CLIENTE`. La recomendada va primero en cada tabla. Dependencias: la 3 condiciona la 4 y la 5; la 2 condiciona la 7; la 1 y la 8 fijan lo que se prueba y se etiqueta.

### Decisión 1 · Qué viaja

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. 03-01 a 03-04 en una sola etiqueta, sin migraciones (recomendada)** | Una etiqueta anotada sobre el último commit de código (hoy `7e14398`; `HEAD` solo suma documentos), con `collectstatic` por `index.js` | Cumple RDA-007 y `despliegue.md` («una fase cerrada»). Es lo que cada iteración declaró («viaja con la 03-05»). Se prueba y se vigila el estado final, el único revisado a mano | Cuatro iteraciones y dos propósitos (contrato de error y envío único) en un solo despliegue: si falla, se retrocede todo (caso 1, sin migraciones). Un retroceso vuelve también el token y el bloqueo del botón de las pantallas nuevas |
| **B. Dos despliegues: 03-01 a 03-03 y luego 03-04** | Etiqueta intermedia sobre el commit `501c0b0` (fin de la 03-03) | Aísla el cambio de atomicidad del de interfaz | `501c0b0` no se revisó a mano como producto final ni se probó con la revisión de servidor (inferido); la 03-04 reescribe partes de `views.py` que la 03-03 toca (586 líneas cambiadas en el archivo); dos recargas, dos vigilancias y dos ventanas antes del 2026-11-20 |
| **C. Sumar al despliegue pendientes de la Épica 08** (AUD-05-005 a AUD-05-008) | Mezclar correcciones de presentación | Limpia avisos menores | Contra «un despliegue, un propósito» y contra el alcance de la 03-05. No se recomienda |

### Decisión 2 · Respaldo previo

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Respaldo nuevo el día del despliegue, verificado antes de recargar (recomendada)** | Un clic en «Generar Nuevo Respaldo BD», descarga, `verificar_respaldo.py` con código 0 y fila en `respaldo.md`, sección 6. Cuenta también como el semanal si cae el mismo día | `respaldo.md`, sección 5: «uno antes de cada despliegue de fase»; `despliegue.md`, lista de comprobación, punto 5: «el primer despliegue de una fase». Es el único destino del caso 3 de `retroceso.md`. Esta etiqueta cambia las vistas de escritura y también `restaurar_bd` y el aviso del respaldo. Precedentes: `v0.1-higiene`, `v1.1-observabilidad` y `v1.2-capturas` se desplegaron con respaldo nuevo | El enlace del respaldo es un GET que se recarga a los 2 s y cortó una descarga el 2026-11-04 (AUD-03-002): hacer **un solo clic** y, si se corta, bajar el archivo desde Files (`respaldo.md`, sección 2). Consume parte de los 100 s de CPU diarios |
| **B. Sin respaldo nuevo; vale el del 2026-11-04 00:12:37** | Se anota «no aplica» como en `v0.3-doble-envio` | Sin trabajo extra; el esquema no cambia | Ese respaldo tendría al menos 7 días: un retroceso del caso 3 perdería una semana de pedidos y pagos. El precedente de la 00-07 (un botón, sin tocar datos) no es comparable: esta etiqueta cambia cómo se escriben pedidos, cotizaciones y pagos |
| **C. Respaldo nuevo y además refrescar la réplica con él antes de desplegar** | Una sola descarga sirve para las dos cosas | Cierra antes AUD-05-002 | Cambia la decisión del 2026-11-04 («al cerrar la Épica 03, sin respaldo nuevo») y borra la réplica donde se reproducirían errores durante la vigilancia. Ver decisión 7 |

### Decisión 3 · Ventana y etiqueta

Precondición: **no desplegar antes de la medición de la 00-07 del 2026-11-11 (hacia las 01:32)** ni de anotar su resultado. Hechos documentados que pesan en la ventana:

- `v1.1-observabilidad` se desplegó un domingo (2026-10-25) porque «el negocio cierra el sábado en la tarde y no hay uso hasta el lunes» (`registro-pendientes.md`, sección 3, decisión de la 01-06).
- `v1.2-capturas` y `v0.3-doble-envio` se desplegaron de madrugada del miércoles 2026-11-04 (reinicios efectivos a las 00:11:49 y 01:32:51).
- La vigilancia de siete días termina a más tardar el 2026-11-20 (vencimiento de la web app e informe C2) solo si `R` es hasta el 2026-11-13.
- Días de la semana calculados desde «domingo 2026-11-01» (`despliegue.md`, `evidencia-00-07`): el 2026-11-11 es miércoles y el 2026-11-14, sábado.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. De madrugada, en una noche de la semana del 2026-11-11 posterior a la medición, con `R` hasta el 2026-11-13 (recomendada)** | Orden: renovar la web app (11-10) → medir la 00-07 (11-11, 01:32) → respaldo → pruebas → etiqueta → despliegue. Puede ser esa misma noche, tras anotar la medición, o una de las dos siguientes | Respeta la precondición y el precedente de la 01-09. Mismo horario de los dos últimos despliegues. El uso real del negocio empieza horas después, así que la semana de vigilancia ve tráfico desde el día 1 (inferido). Termina el 2026-11-20 o antes | Nadie del negocio ve un fallo hasta la mañana (inferido). Concentra en pocos días la renovación, la medición, el respaldo, las pruebas y el despliegue. `PENDIENTE_CLIENTE`: no hay medición de horas de uso entre semana |
| **B. Fin de semana: sábado en la tarde a lunes, desde el 2026-11-14** | Mismo orden, con la ventana del precedente de la 01-06 | Sin uso durante la recarga ni formularios abiertos al reiniciar (menos avisos que dar) | El primer uso real llega el lunes: de los siete días, dos casi no tienen tráfico (inferido). `R` cae el 2026-11-14 o después, así que la semana termina el 2026-11-21 o después: pasa el vencimiento y el informe C2 del 2026-11-20 |
| **C. Antes de la medición** | Desplegar apenas esté lista | Cierra antes AUD-04-001 en producción | La parte D de la 00-07 dejaría de medir solo el botón (ver arriba). **Contradice la precondición dicha por el desarrollador.** No se recomienda |
| **D. Después del 2026-11-20** | Esperar el informe C2 y la renovación siguiente | Sin solapes con otras fechas | AUD-04-001 (Alta) sigue abierto más de dos semanas con el servidor sin protección, y la vigilancia queda atada a otra renovación |

- **Etiqueta (sugerida):** `v3.1-integridad`. Formato `v<fase>.<correlativo>-<propósito>` de `despliegue.md`, sección 1: fase 3, correlativo 1 (cada fase parte en 1; los documentos no registran ninguna etiqueta de la fase 2). Mensaje: `Iteraciones 03-01 a 03-04 · desplegada el AAAA-MM-DD` con la fecha de Chile del día. Anotada, publicada con `git push origin`, y comprobada con `git ls-remote --tags origin v3.1-integridad`.
- **Destino de retroceso:** `v0.3-doble-envio` (la última desplegada; `despliegue.md`, sección 1: «el destino es la etiqueta desplegada antes»).
- **No se crea ninguna etiqueta en esta redacción** (`AGENTS.md`, sección 6).

### Decisión 4 · Aviso al cliente

Lo que cambia para quien usa la aplicación: (a) los formularios abiertos al desplegar no traen token y se guardan al segundo intento, sin perder lo escrito; (b) los botones de guardar se bloquean con «Guardando…»; (c) los errores se ven arriba, en rojo; (d) la recarga deja unos 10 s de respuestas 502 (AUD-04-002); (e) el navegador puede conservar el `index.js` antiguo (no hay nombre con hash: `settings.py:190-191`, almacenamiento de estáticos por defecto) y conviene recargar con Ctrl+F5 (inferido, no probado).

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Aviso breve antes y recordatorio después (recomendada)** | El desarrollador manda el texto de abajo antes de la hora elegida y, tras la recarga, pide cerrar y reabrir la aplicación con Ctrl+F5 | Quien usa la aplicación (hoy el dueño, único usuario según `pruebas.md`, sección 9) sabe qué esperar; evita un reporte de «no se guardó» o de «el botón no responde» | El texto es nuevo y debe aprobarse. Depende del canal que use el desarrollador, que no consta en los documentos |
| **B. Sin aviso previo; solo explicar si pregunta** | Nada antes | Sin trabajo | El primer intento de guardar con un formulario abierto vuelve con «Este formulario venció…» y puede leerse como un error nuevo del sistema |
| **C. Aviso solo en pantalla** (un mensaje fijo en la aplicación) | Mensaje temporal | Lo ve quien entra | Es código y plantilla nuevos: **fuera de alcance** (esta iteración no toca código) |

**Texto propuesto para la opción A** (`PENDIENTE_DESARROLLADOR`: aprobar o cambiar; voz de `DESIGN.md`, sección 10):

> Hoy a las HH:MM vamos a actualizar el sistema. Puede dejar de responder unos segundos mientras se reinicia. Si tenías un pedido, una cotización o un pago abierto antes de eso, la primera vez que lo guardes va a salir el aviso «Este formulario venció y no se guardó»: no perdiste lo que escribiste, revisa los datos y vuelve a guardar. Después de la actualización, cierra la pestaña y abre la aplicación de nuevo (o pulsa Ctrl+F5). Notarás que los botones de guardar dicen «Guardando…» y se bloquean un momento: es para que un doble clic no cree el pedido dos veces. Si algo no funciona, cuéntanos en qué pantalla estabas y a qué hora.

### Decisión 5 · Vigilancia de una semana

La vigilancia la hace el desarrollador (los agentes no tocan PythonAnywhere). Cada lectura consume CPU de los 100 s diarios de la consola; los comandos de `despliegue.md`, 3.7 y 3.9, son cortos. `R` es la hora del reinicio efectivo (`Starting uWSGI`, hora de Chile), la oficial.

**5a · Qué se lee, cuándo y cuándo se cierra**

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Siete días corridos desde `R`, cuatro lecturas y medición de duplicados con `access.log` y conteo de pedidos (recomendada)** | Lecturas: **día 0** (a la hora de `R`, una hora después y al cierre de la jornada), **día 1**, **día 3** y **día 7** (misma hora que `R`). Cada lectura: (1) `nivel=ERROR` de `server.log` desde `R`, por ruta, sin copiar el texto; (2) respuestas 5xx y conteo de `POST` de las rutas de creación por código de estado en `access.log`; (3) tiempo de respuesta de `GET /pedidos/nuevo/`, `/cotizaciones/nueva/` y `/pagos/ingresar/` (+3 consultas aceptadas); (4) líneas `nivel=INFO` «Envío sin token válido» (esperadas el día 0 por los formularios abiertos; después, pocas). **Duplicados:** conteo de `POST /pedidos/nuevo/` con 302 contra pedidos nuevos en la base de ese día (conteo de solo lectura del desarrollador) | Cumple el criterio de la definición (una semana, `server.log`). La comparación 302/pedidos nuevos sí distingue un envío repetido rechazado de uno guardado, que `access.log` solo no distingue | Exige una consulta de solo lectura a la base de producción hecha por el desarrollador y un guion nuevo (`PENDIENTE_DESARROLLADOR`, se escribe al ejecutar; no existe hoy) |
| **B. Lo mismo, pero medir duplicados solo con el guion de la 00-07 (`segundos_repetidos`)** | Reutiliza la parte D de la 00-07 | Ya existe y está probado en el formato de `access.log` | Después de la 03-05 un doble envío rechazado también responde 302 en el mismo segundo: `segundos_repetidos > 0` no probaría un duplicado y `= 0` no probaría nada más que la ausencia de dobles envíos (ver «Avisos») |
| **C. Tres días** | Acorta la vigilancia | Menos trabajo | Contradice la definición de la épica («una semana») y el plan: habría que cambiarlos con una nota fechada |

**Criterio de cierre propuesto (para A):** (i) siete días desde `R` sin `nivel=ERROR` nuevo de `django.request` ni de `pedidos.views` en las rutas modificadas, descontando las líneas ya clasificadas (`registrador=root`, `OSError: write error`, AUD-04-004) y los `ERROR` de ítem fallido que se expliquen (ver decisión 6); (ii) ningún 5xx en las rutas de creación y edición; (iii) ningún pedido, cotización ni pago duplicado en la ventana; (iv) tiempos de respuesta de los tres formularios sin salir de la banda que ya se midió en producción (de 0,03 a 1,13 s fuera de las recargas, Auditoría 04) (inferido: la banda es de todo el sitio, no de estas rutas); (v) la línea `INFO` verificada (5b). El umbral de «sin salir de la banda» es `PENDIENTE_DESARROLLADOR`.

**5b · La línea `INFO` del rechazo, «por verificar en producción» (`despliegue.md`, 3.9)**

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Una verificación deliberada el día 0 (recomendada)** | En `/pedidos/nuevo/` (o `/pagos/ingresar/`), borrar el valor del campo oculto `token_envio` con la consola del navegador y guardar. Debe salir el aviso «Este formulario venció y no se guardó…», no crearse nada y quedar **una** línea `nivel=INFO` en `server.log` con método, ruta y usuario | Resultado en minutos. La prueba automática lo garantiza en local y la revisión de servidor lo vio en la réplica | Es un envío en producción: no debe crear ningún registro (inferido de `test_pedido_sin_token_no_crea_nada…` y de la comprobación 9 de la revisión de servidor), pero ahí se prueba por primera vez. La revisión de la 00-07 evitó, a propósito, enviar formularios |
| **B. Esperar la observación natural** | Mirar si aparece al reiniciar por los formularios abiertos | No se toca nada | Si nadie tenía un formulario abierto, no aparece y la semana termina sin verificarla |
| **C. No verificarla; quitar la línea de la guía al cerrar** | Dejar `despliegue.md`, 3.9, sin esa fila | Sin riesgo | Pierde la señal de «formulario vencido» para los reportes |

### Decisión 6 · Retroceso y qué hacer si aparece un `ERROR` nuevo

El retroceso es el caso 1 de `retroceso.md`: `git checkout v0.3-doble-envio`, `collectstatic --noinput` (porque la etiqueta nueva cambió `index.js`; paso 3 del caso 1), `check`, **Reload** y verificar las tres pantallas. Sin migraciones que deshacer. Una sesión con la clave `tokens_envio` no molesta al código anterior, que no la lee (inferido; no ensayado).

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Regla escrita antes del despliegue (recomendada)** | (1) **Datos incorrectos o perdidos** (montos, pedidos, pagos): detener, avisar y evaluar el caso 3 (restaurar). (2) **5xx repetido** o formulario que no guarda en una vista modificada: retroceder (caso 1). (3) **Un `ERROR` aislado** de ítem fallido con aviso en pantalla: no retroceder; sacar la traza (`despliegue.md`, 3.9), reproducir en la réplica y registrar en la evidencia solo el tipo y la hora. (4) **Líneas `INFO` de rechazo:** sin acción. Todo `ERROR` nuevo se clasifica con la tabla de 3.9 antes de decidir | Evita retroceder por un `ERROR` esperado y evita no retroceder ante uno grave. La réplica queda disponible para reproducir (decisión 7) | Los umbrales de «repetido» y «aislado» son criterio del desarrollador y no tienen número hoy (`PENDIENTE_DESARROLLADOR`) |
| **B. Retroceder ante cualquier `ERROR` nuevo** | Conservador | Simple | El ítem fallido ahora deja un `ERROR` **por diseño** (decisión 3-B de la 03-04): se retrocedería por el comportamiento previsto. Además se pierde el token de envío único otra vez (AUD-04-001, Alta) |
| **C. No retroceder: corregir hacia adelante con una etiqueta nueva** | Arreglar y desplegar de nuevo | Evita volver a un estado con el defecto de duplicados | Un solo desarrollador, sin ambiente de ensayo en producción y con 1 worker: mientras se corrige, el error sigue. Contradice el propósito de la etiqueta de retroceso (RDA-007) |

### Decisión 7 · Limpieza de la réplica y AUD-05-002

Documentado: la decisión del desarrollador del 2026-11-04 deja el traslado del disco de Docker a D: (o el cifrado de C:) y el refresco de la réplica «al cerrar la Épica 03», con el respaldo del 2026-11-04 00:12:37 y sin respaldo nuevo, «para no retrasarla» (AUD-05-002; `replica-local.md`, sección 9). El refresco también limpia los datos de prueba de la 03-03 y la 03-04 y obliga a **repetir el conteo de pedidos sin ítems** de la 03-02 (registro, sección 3) y a repetir la comprobación de cifrado (`replica-local.md`, sección 2), que hoy no pasa.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Como paso final de la 03-05, después de cerrar la vigilancia (recomendada)** | Es la última tarea de la iteración, y con ella se cierra la Épica 03. Fuente: el respaldo de la decisión 2 si se hizo (ya existe, no se genera otro solo para esto), o el del 2026-11-04 | Respeta la decisión del 2026-11-04. Deja la réplica con los datos de las revisiones para reproducir cualquier `ERROR` de la semana. Evita que quede como pendiente suelto | AUD-05-002 (Media) sigue abierto unas dos semanas más: la réplica tiene datos reales y hashes de contraseñas en un disco sin cifrar |
| **B. Antes del despliegue** | Trasladar el disco y refrescar con el respaldo de la decisión 2 | Cierra el riesgo de seguridad cuanto antes | Cambia la decisión del 2026-11-04. Elimina la réplica donde se reproducirían los errores de la vigilancia. Suma trabajo antes de una fecha ya apretada (2026-11-10 y 2026-11-11) |
| **C. Fuera de la 03-05, como tarea de Operación al cerrar la épica** | Se hace después, sin ligarla a la iteración | La 03-05 queda solo con el despliegue | Es lo que hoy figura en el registro y es fácil que se postergue otra vez; la épica se cerraría con AUD-05-002 abierto |

### Decisión 8 · Estado de las regresiones al desplegar

Documentado: `pruebas.md`, sección 7.1, **valor vigente `expected failures=9`** (R6a, R6b, R6c, R7, R8, R9, R14, R15 y R19) y 267 pruebas en la última medición, `OK (expected failures=9)` en tres ejecuciones (2026-11-06, [bitacora-03-04-correccion-abono](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-correccion-abono.md)). `despliegue.md`, lista de comprobación, punto 1: cualquier `failures`, `errors` o `unexpected successes` detiene el despliegue; el N de `expected failures` debe coincidir con las regresiones declaradas.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Una ejecución el día del despliegue, sobre el commit que se etiqueta, con `OK (expected failures=9)` y 267 pruebas (recomendada)** | `python manage.py test pedidos` con el árbol limpio, más `check --deploy` (con `DEBUG=False`; solo las advertencias conocidas W004, W008, W009, W012 y W016) y `makemigrations --check --dry-run` (`No changes detected`). Si el recuento no es exacto, se detiene | Es lo que pide `despliegue.md`. No hay cambios de código desde las tres ejecuciones iguales del 2026-11-06 (`git diff` sin salida desde `7e14398`) | Una ejecución sola no detectaría una prueba intermitente. Duran entre 4 y 6 minutos (240 a 350 s) |
| **B. Tres ejecuciones seguidas** | El estándar de las iteraciones 03-01 a 03-04 | Más confianza | Unos 15 minutos de reloj extra; el código no cambió |
| **C. Desplegar con `OK` limpio, retirando las marcas de las 9** | — | — | **No.** Son defectos reales declarados (pendientes en la 04-01, 04-06, 06-01 y 06-05); quitar la marca los ocultaría y haría fallar el conjunto |

- **Estas 9 no viajan corregidas:** R6a, R6b, R6c, R7 y R19 (04-01), R14 (04-06), R8 y R9 (06-01), R15 (06-05, según `pruebas.md`; ver «Avisos»).

## Tareas (en este orden, una vez tomadas las decisiones)

Las hace el desarrollador salvo donde se dice. Ningún agente toca PythonAnywhere, crea etiquetas ni hace `push`.

0. **Precondiciones:** 00-07 medida (parte D, 2026-11-11, hacia las 01:32) y su resultado anotado; web app renovada (2026-11-10); `git status --short` vacío y `main` igual a `origin/main`.
1. **Pedir la evidencia** (agente, al empezar la ejecución): crear `10_epicas/epica-03-integridad-transaccional/evidencia-03-05.md` con la plantilla 6.3 de `_planificacion/README.md` y los comandos listos. No se crea en esta redacción porque depende de las decisiones 2, 3 y 5.
2. **Lista de comprobación previa** (`despliegue.md`, sección 2) en el PC: pruebas (decisión 8), `check --deploy`, `makemigrations --check --dry-run`, `showmigrations pedidos` (ninguna migración nueva), respaldo (decisión 2), «Estilos compilados: no aplica», etiqueta.
3. **Etiqueta** (decisiones 1 y 3): `git diff --stat <hash>..main -- . ":(exclude)_planificacion" ":(exclude)docs"` vacío, `git tag -a`, `git push origin`, `git ls-remote --tags origin`.
4. **Aviso al cliente** (decisión 4), con la hora acordada.
5. **Despliegue** (`despliegue.md`, 3.1 a 3.6): ubicarse, `git fetch origin --tags`, `git checkout <etiqueta>`, **sin dependencias** (3.3: `requirements.txt` no cambió), **sin migraciones** (3.4: `No planned migration operations.`), **`collectstatic --noinput`** (3.5: cambió `index.js`), **Reload** y anotar la hora del reinicio efectivo `R`.
6. **Verificación inmediata, solo lectura** (3.7): ventana privada, acceso, panel, listado y detalle de pedidos; además, sin crear nada: que `/pedidos/nuevo/`, `/cotizaciones/nueva/` y `/pagos/ingresar/` carguen y que el código fuente de cada una traiga el campo `token_envio`. Registro de errores desde `R`.
7. **Verificar la línea `INFO`** (decisión 5b) y **vigilar** (decisión 5a): lecturas de los días 0, 1, 3 y 7.
8. **Si aparece un `ERROR` nuevo:** clasificar (3.9) y aplicar la regla de la decisión 6.
9. **Cierre documental** (agente, con la evidencia que responda el desarrollador): `bitacora-03-05-produccion.md`; fila en `despliegue.md`, sección 5 (registro de despliegues); notas fechadas en AUD-04-001 y en los hallazgos que dicen «se despliega con la 03-05» (sin borrar lo anterior); el texto de `despliegue.md`, 3.9, según el resultado de 5b; `registro-pendientes.md`; estado de la 03-05 y de la Épica 03 (nota fechada en `definicion-epica-03.md`).
10. **Operación** (decisión 7): traslado del disco de Docker, refresco de la réplica, conteo de pedidos sin ítems y comprobación de cifrado, según la opción elegida.

## Criterios de aceptación

- [ ] Las decisiones 1 a 8 están registradas antes de ejecutar.
- [ ] Pruebas, `check --deploy` y `makemigrations --check --dry-run` del día del despliegue anotados, con `OK (expected failures=9)`, 267 pruebas y `No changes detected` (o la desviación explicada).
- [ ] Respaldo previo según la decisión 2, verificado (código 0) y anotado en `respaldo.md`, sección 6.
- [ ] Etiqueta anotada publicada y comprobada con `ls-remote`; destino de retroceso anotado.
- [ ] Despliegue hecho por los pasos de `despliegue.md`, con `collectstatic`, sin migraciones; hora `R` anotada.
- [ ] Verificación inmediata sin errores desde `R`; los tres formularios traen `token_envio`.
- [ ] La línea `INFO` verificada, o su estado explicado (decisión 5b).
- [ ] Siete días desde `R` con el criterio de cierre de la decisión 5a cumplido, o cada excepción explicada.
- [ ] `access.log` y el conteo de pedidos sin duplicados por envío repetido (AUD-04-001, criterio de término).
- [ ] Fila en el registro de despliegues de `despliegue.md`; notas fechadas en los hallazgos; bitácora de producción.
- [ ] AUD-05-002 y la limpieza de la réplica resueltas o reprogramadas por escrito (decisión 7).
- [ ] Los `PENDIENTE_CLIENTE` abiertos siguen sin cambios de comportamiento: AUD-02-014, pedido de $0 como pagado y sobrepago, y la hora de poco uso.

## Fechas de operación

| Fecha | Qué | Fuente | Estado |
| :---- | :-- | :----- | :----- |
| 2026-11-10 | Renovar la web app de PythonAnywhere (vence el 2026-11-20) | `registro-pendientes.md` (cabecera y sección 3, AUD-01-019) | Documentado. No verificado si ya se hizo ni cuánto extiende la renovación |
| 2026-11-10 u 11 | Próximo respaldo semanal | `registro-pendientes.md` (cabecera) | Documentado. Puede ser el de la decisión 2 si cae el mismo día |
| 2026-11-11, hacia las 01:32 (hora de Chile; 04:32 UTC) | Medición de `access.log` de la 00-07 (parte D) y, con ella, cierre de la 00-07 | [evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md), `registro-pendientes.md` | Documentado en tres lugares; coinciden con lo dicho por el desarrollador. No medible desde aquí |
| Desde el 2026-11-11, tras la medición | Primer momento posible para el despliegue de la 03-05 | Esta redacción (decisión 3) | Propuesta |
| Hasta el 2026-11-13 | Último reinicio `R` con el que la semana de vigilancia termina el 2026-11-20 | Cálculo de esta redacción | Propuesta |
| 2026-11-20 | Vence la web app si no se renueva | `registro-pendientes.md` (cabecera) y [bitacora-00-02](../../99_bitacora/epica-00-blindaje/bitacora-00-02.md) | Documentado |
| 2026-11-20 | Informe de desconexiones a 28 días (parte C2 de [evidencia-00-06](../epica-00-blindaje/evidencia-00-06.md)) | `registro-pendientes.md`, sección 3 | Documentado. La recarga del despliegue de la 03-05 figurará en los conteos de reinicios: anótala para poder separarla (inferido) |

## Fuera de alcance

- Corregir defectos de código, plantillas o JavaScript. Los hallazgos de la vigilancia se registran y se deciden aparte.
- AUD-05-005 a AUD-05-008, el candado de precio y cualquier cambio de presentación: Épica 08.
- Que los mutadores acepten solo POST, la plantilla de eliminar pago, `duplicar_pedido` con `creado_por` (04-01) y las 9 regresiones restantes.
- Consulta histórica de pedidos duplicados (06-04) e indicador de carga (08-07), que mantienen abierto AUD-04-001.
- Respaldo periódico de `media/` (AUD-02-023) y borrar imágenes huérfanas.
- Un mensaje de aviso dentro de la aplicación (decisión 4, opción C).
- `DESIGN.md`, `README.md` y los demás documentos protegidos.

## Despliegue

- Esta iteración **es** el despliegue de la Fase 3 (RDA-007): una etiqueta anotada, sin migraciones, con `collectstatic`.
- Respaldo, ventana, aviso, vigilancia y retroceso: decisiones 2 a 6.
- Los formularios abiertos al reiniciar no traen token y se guardan al segundo intento (decisión 7 de la 03-04).

## Riesgos

| Riesgo | Mitigación |
| :----- | :--------- |
| Desplegar antes de la medición de la 00-07 la contamina | Decisión 3-A; precedente de la 01-09 |
| La recarga deja unos 10 s de 502 y un POST en ese lapso se pierde (AUD-04-002) | Ventana de madrugada o de fin de semana (decisión 3) y aviso (decisión 4) |
| Cuatro iteraciones juntas: si falla, se retrocede todo | Retroceso del caso 1 (sin migraciones), regla de la decisión 6, lista de comprobación completa |
| Un `ERROR` esperado (ítem fallido) se confunde con uno nuevo | Tabla de `despliegue.md`, 3.9, y decisión 6 |
| Con la 03-05 desplegada, `access.log` ya no distingue un duplicado rechazado de uno guardado | Decisión 5a: comparar con el conteo de pedidos nuevos |
| El token suma entradas a la sesión (hasta 20 por sesión) y suma consultas | Costo aceptado el 2026-11-04. No se encontró ninguna purga de sesiones en el repositorio (búsqueda de `clearsessions`, sin resultados): la sesión dura 14 días y el disco es escaso (inferido: el tamaño es pequeño; no medido) |
| El navegador conserva el `index.js` anterior | Aviso con Ctrl+F5 (decisión 4); no hay nombre con hash en los estáticos |
| La 03-05 se atrasa y la semana de vigilancia cae sobre el 2026-11-20 | Decisión 3: `R` hasta el 2026-11-13 para terminar a tiempo; renovar la web app el 2026-11-10 |
| Retroceder deja sin token ni bloqueo de botón en las pantallas nuevas | Regla de la decisión 6: retroceder solo ante 5xx repetido o datos incorrectos |
| La limpieza de la réplica borra el lugar donde reproducir errores | Decisión 7-A: después de la vigilancia |

## Avisos (contradicciones o tensiones con RDA, decisiones o documentos; sin corregir)

1. **Criterio de término contra `access.log`.** La definición pide que «`access.log` no muestre pedidos duplicados por envío repetido». Con el token, el segundo POST responde 302 igual que el primero y `access.log` no registra el destino (inferido del formato, que lleva el código de estado pero no la redirección). El guion de la 00-07 queda como señal, no como prueba. Se propone medir con el conteo de pedidos (decisión 5a).
2. **Plan 3.5 contra RDA-013.** El plan pide vigilar «mediante las tablas de registro de la Fase 1»; RDA-013 descartó la tabla de errores y el diagnóstico va en `server.log`. La definición de la épica ya lo dice así. `plan-de-trabajo.md` no se edita.
3. **«Un despliegue, un propósito» (RDA-007) contra cuatro iteraciones.** `despliegue.md` lo permite para «una fase cerrada»; aun así, la 03-04 ya mezcló el contrato de error y el envío único (decisión 10 de la 03-04) y esta etiqueta suma la 03-01 a la 03-03. Se recomienda la etiqueta única; la opción B de la decisión 1 es la salida si no te parece.
4. **Respaldo: las iteraciones dicen «lo decide el desarrollador en la 03-05»; los procedimientos ya lo piden.** `respaldo.md`, sección 5, y `despliegue.md`, punto 5 de la lista, piden respaldo antes del primer despliegue de una fase. La decisión 2 lo recomienda por eso.
5. **AUD-05-002: «sin respaldo nuevo».** La decisión del 2026-11-04 evitaba generar un respaldo solo para refrescar la réplica. Si la decisión 2 es A, ese respaldo existirá y podría ser la fuente: cambia el texto de esa decisión.
6. **La 03-02 describe un comportamiento que la 03-04 cambió.** [iteracion-03-02](iteracion-03-02-erradicacion-supresion-silenciosa.md), «Despliegue», dice que un ítem fallido al crear un pedido deja una línea de `django.request` y muestra la página 500; desde la decisión 3-B de la 03-04 devuelve el formulario (200) con una línea `ERROR` de `pedidos.views`. Vale lo de la 03-04 y `despliegue.md`, 3.9. `despliegue.md`, sección 0, también dice que «un error en cualquier vista deja una sola línea `django.request`»: sigue valiendo para excepciones no previstas.
7. **`R15`.** [iteracion-03-04](iteracion-03-04-contrato-de-error-hacia-el-usuario.md) dice que la corrigen «la 04-01, 04-06, 06-01 y 07-02»; `pruebas.md`, sección 7.1, dice 06-05. Aquí se sigue `pruebas.md`.
8. **Épica 03 sigue «Pendiente».** Cuatro de sus cinco iteraciones están Terminadas y el estado de la épica no cambia hasta cerrar la 03-05 (precedente de las notas de `definicion-epica-03.md`).
9. **El aviso de la decisión 4 es texto nuevo** para el usuario: no está entre los «Textos aprobados» de la 03-04 y necesita aprobación.

## No pude ver ni verificar

- **Producción:** qué etiqueta corre hoy, el contenido de `server.log` y `access.log`, la hora de uso del cliente, si la renovación del 2026-11-10 se hizo y cuánto extiende. Todo lo anterior viene de documentos.
- **Etiquetas:** `git tag` y `git tag -n` están fuera de lo que puedo ejecutar (`AGENTS.md`, sección 6). Las etiquetas existentes salen de `despliegue.md` y las evidencias: `v0.0-inicial`, `v0.1-higiene`, `v0.2-correcciones`, `v1.1-observabilidad`, `v1.2-capturas` y `v0.3-doble-envio`. No comprobé que `v3.1-integridad` esté libre.
- **Hora de poco uso** (`PENDIENTE_CLIENTE`) y canal para avisar.
- **Caché de `index.js`** en el navegador del cliente (inferido por la ausencia de nombre con hash).
- **Línea `INFO` en producción** (decisión 5b) y **retroceso con sesiones que traen `tokens_envio`** (inferido, no ensayado).
- **Costo de las +3 consultas en producción:** medido solo en la réplica.
- **Pruebas, `check` y `makemigrations`:** no se ejecutaron en esta redacción; las cifras (267 pruebas, `expected failures=9`) salen de la bitácora del 2026-11-06.

## Decisiones del desarrollador

Ninguna tomada. Las ocho figuran como `PENDIENTE_DESARROLLADOR` en `registro-pendientes.md`, sección 3.

## Datos requeridos del cliente

- **`PENDIENTE_CLIENTE`:** en qué horas de entre semana la aplicación se usa menos, para elegir la ventana del despliegue (decisión 3). Solo consta que el negocio cierra el sábado en la tarde y no hay uso hasta el lunes; no hay medición de horas.
- **Siguen abiertos, sin cambiar de comportamiento aquí:** valor de una cotización neto o con IVA (AUD-02-014), pedido de $0 como pagado y sobrepago (`registro-pendientes.md`, sección 2).
