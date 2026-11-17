# Iteración 03-05 · Validación y despliegue de la integridad

- **Épica:** 03 · Integridad transaccional
- **Estado:** **En vigilancia (día 0 hecho el 2026-11-16).** Desplegada como `v3.1-integridad` el lunes 2026-11-16 por la noche, con `R` = **23:48:12** (hora de Chile; 2026-11-17 02:48:12 UTC). Día 0 sin 500, con `token_envio` en los tres formularios y la línea `INFO` verificada; quedan la lectura del **día 7** (desde el lunes 2026-11-23 a las 23:48:12, o el martes 2026-11-24) y la limpieza de la réplica (parte F). **La Épica 03 no está Terminada** y ningún hallazgo pasa a «Resuelto» antes del día 7. Ver «Ejecución del día 0 (2026-11-16)» y [bitacora-03-05-produccion](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-produccion.md).
- **Estado anterior (2026-11-06, reprogramado el 2026-11-16 para el martes 2026-11-17; superado el 2026-11-17 por la ejecución del día 0; se conserva como registro):** Pendiente (redactada, decisiones resueltas; **reprogramada el 2026-11-16 para el martes 2026-11-17**, ver «Reprogramación del 2026-11-16»). Redactada el 2026-11-06 ([bitacora-03-05-redaccion](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-redaccion.md)); las ocho decisiones las resolvió el desarrollador el mismo día ([bitacora-03-05-decisiones](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-decisiones.md); detalle en «Decisiones del desarrollador»). Sin ejecutar: ni pruebas, ni respaldo, ni etiqueta, ni despliegue. Pasos listos en [evidencia-03-05](evidencia-03-05.md). Ronda final del 2026-11-06 registrada (aviso aprobado, ~~jueves 2026-11-12~~ martes 2026-11-17 desde el 2026-11-16, umbral de tiempos y números del retroceso): **solo falta elegir la fuente del respaldo para refrescar la réplica** (parte F1 de la evidencia, `PENDIENTE_DESARROLLADOR`). **Bloqueada** hasta anotar la medición de la 00-07 (~~2026-11-11~~: no se hizo ese día; se mide antes del despliegue del 2026-11-17).
- **Subfase del plan:** 3.5 «Validación y despliegue» (`plan-de-trabajo.md:364-371`)
- **Depende de:** 03-04 (Terminada el 2026-11-06) y de la medición de la 00-07 (parte D de [evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md), ~~2026-11-11, hacia las 01:32 hora de Chile~~ no se hizo ese día; se midió el 2026-11-16 hacia las 23:13 y cumple, ver «Ejecución del día 0 (2026-11-16)»)
- **RDA relacionadas:** RDA-007 (rama única y etiqueta anotada antes de cada despliegue; un despliegue lleva un solo propósito), RDA-013 (diagnóstico en `server.log`, sin identificador ni tabla de errores), RDA-019 (los errores de vista los maneja Django).
- **Hallazgos que cierra:** AUD-04-001 en la medición de producción que le faltaba (la parte de servidor ya está «Resuelto en 03-04» en código); confirma en producción los que hoy dicen «se despliega con la 03-05»: AUD-01-001, AUD-01-002, AUD-02-004 (el código; las filas históricas no se reparan), AUD-02-005, AUD-02-008, AUD-02-027 y AUD-02-029.
- **Hallazgos relacionados:** AUD-02-006 (avance de la 03-04; sigue abierto por el GET, 04-01), AUD-02-021 (13 errores de plantilla sin causa conocida: la semana de `server.log` puede aportar evidencia, no se asume), AUD-02-023 (imágenes de `media/` sin copia: no se tocan), AUD-04-002 (cada recarga deja unos 10 s de 502), AUD-04-004 (líneas `OSError: write error`, ya clasificadas), AUD-05-002 (disco de Docker de la réplica en C:).
- **Cambio de esquema:** Ninguno (verificado el 2026-11-06 con `git diff`, ver «Qué viaja»).
- **Respaldo previo al despliegue:** nuevo el día del despliegue, verificado antes de recargar (decisión 2, opción A, resuelta el 2026-11-06).
- **Etiqueta y ventana:** `v3.1-integridad` (convención de `despliegue.md`, sección 1), el ~~**jueves 2026-11-12**~~ ~~**martes 2026-11-17**~~ **lunes 2026-11-16** (ejecutado ese día; `R` 23:48:12, fuera de la ventana por decisión del desarrollador), con ventana prevista entre las 20:00 y las 23:00 (hora de Chile) (decisión 3, resuelta el 2026-11-06; reemplaza «de madrugada»; el día se fijó en la ronda final del mismo día y se movió el 2026-11-16). Día 7: ~~jueves 2026-11-19~~ ~~martes 2026-11-24 por la noche~~ desde el lunes 2026-11-23 a las 23:48:12, o el martes 2026-11-24.

## Reprogramación del 2026-11-16

> **Nota (2026-11-17):** las fechas de esta sección (despliegue el martes 2026-11-17, día 7 el martes 2026-11-24) quedaron superadas por la ejecución: el despliegue fue el lunes 2026-11-16 y el día 7 se lee desde el lunes 2026-11-23 a las 23:48:12, o el martes 2026-11-24. Se conserva como registro; vale «Ejecución del día 0 (2026-11-16)».

**Qué pasó.** El despliegue previsto para el jueves 2026-11-12 no se hizo. Verificado el 2026-11-16 en GitHub: la etiqueta `v3.1-integridad` no existe y no hay commits posteriores a `a1653dd` (2026-11-06). Medido en local el mismo día: `HEAD` sigue en `a1653dd` y `git diff --stat 7e14398..HEAD` (sin `_planificacion` ni `docs`) no da salida, así que el código es el de las tres ejecuciones de pruebas del 2026-11-06. Detalle en [bitacora-03-05-reprogramacion](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-reprogramacion.md).

**Dicho por el desarrollador (2026-11-16; el agente no lo verificó):**

- La medición de `access.log` de la 00-07 (parte D) **no se hizo** el 2026-11-11.
- La web app vence el **2026-12-13**, no el 2026-11-20 que dicen los documentos. El 2026-11-20 queda solo para el informe C2 de la 00-06.
- **Por confirmar por el desarrollador en el servidor** (`PENDIENTE_DESARROLLADOR`): que producción sigue en `v0.3-doble-envio` (`git status` limpio y `Starting uWSGI` sin más reinicios que el del 2026-11-04 01:32:51, o los que se expliquen).

**Decisión del desarrollador (2026-11-16), sobre la decisión 3:** nueva ventana el **martes 2026-11-17**, de 20:00 a 23:00 (hora de Chile), en lugar del jueves 2026-11-12. Día 7: **martes 2026-11-24** por la noche. Las demás decisiones (1, 2 y 4 a 8) no cambian.

| Qué | Cómo queda |
| :-- | :--------- |
| Medición de la 00-07 | Sigue siendo **precondición**. Se mide antes del despliegue (hoy por la noche o el 2026-11-17 durante el día), con 12 o 13 días desde el reinicio del 2026-11-04 01:32:51 en lugar de siete. El guion de la parte D de [evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md) se ajustó el 2026-11-16: el original solo miraba los 8 últimos días y habría dejado fuera los primeros. La 03-05 sigue bloqueada hasta anotar el resultado |
| Tope «`R` hasta el 2026-11-13» | Ya no rige: venía del vencimiento del 2026-11-20 y la web app vence el 2026-12-13. La vigilancia (11-17 a 11-24) termina 19 días antes |
| Informe C2 de la 00-06 (2026-11-20) | Cae **a mitad de la vigilancia** y la **recarga del 2026-11-17 entra en sus conteos** (reinicios y desconexiones a 28 días). Hay que separarla usando `R`, la hora oficial (`Starting uWSGI`): anótala al desplegar y excluye o marca aparte esa recarga y sus unos 10 s de 502 (AUD-04-002). Sugerencia, sin decidir: aprovechar esa lectura de registros para una lectura a demanda de la 03-05 (C5 y C6 de la evidencia) |
| Aviso al cliente | El texto aprobado dice «Hoy a las HH:MM»: **sigue valiendo si se envía el martes 2026-11-17 antes de las 20:00**, el mismo día de la actualización. Si se enviara otro día habría que cambiar «Hoy» por el día; es un cambio de una palabra sobre un texto aprobado y lo confirma el desarrollador. No consta si el cliente recibió algún aviso para el 2026-11-12 (`PENDIENTE_DESARROLLADOR`): si lo recibió, conviene decirle que cambió |
| Respaldo | El del despliegue se hace el 2026-11-17, poco antes de las 20:00. No consta si el semanal de hacia el 2026-11-10 u 11 se hizo (`PENDIENTE_DESARROLLADOR`); si no se hizo, el del despliegue puede contar también como semanal (decisión 2-A) |
| Producción | Se supone `v0.3-doble-envio` (documentado). B1 de la evidencia lo comprueba antes de tocar nada: `git describe --tags --always` debe decir `v0.3-doble-envio` y `git rev-parse --short HEAD`, `5dc82a8` |

Lo anterior (tablas de opciones, decisiones del 2026-11-06 y fechas del jueves 2026-11-12) se conserva como registro; donde difiere, vale esta sección.

## Ejecución del día 0 (2026-11-16)

El despliegue se hizo la noche del **lunes 2026-11-16**, un día antes de lo reprogramado (martes 2026-11-17), con `R` a las 23:48:12, fuera de la ventana de 20:00 a 23:00 por decisión del desarrollador. Datos dichos por el desarrollador el 2026-11-17, de sus consolas, en hora de Chile; el agente no vio ninguna salida. El detalle por paso, con lo que no se informó, está en las partes A a C de [evidencia-03-05](evidencia-03-05.md) y en [bitacora-03-05-produccion](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-produccion.md). **Donde difiere de «Reprogramación del 2026-11-16», vale esta sección.**

| Qué | Resultado |
| :-- | :-------- |
| 00-07 (precondición) | Medida el 2026-11-16 hacia las 23:13: 12 días con registro (2026-11-04 a 2026-11-16), todos con `segundos_repetidos=0`; 2026-11-08 y 2026-11-17 (UTC) con `lineas=0`: sin medir. **Cumple** |
| Pruebas y comprobaciones (A1) | 267 pruebas, `OK (expected failures=9)`; `check --deploy` con `W004 W008 W009 W012 W016`; `makemigrations` sin cambios; sin diferencias en migraciones, `requirements.txt` ni `settings.py` |
| Respaldo (A2) | `respaldo_16-11-2026_23-34-18.sql`, 1.525.277 bytes, 19 de 19, `VÁLIDO`, código 0 (SHA-256 completo en la evidencia y en `respaldo.md`) |
| Etiqueta (A3) | `v3.1-integridad` sobre `7e14398` (objeto `c05a16b8…`); retroceso `v0.3-doble-envio` (`e68f8721…`) |
| Servidor (B) | Antes: `5dc82a8`, 106 sesiones, 23:43:18. Después: `collectstatic` 1 archivo, `check` limpio. **`R` = 2026-11-16 23:48:12** |
| Día 0 (C) | C1 sin 500 y `token_envio` en las tres pantallas. C2 `bloqueado=true` y «Guardando…» (ventana privada: **no prueba el caché**). C4 a las 23:58:23: línea `INFO` verificada y ningún pago creado. C5: 1 `ERROR` (`root`, `OSError: write error`, 23:55:10, AUD-04-004) y 1 `INFO`. C6: ningún `POST /pedidos/nuevo/`, todos los conteos en 0 (**sin tráfico: no pone a prueba el criterio de duplicados**) |
| Hallazgo nuevo | AUD-05-009 (Baja, Épica 08): `pago_form.html` usa `$(document).ready` antes de que `base.html` cargue jQuery («$ is not defined»). Idéntico en `v0.3-doble-envio` (verificado por el desarrollador): **no es una regresión** |

**Desviaciones:** despliegue el 2026-11-16 en vez del 2026-11-17; `R` fuera de las 20:00 a 23:00; el aviso decía 22:30 y `R` fue 23:48:12; el `diff` de A3 falló en PowerShell y se repitió con comillas; C2 en ventana privada; varias salidas de A1, B2 a B6 no informadas.

**Lo que sigue:** el cliente hace Ctrl+F5 el martes 2026-11-17 de día (dicho por el desarrollador); el viernes 2026-11-20 se hace el informe C2 de la 00-06 y **la recarga de `R` entra en sus conteos** (sepárala usando `R`); el día 7 se lee desde el lunes 2026-11-23 a las 23:48:12 (02:48:12 UTC del 11-24) o el martes 2026-11-24; la web app está renovada hasta el 2026-12-13.

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

Medido hoy: `git diff --stat 5dc82a8..HEAD -- . ":(exclude)_planificacion" ":(exclude)docs"` → **30 archivos, 1.957 inserciones y 456 eliminaciones**. Y `git diff --stat 7e14398..HEAD` con la misma exclusión → **sin salida**: desde el último commit de código (`7e14398`, corrección del abono) solo cambian documentos. `git status --short` está vacío y `HEAD` es igual a `origin/main` (`c9db60e`). **Nota 2026-11-16:** desde entonces solo hubo commits de documentos; `HEAD` es hoy `a1653dd` y `git diff --stat 7e14398..HEAD` con la misma exclusión sigue sin salida (medido el 2026-11-16).

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

- **Documentado:** la parte D de [evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md) se mide el **2026-11-11, hacia las 01:32** (hora de Chile; 04:32 UTC; una semana después del reinicio efectivo del 2026-11-04). Cuenta por día en UTC los `POST /pedidos/nuevo/` y los segundos con dos o más; esperado `segundos_repetidos=0`. Aparece igual en `registro-pendientes.md` (cabecera y «Fechas vigentes»). El desarrollador lo dijo; los tres documentos coinciden. **Nota 2026-11-16:** ~~2026-11-11~~ no se midió ese día (dicho por el desarrollador). La medición sigue siendo precondición y se hace antes del despliegue del 2026-11-17, con 12 o 13 días desde el reinicio y el guion ajustado de la parte D de la evidencia-00-07.
- **Por qué no se despliega antes (inferido):** esa medición mide el efecto del botón de la 00-07. Con la 03-05 en producción, el segundo POST de un doble envío responde 302 como el primero y `pedido_form.html` cambió (37 líneas), así que dejaría de poder atribuirse el resultado al botón. Es el mismo motivo del precedente de la 01-09.

## Decisiones

**Resueltas el 2026-11-06** (ver «Decisiones del desarrollador», al final; una ronda final del mismo día fijó el texto del aviso, el día, el umbral de tiempos y los números del retroceso): las tablas quedan como estaban al redactar, como registro de las opciones. Al redactar eran `PENDIENTE_DESARROLLADOR` (y una `PENDIENTE_CLIENTE`, la hora de uso, que la decisión 3 reemplazó). La recomendada iba primero en cada tabla. Dependencias: la 3 condiciona la 4 y la 5; la 2 condiciona la 7; la 1 y la 8 fijan lo que se prueba y se etiqueta.

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

Precondición: **no desplegar antes de la medición de la 00-07** (~~del 2026-11-11, hacia las 01:32~~; reprogramada el 2026-11-16: antes del 2026-11-17) ni de anotar su resultado. Hechos documentados que pesan en la ventana:

- `v1.1-observabilidad` se desplegó un domingo (2026-10-25) porque «el negocio cierra el sábado en la tarde y no hay uso hasta el lunes» (`registro-pendientes.md`, sección 3, decisión de la 01-06).
- `v1.2-capturas` y `v0.3-doble-envio` se desplegaron de madrugada del miércoles 2026-11-04 (reinicios efectivos a las 00:11:49 y 01:32:51).
- La vigilancia de siete días termina a más tardar el 2026-11-20 (vencimiento de la web app e informe C2) solo si `R` es hasta el 2026-11-13.
- Días de la semana calculados desde «domingo 2026-11-01» (`despliegue.md`, `evidencia-00-07`): el 2026-11-11 es miércoles y el 2026-11-14, sábado.
- **Nota 2026-11-16 (reprogramación):** el 2026-11-16 es lunes y el 2026-11-17 y el 2026-11-24 son martes (calculado con Python). La web app vence el 2026-12-13 (dicho por el desarrollador), así que el tope «`R` hasta el 2026-11-13» de este punto y de la opción A ya no rige. La decisión sigue siendo la A (noche, entre semana); cambia solo el día.

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. De madrugada, en una noche de la semana del 2026-11-11 posterior a la medición, con `R` hasta el 2026-11-13 (recomendada)** | Orden: renovar la web app (11-10) → medir la 00-07 (11-11, 01:32) → respaldo → pruebas → etiqueta → despliegue. Puede ser esa misma noche, tras anotar la medición, o una de las dos siguientes | Respeta la precondición y el precedente de la 01-09. Mismo horario de los dos últimos despliegues. El uso real del negocio empieza horas después, así que la semana de vigilancia ve tráfico desde el día 1 (inferido). Termina el 2026-11-20 o antes | Nadie del negocio ve un fallo hasta la mañana (inferido). Concentra en pocos días la renovación, la medición, el respaldo, las pruebas y el despliegue. `PENDIENTE_CLIENTE`: no hay medición de horas de uso entre semana |
| **B. Fin de semana: sábado en la tarde a lunes, desde el 2026-11-14** | Mismo orden, con la ventana del precedente de la 01-06 | Sin uso durante la recarga ni formularios abiertos al reiniciar (menos avisos que dar) | El primer uso real llega el lunes: de los siete días, dos casi no tienen tráfico (inferido). `R` cae el 2026-11-14 o después, así que la semana termina el 2026-11-21 o después: pasa el vencimiento y el informe C2 del 2026-11-20 |
| **C. Antes de la medición** | Desplegar apenas esté lista | Cierra antes AUD-04-001 en producción | La parte D de la 00-07 dejaría de medir solo el botón (ver arriba). **Contradice la precondición dicha por el desarrollador.** No se recomienda |
| **D. Después del 2026-11-20** | Esperar el informe C2 y la renovación siguiente | Sin solapes con otras fechas | AUD-04-001 (Alta) sigue abierto más de dos semanas con el servidor sin protección, y la vigilancia queda atada a otra renovación |

- **Etiqueta (sugerida):** `v3.1-integridad`. Formato `v<fase>.<correlativo>-<propósito>` de `despliegue.md`, sección 1: fase 3, correlativo 1 (cada fase parte en 1; los documentos no registran ninguna etiqueta de la fase 2). Mensaje: `Iteraciones 03-01 a 03-04 · desplegada el AAAA-MM-DD` con la fecha de Chile del día. Anotada, publicada con `git push origin`, y comprobada con `git ls-remote --tags origin v3.1-integridad`.
- **Destino de retroceso:** `v0.3-doble-envio` (la última desplegada; `despliegue.md`, sección 1: «el destino es la etiqueta desplegada antes»).
- **No se crea ninguna etiqueta en esta redacción** (`AGENTS.md`, sección 6).
- **Resuelta el 2026-11-06:** etiqueta `v3.1-integridad`, de 20:00 a 23:00 (hora de Chile) de un día entre el 2026-11-11 y el 2026-11-13. Con esa hora, desde las 21:00 la fecha UTC ya es la del día siguiente, y con el día 7 a la misma hora `R` el 11-13 deja la última lectura el 11-20 por la noche (el día del vencimiento de la web app y del informe C2); el 11-11 o el 11-12 dejan margen (sugerencia, sin decidir). **Ronda final (2026-11-06): jueves 2026-11-12, de 20:00 a 23:00; día 7, jueves 2026-11-19 por la noche**, un día antes del vencimiento de la web app y del informe C2. **Reprogramada el 2026-11-16 (desarrollador): martes 2026-11-17, de 20:00 a 23:00; día 7: martes 2026-11-24 por la noche** (ver «Reprogramación del 2026-11-16»). **Ejecutado el lunes 2026-11-16 (dicho por el desarrollador el 2026-11-17):** `R` = 23:48:12, fuera de la ventana por decisión del desarrollador; día 7 desde el lunes 2026-11-23 a las 23:48:12, o el martes 2026-11-24. Ver «Ejecución del día 0 (2026-11-16)».

### Decisión 4 · Aviso al cliente

Lo que cambia para quien usa la aplicación: (a) los formularios abiertos al desplegar no traen token y se guardan al segundo intento, sin perder lo escrito; (b) los botones de guardar se bloquean con «Guardando…»; (c) los errores se ven arriba, en rojo; (d) la recarga deja unos 10 s de respuestas 502 (AUD-04-002); (e) el navegador puede conservar el `index.js` antiguo (no hay nombre con hash: `settings.py:190-191`, almacenamiento de estáticos por defecto) y conviene recargar con Ctrl+F5 (inferido, no probado).

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Aviso breve antes y recordatorio después (recomendada)** | El desarrollador manda el texto de abajo antes de la hora elegida y, tras la recarga, pide cerrar y reabrir la aplicación con Ctrl+F5 | Quien usa la aplicación (hoy el dueño, único usuario según `pruebas.md`, sección 9) sabe qué esperar; evita un reporte de «no se guardó» o de «el botón no responde» | El texto es nuevo y debe aprobarse. Depende del canal que use el desarrollador, que no consta en los documentos |
| **B. Sin aviso previo; solo explicar si pregunta** | Nada antes | Sin trabajo | El primer intento de guardar con un formulario abierto vuelve con «Este formulario venció…» y puede leerse como un error nuevo del sistema |
| **C. Aviso solo en pantalla** (un mensaje fijo en la aplicación) | Mensaje temporal | Lo ve quien entra | Es código y plantilla nuevos: **fuera de alcance** (esta iteración no toca código) |

**Texto aprobado para la opción A** (aprobado por el desarrollador el 2026-11-06, con una frase agregada por él: la de la imagen de referencia, porque el texto decía que no se pierde nada y la imagen sí se pierde; voz de `DESIGN.md`, sección 10):

> Hoy a las HH:MM vamos a actualizar el sistema. Puede dejar de responder unos segundos mientras se reinicia. Si tenías un pedido, una cotización o un pago abierto antes de eso, la primera vez que lo guardes va a salir el aviso «Este formulario venció y no se guardó»: no perdiste lo que escribiste, revisa los datos y vuelve a guardar. Si habías elegido una imagen de referencia, vuelve a elegirla: el navegador no la conserva. Después de la actualización, cierra la pestaña y abre la aplicación de nuevo (o pulsa Ctrl+F5). Notarás que los botones de guardar dicen «Guardando…» y se bloquean un momento: es para que un doble clic no cree el pedido dos veces. Si algo no funciona, cuéntanos en qué pantalla estabas y a qué hora.

### Decisión 5 · Vigilancia de una semana

La vigilancia la hace el desarrollador (los agentes no tocan PythonAnywhere). Cada lectura consume CPU de los 100 s diarios de la consola; los comandos de `despliegue.md`, 3.7 y 3.9, son cortos. `R` es la hora del reinicio efectivo (`Starting uWSGI`, hora de Chile), la oficial.

**5a · Qué se lee, cuándo y cuándo se cierra**

| Opción | Qué hace | Ventajas | Riesgos |
| :----- | :------- | :------- | :------ |
| **A. Siete días corridos desde `R`, cuatro lecturas y medición de duplicados con `access.log` y conteo de pedidos (recomendada)** | Lecturas: **día 0** (a la hora de `R`, una hora después y al cierre de la jornada), **día 1**, **día 3** y **día 7** (misma hora que `R`). Cada lectura: (1) `nivel=ERROR` de `server.log` desde `R`, por ruta, sin copiar el texto; (2) respuestas 5xx y conteo de `POST` de las rutas de creación por código de estado en `access.log`; (3) tiempo de respuesta de `GET /pedidos/nuevo/`, `/cotizaciones/nueva/` y `/pagos/ingresar/` (+3 consultas aceptadas); (4) líneas `nivel=INFO` «Envío sin token válido» (esperadas el día 0 por los formularios abiertos; después, pocas). **Duplicados:** conteo de `POST /pedidos/nuevo/` con 302 contra pedidos nuevos en la base de ese día (conteo de solo lectura del desarrollador) | Cumple el criterio de la definición (una semana, `server.log`). La comparación 302/pedidos nuevos sí distingue un envío repetido rechazado de uno guardado, que `access.log` solo no distingue | Exige una consulta de solo lectura a la base de producción hecha por el desarrollador y un guion nuevo (`PENDIENTE_DESARROLLADOR`, se escribe al ejecutar; no existe hoy). **Actualización 2026-11-06:** el guion ya está escrito en la evidencia (C6 y D4), probado solo con datos sintéticos |
| **B. Lo mismo, pero medir duplicados solo con el guion de la 00-07 (`segundos_repetidos`)** | Reutiliza la parte D de la 00-07 | Ya existe y está probado en el formato de `access.log` | Después de la 03-05 un doble envío rechazado también responde 302 en el mismo segundo: `segundos_repetidos > 0` no probaría un duplicado y `= 0` no probaría nada más que la ausencia de dobles envíos (ver «Avisos») |
| **C. Tres días** | Acorta la vigilancia | Menos trabajo | Contradice la definición de la épica («una semana») y el plan: habría que cambiarlos con una nota fechada |

**Criterio de cierre propuesto (para A):** (i) siete días desde `R` sin `nivel=ERROR` nuevo de `django.request` ni de `pedidos.views` en las rutas modificadas, descontando las líneas ya clasificadas (`registrador=root`, `OSError: write error`, AUD-04-004) y los `ERROR` de ítem fallido que se expliquen (ver decisión 6); (ii) ningún 5xx en las rutas de creación y edición; (iii) ningún pedido, cotización ni pago duplicado en la ventana; (iv) tiempos de respuesta de los tres formularios sin salir de la banda que ya se midió en producción (de 0,03 a 1,13 s fuera de las recargas, Auditoría 04) (inferido: la banda es de todo el sitio, no de estas rutas); (v) la línea `INFO` verificada (5b). **Resuelto el 2026-11-06 (ronda final):** (iv) pasa a ser «ninguna respuesta de `GET` o `POST` de crear pedido, crear cotización e ingresar pago pasa de 2 s, sin contar la recarga»; si `access.log` no trae `response-time=`, se anota y el criterio queda en los 5xx. La banda de 0,03 a 1,13 s deja de ser el criterio. En (i), los `ERROR` de ítem fallido de causa explicada no cuentan, y 3 o más en 24 h sin causa explicada no se cierran hasta reproducirlos en la réplica; en (ii), un 5xx suelto se investiga y, si queda explicado, es una excepción explicada.

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
| **A. Regla escrita antes del despliegue (recomendada)** | (1) **Datos incorrectos o perdidos** (montos, pedidos, pagos): detener, avisar y evaluar el caso 3 (restaurar). (2) **5xx repetido** o formulario que no guarda en una vista modificada: retroceder (caso 1). (3) **Un `ERROR` aislado** de ítem fallido con aviso en pantalla: no retroceder; sacar la traza (`despliegue.md`, 3.9), reproducir en la réplica y registrar en la evidencia solo el tipo y la hora. (4) **Líneas `INFO` de rechazo:** sin acción. Todo `ERROR` nuevo se clasifica con la tabla de 3.9 antes de decidir | Evita retroceder por un `ERROR` esperado y evita no retroceder ante uno grave. La réplica queda disponible para reproducir (decisión 7) | **Resuelto el 2026-11-06 (ronda final):** «5xx repetido» = 2 o más en 24 h en la misma ruta, sin contar la recarga de unos 10 s ni las líneas ya clasificadas (`OSError`); un 5xx suelto es aislado: se investiga y no se retrocede. `ERROR` de ítem fallido: 3 o más en 24 h sin causa explicada se reproducen en la réplica antes de decidir; los de causa explicada no cuentan |
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
| **C. Desplegar con `OK` limpio, retirando las marcas de las 9** | — | — | **No.** Son defectos reales declarados (pendientes en la 04-01, 04-06, 06-01 y 07-02, antes 06-05); quitar la marca los ocultaría y haría fallar el conjunto |

- **Estas 9 no viajan corregidas:** R6a, R6b, R6c, R7 y R19 (04-01), R14 (04-06), R8 y R9 (06-01), R15 (07-02, antes 06-05; ver «Avisos»).

## Tareas (en este orden, una vez tomadas las decisiones)

Las hace el desarrollador salvo donde se dice. Ningún agente toca PythonAnywhere, crea etiquetas ni hace `push`.

**Avance (2026-11-17):** las tareas 0 a 6 y la verificación de la línea `INFO` de la 7 se hicieron el 2026-11-16 (dicho por el desarrollador). Quedan la vigilancia hasta el día 7 (7, parte D), el cierre documental (9) y la operación (10).

0. **Precondiciones:** 00-07 medida (parte D, ~~2026-11-11, hacia las 01:32~~ antes del 2026-11-17, con el guion ajustado el 2026-11-16) y su resultado anotado; web app con vencimiento conocido (2026-12-13, dicho por el desarrollador; ~~renovada el 2026-11-10~~); producción confirmada en `v0.3-doble-envio` por el desarrollador; `git status --short` vacío y `main` igual a `origin/main`.
1. **Evidencia lista** (agente): [evidencia-03-05](evidencia-03-05.md), creada el 2026-11-06 al resolverse las decisiones, con comandos exactos y casillas (A, PC; B, servidor; C, día 0; D, día 7 y cierre; E, retroceso; F, limpieza de la réplica). La rellena el desarrollador al ejecutar.
2. **Lista de comprobación previa** (`despliegue.md`, sección 2) en el PC: pruebas (decisión 8), `check --deploy`, `makemigrations --check --dry-run`, `showmigrations pedidos` (ninguna migración nueva), respaldo (decisión 2), «Estilos compilados: no aplica», etiqueta.
3. **Etiqueta** (decisiones 1 y 3): `git diff --stat <hash>..main -- . ":(exclude)_planificacion" ":(exclude)docs"` vacío, `git tag -a`, `git push origin`, `git ls-remote --tags origin`.
4. **Aviso al cliente** (decisión 4) el ~~2026-11-12~~ ~~2026-11-17~~ 2026-11-16, antes de `R` (el aviso decía 22:30 y `R` fue 23:48:12), con el texto aprobado.
5. **Despliegue** (`despliegue.md`, 3.1 a 3.6): ubicarse, `git fetch origin --tags`, `git checkout <etiqueta>`, **sin dependencias** (3.3: `requirements.txt` no cambió), **sin migraciones** (3.4: `No planned migration operations.`), **`collectstatic --noinput`** (3.5: cambió `index.js`), **Reload** y anotar la hora del reinicio efectivo `R`.
6. **Verificación inmediata, solo lectura** (3.7): ventana privada, acceso, panel, listado y detalle de pedidos; además, sin crear nada: que `/pedidos/nuevo/`, `/cotizaciones/nueva/` y `/pagos/ingresar/` carguen y que el código fuente de cada una traiga el campo `token_envio`. Registro de errores desde `R`.
7. **Verificar la línea `INFO`** (decisión 5b; parte C de la evidencia) y **vigilar** (decisión 5): lecturas **solo los días 0 y 7** (~~2026-11-12 y 2026-11-19~~ ~~2026-11-17 y 2026-11-24~~ día 0: 2026-11-16, hecho; día 7: desde el 2026-11-23 a las 23:48:12 o el 2026-11-24; partes C y D de la evidencia). Una lectura extra a demanda queda como sugerencia, sin decidir (ver «Riesgos»).
8. **Si aparece un `ERROR` nuevo:** clasificar (3.9) y aplicar la regla de la decisión 6.
9. **Cierre documental** (agente, con la evidencia que responda el desarrollador): `bitacora-03-05-produccion.md`; fila en `despliegue.md`, sección 5 (registro de despliegues); notas fechadas en AUD-04-001 y en los hallazgos que dicen «se despliega con la 03-05» (sin borrar lo anterior); el texto de `despliegue.md`, 3.9, según el resultado de 5b; `registro-pendientes.md`; estado de la 03-05 y de la Épica 03 (nota fechada en `definicion-epica-03.md`).
10. **Operación** (decisión 7, opción A) como último paso, después de cerrar la vigilancia: traslado del disco de Docker, refresco de la réplica, conteo de pedidos sin ítems y comprobación de cifrado (parte F de la evidencia).

## Criterios de aceptación

- [x] Las decisiones 1 a 8 están registradas antes de ejecutar (2026-11-06; ver «Decisiones del desarrollador»).
- [x] Pruebas, `check --deploy` y `makemigrations --check --dry-run` del día del despliegue anotados, con `OK (expected failures=9)`, 267 pruebas y `No changes detected` (o la desviación explicada).
- [x] Respaldo previo según la decisión 2, verificado (código 0) y anotado en `respaldo.md`, sección 6.
- [x] Etiqueta anotada publicada y comprobada con `ls-remote`; destino de retroceso anotado.
- [x] Despliegue hecho por los pasos de `despliegue.md`, con `collectstatic`, sin migraciones; hora `R` anotada (2026-11-16 23:48:12; la salida de `migrate --plan` no se informó).
- [x] Verificación inmediata sin errores desde `R`; los tres formularios traen `token_envio`.
- [x] La línea `INFO` verificada, o su estado explicado (decisión 5b).
- [ ] Siete días desde `R` con el criterio de cierre (parte D5 de la evidencia) cumplido, o cada excepción explicada. Lecturas: días 0 y 7 (~~2026-11-12 y 2026-11-19~~ ~~2026-11-17 y 2026-11-24~~ día 0: 2026-11-16, hecho; día 7: desde el 2026-11-23 a las 23:48:12 o el 2026-11-24). **Sin marcar: falta el día 7.**
- [ ] `access.log` y el conteo de pedidos sin duplicados por envío repetido (AUD-04-001, criterio de término).
- [ ] Fila en el registro de despliegues de `despliegue.md`; notas fechadas en los hallazgos; bitácora de producción. **Sin marcar:** hechas la fila (2026-11-17) y la bitácora de producción del día 0; faltan las notas fechadas en los hallazgos, que se dejan al cerrar la vigilancia.
- [ ] AUD-05-002 y la limpieza de la réplica resueltas o reprogramadas por escrito (decisión 7).
- [ ] Los `PENDIENTE_CLIENTE` abiertos siguen sin cambios de comportamiento: AUD-02-014, pedido de $0 como pagado y sobrepago.

## Fechas de operación

### Vigentes desde el 2026-11-17 (tras la ejecución del día 0)

| Fecha | Qué | Fuente | Estado |
| :---- | :-- | :----- | :----- |
| Lunes 2026-11-16, por la noche | Medición de la 00-07 (hacia las 23:13), pruebas y comprobaciones, respaldo (23:34:18), etiqueta, servidor antes (23:43:18), `R` (23:48:12) y día 0 (C1 a C6, hasta pasadas las 23:58) | Dicho por el desarrollador, 2026-11-17 | Hecho |
| Martes 2026-11-17, de día | El cliente hace Ctrl+F5 y empieza el uso real. Lectura a demanda como sugerencia, sin decidir (C5 y C6 de la evidencia) | Dicho por el desarrollador; decisión 5 | Pendiente |
| Del miércoles 2026-11-18 al jueves 2026-11-19 | Sin lecturas programadas (decisión 5) | Decisión 5 | Decidido |
| Viernes 2026-11-20 | Informe de desconexiones a 28 días (parte C2 de [evidencia-00-06](../epica-00-blindaje/evidencia-00-06.md)), **a mitad de la vigilancia**. La recarga de `R` (2026-11-16 23:48:12 Chile = 2026-11-17 02:48:12 UTC, con sus unos 10 s de 502, AUD-04-002) y el `OSError: write error` de las 23:55:10 (AUD-04-004) figuran en sus conteos: sepáralos usando `R` | `registro-pendientes.md`, sección 3 | Documentado |
| Del sábado 2026-11-21 al lunes 2026-11-23 (antes de las 23:48:12) | Sin lecturas programadas | Decisión 5 | Decidido |
| **Lunes 2026-11-23 desde las 23:48:12** (02:48:12 UTC del 11-24), o **martes 2026-11-24** en adelante | Lectura del día 7 y cierre de la vigilancia | Cálculo: `R` + 7 días | Decidido por la fecha del despliegue |
| Después de la lectura del día 7 | Respuesta del desarrollador en la evidencia; cierre documental del agente; parte F (réplica y AUD-05-002) | — | Pendiente |
| Domingo 2026-12-13 | La web app queda renovada hasta esa fecha (dicho por el desarrollador, 2026-11-17). Fecha de la renovación y fecha para volver a renovar: `PENDIENTE_DESARROLLADOR` | Dicho; no visto en el panel | La vigilancia termina antes |

### Reprogramadas el 2026-11-16 (superadas el 2026-11-17 por la ejecución del día 0; se conservan como registro)

| Fecha | Qué | Fuente | Estado |
| :---- | :-- | :----- | :----- |
| Lunes 2026-11-16 (hoy) | Reprogramación documentada. El desarrollador confirma en el servidor que producción sigue en `v0.3-doble-envio` (`git status` limpio, `git describe --tags --always` y `Starting uWSGI` desde el 2026-11-04 01:32:51) | Dicho por el desarrollador, 2026-11-16 | `PENDIENTE_DESARROLLADOR`: por confirmar |
| Lunes 2026-11-16 por la noche, o martes 2026-11-17 durante el día y antes de empezar la 03-05 (A1 de la evidencia) | Medición de `access.log` de la 00-07 (parte D de [evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md), guion ajustado el 2026-11-16: 12 o 13 días desde el reinicio) y, con ella, cierre de la 00-07 | Dicho por el desarrollador: no se hizo el 2026-11-11; sigue siendo precondición | Pendiente. No medible desde aquí |
| Martes 2026-11-17, por la tarde | Pruebas, `check --deploy` y `makemigrations` (partes A1); etiqueta `v3.1-integridad` (A3); aviso al cliente con la hora real, antes de las 20:00 (A4: el texto dice «Hoy») | [evidencia-03-05](evidencia-03-05.md) | Pendiente |
| Martes 2026-11-17, poco antes de las 20:00 | Respaldo nuevo, verificado (A2). Puede contar también como el semanal si el de hacia el 2026-11-10 u 11 no se hizo (decisión 2-A) | Decisión 2 | Pendiente |
| Martes 2026-11-17, de 20:00 a 23:00 (hora de Chile) | Despliegue de la 03-05 (`R`) y lectura del día 0. En UTC, `R` cae entre las 23:00 del 11-17 y las 02:00 del 11-18 | Decisión del desarrollador, 2026-11-16 | Decidido |
| Del miércoles 2026-11-18 al lunes 2026-11-23 | Sin lecturas programadas (decisión 5); lectura a demanda solo como sugerencia (primera mañana, miércoles 11-18, o ante un reporte) | Decisión 5 | Decidido |
| Viernes 2026-11-20 | Informe de desconexiones a 28 días (parte C2 de [evidencia-00-06](../epica-00-blindaje/evidencia-00-06.md)), **a mitad de la vigilancia**. La recarga del 11-17 figura en sus conteos: sepárala usando `R`. Sugerencia, sin decidir: una lectura a demanda de la 03-05 en la misma sesión | `registro-pendientes.md`, sección 3 | Documentado |
| Martes 2026-11-24, por la noche (siete días después de `R` o más tarde, de 20:00 a 23:00 de Chile; de 23:00 UTC del 11-24 a 02:00 UTC del 11-25) | Lectura del día 7 y cierre de la vigilancia | Cálculo: `R` + 7 días | Decidido por la fecha del despliegue |
| Martes 2026-11-24 por la noche o miércoles 2026-11-25 | Respuesta del desarrollador en la evidencia; cierre documental del agente | — | Pendiente |
| Domingo 2026-12-13 | Vence la web app (dicho por el desarrollador el 2026-11-16; reemplaza el 2026-11-20 de los documentos). Fecha para renovarla: `PENDIENTE_DESARROLLADOR` | Dicho; no visto en el panel | La vigilancia termina 19 días antes |

### Anteriores (2026-11-06, superadas el 2026-11-16; se conservan como registro)

| Fecha | Qué | Fuente | Estado |
| :---- | :-- | :----- | :----- |
| 2026-11-10 | Renovar la web app de PythonAnywhere (vence el 2026-11-20) | `registro-pendientes.md` (cabecera y sección 3, AUD-01-019) | Documentado. No verificado si ya se hizo ni cuánto extiende la renovación |
| 2026-11-10 u 11 | Próximo respaldo semanal | `registro-pendientes.md` (cabecera) | Documentado. Es distinto del de la decisión 2, que se hace el 2026-11-12 |
| 2026-11-11, hacia las 01:32 (hora de Chile; 04:32 UTC) | Medición de `access.log` de la 00-07 (parte D) y, con ella, cierre de la 00-07 | [evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md), `registro-pendientes.md` | Documentado en tres lugares; coinciden con lo dicho por el desarrollador. No medible desde aquí |
| Jueves 2026-11-12 (pruebas, etiqueta y aviso por la tarde; respaldo poco antes de las 20:00), de 20:00 a 23:00 (hora de Chile) | Despliegue de la 03-05 (`R`) y lectura del día 0. En UTC, `R` cae entre las 23:00 del 11-12 y las 02:00 del 11-13 | Decisión del desarrollador, 2026-11-06 (ronda final); las horas de la tarde son una sugerencia del calendario de la evidencia | Decidido |
| Jueves 2026-11-19, por la noche (siete días después de `R` o más tarde, de 20:00 a 23:00 de Chile; de 23:00 UTC del 11-19 a 02:00 UTC del 11-20) | Lectura del día 7 y cierre de la vigilancia. Un día antes del vencimiento de la web app y del informe C2 | Cálculo: `R` + 7 días | Decidido por la fecha del despliegue |
| Del viernes 2026-11-13 al miércoles 2026-11-18 | Sin lecturas programadas (decisión 5); lectura a demanda solo como sugerencia | Decisión 5 | Decidido |
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
| La recarga deja unos 10 s de 502 y un POST en ese lapso se pierde (AUD-04-002) | Ventana nocturna de 20:00 a 23:00, de menor uso según el desarrollador (decisión 3), y aviso (decisión 4) |
| Cuatro iteraciones juntas: si falla, se retrocede todo | Retroceso del caso 1 (sin migraciones), regla de la decisión 6, lista de comprobación completa |
| Un `ERROR` esperado (ítem fallido) se confunde con uno nuevo | Tabla de `despliegue.md`, 3.9, y decisión 6 |
| Con la 03-05 desplegada, `access.log` ya no distingue un duplicado rechazado de uno guardado | Decisión 5a: comparar con el conteo de pedidos nuevos |
| El token suma entradas a la sesión (hasta 20 por sesión) y suma consultas | Costo aceptado el 2026-11-04. No se encontró ninguna purga de sesiones en el repositorio (búsqueda de `clearsessions`, sin resultados): la sesión dura 14 días y el disco es escaso (inferido: el tamaño es pequeño; no medido) |
| El navegador conserva el `index.js` anterior | Aviso con Ctrl+F5 (decisión 4); no hay nombre con hash en los estáticos |
| ~~La 03-05 se atrasa y la semana de vigilancia cae sobre el 2026-11-20~~ (superado el 2026-11-16: la web app vence el 2026-12-13) | ~~Con `R` el 2026-11-12, el día 7 es el 11-19: queda un día de margen. Si algo lo atrasa un día, `R` el 11-13 deja la lectura final el 11-20 (el mismo día del vencimiento); más tarde pasa de esa fecha. Renovar la web app el 2026-11-10~~ |
| La recarga del 2026-11-16 (`R` 23:48:12; ~~2026-11-17~~ en la reprogramación) y sus 502 caen dentro del informe C2 de la 00-06 (28 días), que se hace el 2026-11-20, a mitad de la vigilancia | Anotar `R` (hora oficial, `Starting uWSGI`) y separar esa recarga en los conteos de C2: excluirla o marcarla aparte, con sus unos 10 s de 502 (AUD-04-002). Lo hace el desarrollador al medir C2 |
| ~~La medición de la 00-07 se vuelve a atrasar y arrastra el despliegue~~ (superado el 2026-11-17: se midió el 2026-11-16 antes del despliegue y cumple) | Es precondición: sin su resultado anotado, no se despliega el 2026-11-17. Se reprograma por escrito; la web app vence el 2026-12-13, así que hay margen |
| ~~Producción no está en `v0.3-doble-envio` (no verificado desde aquí)~~ (superado el 2026-11-17: el desarrollador confirmó el commit `5dc82a8` antes de tocar nada) | El desarrollador lo confirma antes (`git describe --tags --always` y `Starting uWSGI`); B1 de la evidencia exige `v0.3-doble-envio` y `5dc82a8` y manda detenerse si no coincide |
| El cliente ya recibió un aviso para el jueves 2026-11-12 (no consta) | Si lo recibió, decirle que la actualización cambió al ~~martes 2026-11-17~~ lunes 2026-11-16 (el aviso decía 22:30 y `R` fue 23:48:12); el texto del aviso final no cambia |
| El aviso decía 22:30 y `R` fue 23:48:12 (1 h 18 min después) | Desviación anotada en la evidencia; no cambia el criterio de cierre. Canal, día y hora del envío: `PENDIENTE_DESARROLLADOR` |
| El navegador del cliente conserva el `index.js` anterior hasta su Ctrl+F5 del 2026-11-17 (la prueba de C2 fue en ventana privada y no mide el caché) | El cliente hará Ctrl+F5 el 2026-11-17 de día (dicho por el desarrollador); lectura a demanda sugerida tras el primer uso real (C7), sin decidir |
| El día 0 no tuvo tráfico en `/pedidos/nuevo/` (C6 en 0): la línea base de duplicados queda vacía | El criterio (iii) solo se pone a prueba con el uso real: la lectura del día 7 (D4) y, si se hace, una lectura a demanda |
| `pago_form.html`: «$ is not defined» (AUD-05-009) | No es una regresión (idéntico en `v0.3-doble-envio`, verificado por el desarrollador); va a la Épica 08 y no cambia el criterio de la 03-05. Atento solo si el cliente reporta que el selector de pedido de `/pagos/ingresar/` no funciona (hipótesis: `index.js:78-79` inicializa `.select2`; no probado) |
| Retroceder deja sin token ni bloqueo de botón en las pantallas nuevas | Regla de la decisión 6: retroceder solo ante 5xx repetido o datos incorrectos |
| La limpieza de la réplica borra el lugar donde reproducir errores | Decisión 7-A: después de la vigilancia |
| **Con lecturas solo los días 0 y 7, un problema de los días 1 a 6 solo se vería si el cliente lo reporta**, y la lectura del día 0 ocurre de noche, antes del primer uso real | Riesgo aceptado por el desarrollador (decisión 5, 2026-11-06). Sugerencia, sin decidir: una lectura extra a demanda (la primera mañana tras `R` o ante un reporte de «no se guardó»), con los comandos de C5 y C6 de la evidencia. La regla de retroceso de «2 o más en 24 h» se evalúa al leer: un problema del día 3 se resolvería el día 7 o cuando el cliente lo reporte |
| Los archivos rotados de `server.log` y `access.log` podrían no cubrir los siete días al leer solo el día 7 (no verificado) | Las lecturas incluyen los archivos rotados (`despliegue.md`, 3.6); si falta alguno, se anota en la evidencia |
| El `POST` de crear pedido con imagen de referencia podría pasar de 2 s sin ser un defecto (subir la imagen cuenta en el tiempo); no hay medición previa de ese `POST` | El umbral de 2 s es del desarrollador (ronda final). Un exceso se mira con su causa (ruta, método y hora) antes de concluir |
| `response-time=` consta solo como nombre de campo (`definicion-epica-13.md`) y por las mediciones de AUD-04-005; el formato no está documentado | Si `access.log` no lo trae, se anota y el criterio de tiempos queda en los 5xx (decisión del 2026-11-06) |
| Un formulario de pedido abierto al reiniciar vuelve sin la imagen de referencia al guardarse (el navegador no la conserva; dicho por el desarrollador) | Frase agregada al aviso (decisión 4, ronda final) |

## Avisos (contradicciones o tensiones con RDA, decisiones o documentos; sin corregir)

1. **Criterio de término contra `access.log`.** La definición pide que «`access.log` no muestre pedidos duplicados por envío repetido». Con el token, el segundo POST responde 302 igual que el primero y `access.log` no registra el destino (inferido del formato, que lleva el código de estado pero no la redirección). El guion de la 00-07 queda como señal, no como prueba. Se propone medir con el conteo de pedidos (decisión 5a). **Resuelto el 2026-11-06 (decisión 5):** el desarrollador aceptó comparar los `POST` 302 contra los pedidos nuevos de la base (partes C6 y D4 de la evidencia); `access.log` solo no decide el punto.
2. **Plan 3.5 contra RDA-013.** El plan pide vigilar «mediante las tablas de registro de la Fase 1»; RDA-013 descartó la tabla de errores y el diagnóstico va en `server.log`. La definición de la épica ya lo dice así. `plan-de-trabajo.md` no se edita. **Resuelto el 2026-11-06:** la vigilancia usa `server.log` (RDA-013, aceptada); la definición de la épica ya lo dice así y el plan no se toca. Donde el plan 3.5 dice «tablas de registro de la Fase 1», léase `server.log`.
3. **«Un despliegue, un propósito» (RDA-007) contra cuatro iteraciones.** `despliegue.md` lo permite para «una fase cerrada»; aun así, la 03-04 ya mezcló el contrato de error y el envío único (decisión 10 de la 03-04) y esta etiqueta suma la 03-01 a la 03-03. Se recomienda la etiqueta única; la opción B de la decisión 1 es la salida si no te parece. **Resuelto el 2026-11-06 (decisión 1):** una sola etiqueta, sin migraciones. **Aviso de RDA-007, anotado:** la etiqueta publica una fase cerrada con cuatro iteraciones y dos propósitos (contrato de error y envío único); `despliegue.md` lo permite («una fase cerrada») y un retroceso, si hace falta, vuelve todo junto (caso 1).
4. **Respaldo: las iteraciones dicen «lo decide el desarrollador en la 03-05»; los procedimientos ya lo piden.** `respaldo.md`, sección 5, y `despliegue.md`, punto 5 de la lista, piden respaldo antes del primer despliegue de una fase. La decisión 2 lo recomienda por eso. **Resuelto el 2026-11-06 (decisión 2):** respaldo nuevo el día del despliegue.
5. **AUD-05-002: «sin respaldo nuevo».** La decisión del 2026-11-04 evitaba generar un respaldo solo para refrescar la réplica. Si la decisión 2 es A, ese respaldo existirá y podría ser la fuente: cambia el texto de esa decisión. **Propuesta de ajuste, sin decidir (2026-11-06):** como la decisión 7 deja el refresco para después de la vigilancia, la fuente se elige entonces (parte F1 de la evidencia): el respaldo del despliegue, el semanal verificado más reciente o el del 2026-11-04. Cuando el desarrollador elija, hay que ajustar el texto de AUD-05-002 y el de la fila de Operación del registro («sin respaldo nuevo»); el agente solo dejó una nota fechada en ambos y no cambió su texto.
6. **La 03-02 describe un comportamiento que la 03-04 cambió.** [iteracion-03-02](iteracion-03-02-erradicacion-supresion-silenciosa.md), «Despliegue», dice que un ítem fallido al crear un pedido deja una línea de `django.request` y muestra la página 500; desde la decisión 3-B de la 03-04 devuelve el formulario (200) con una línea `ERROR` de `pedidos.views`. Vale lo de la 03-04 y `despliegue.md`, 3.9. `despliegue.md`, sección 0, también dice que «un error en cualquier vista deja una sola línea `django.request`»: sigue valiendo para excepciones no previstas. **Resuelto el 2026-11-06:** nota fechada en la sección «Despliegue» de la [iteración 03-02](iteracion-03-02-erradicacion-supresion-silenciosa.md); el texto original no se tocó.
7. **`R15`.** [iteracion-03-04](iteracion-03-04-contrato-de-error-hacia-el-usuario.md) dice que la corrigen «la 04-01, 04-06, 06-01 y 07-02»; `pruebas.md`, sección 7.1, dice 06-05. **Resuelto el 2026-11-06:** no hay contradicción, es la misma iteración con dos numeraciones: la tabla de equivalencias de RDA-014 (`decisiones.md`) hace la antigua 06-05 la **07-02**, y el registro (sección 3) lo repite. `pruebas.md` y el comentario de `test_regresiones.py` conservan «06-05» (el primero con «numeración anterior a RDA-014») por la regla de [bitacora-02-cierre-epica](../../99_bitacora/epica-02-red-seguridad/bitacora-02-cierre-epica.md): lo escrito antes de RDA-014 no se reescribe. Esta iteración usa «07-02 (antes 06-05)». El comentario del código no se tocó.
8. **Épica 03 sigue «Pendiente».** Cuatro de sus cinco iteraciones están Terminadas y el estado de la épica no cambia hasta cerrar la 03-05 (precedente de las notas de `definicion-epica-03.md`).
9. **El aviso de la decisión 4 es texto nuevo** para el usuario: no está entre los «Textos aprobados» de la 03-04 y necesita aprobación. **Resuelto el 2026-11-06 (ronda final):** el desarrollador aprobó el texto con una frase agregada sobre la imagen de referencia.
10. **El aviso dice «Hoy a las HH:MM» y la fecha cambió.** El texto aprobado no menciona ningún día: vale con la nueva fecha **si se envía el martes 2026-11-17 antes de la actualización**, porque «hoy» es el día del despliegue. Si se enviara antes, «Hoy» sería falso; habría que escribir el día, y eso es un cambio de una palabra sobre un texto aprobado que confirma el desarrollador. **Anotado el 2026-11-16, sin cambiar el texto.** **Nota 2026-11-17:** el despliegue fue el lunes 2026-11-16 y el aviso decía 22:30 mientras `R` fue 23:48:12 (desviación 3 de la evidencia); el día y la hora de envío no se informaron.

## No pude ver ni verificar

- **Producción:** qué etiqueta corre hoy, el contenido de `server.log` y `access.log`, la hora de uso del cliente, ~~si la renovación del 2026-11-10 se hizo y cuánto extiende~~ (2026-11-16: el desarrollador dice que la web app vence el 2026-12-13; no lo vi en el panel ni sé cuándo se renovó). Todo lo anterior viene de documentos.
- **Etiquetas:** `git tag` y `git tag -n` están fuera de lo que puedo ejecutar (`AGENTS.md`, sección 6). Las etiquetas existentes salen de `despliegue.md` y las evidencias: `v0.0-inicial`, `v0.1-higiene`, `v0.2-correcciones`, `v1.1-observabilidad`, `v1.2-capturas` y `v0.3-doble-envio`. No comprobé que `v3.1-integridad` esté libre.
- **Hora de poco uso:** sigue sin medirse; la ventana de 20:00 a 23:00 es decisión del desarrollador (2026-11-06) y ya no es `PENDIENTE_CLIENTE`. El canal para avisar tampoco consta.
- **Caché de `index.js`** en el navegador del cliente (inferido por la ausencia de nombre con hash).
- **Línea `INFO` en producción** (decisión 5b) y **retroceso con sesiones que traen `tokens_envio`** (inferido, no ensayado).
- **Costo de las +3 consultas en producción:** medido solo en la réplica.
- **`response-time=` en `access.log`:** consta solo como nombre de campo en `definicion-epica-13.md` y por las mediciones de AUD-04-005 (0,03 a 1,13 s; 5,6 a 9 s tras una recarga); no hay formato ni línea de ejemplo documentados. Si falta, el criterio de tiempos queda en los 5xx.
- **Pruebas, `check` y `makemigrations`:** no se ejecutaron en esta redacción; las cifras (267 pruebas, `expected failures=9`) salen de la bitácora del 2026-11-06.
- **Día 0 (2026-11-17):** todo lo de la ejecución del 2026-11-16 es dicho por el desarrollador; no vi ninguna salida. No se informaron: el resultado de `git status` y de los `diff` de A1 (filas 1, 2, 6 y 8), `describe` y `migrate --plan` del servidor, `check --deploy` antes y después, el recuento de `bloquearBoton`, el clic de Reload y el número de reinicios desde `R`, el mensaje de la etiqueta, la salida de D0 de la 00-07 (rotación de `access.log`) y el canal, día y hora del aviso. Tampoco sé si el semanal de hacia el 2026-11-10 u 11 se hizo.
- **Al reprogramar (2026-11-16):** no vi producción: que siga en `v0.3-doble-envio`, que la medición de la 00-07 no se hizo y que la web app vence el 2026-12-13 son datos dichos por el desarrollador. Lo único verificado es GitHub (sin etiqueta `v3.1-integridad` ni commits posteriores a `a1653dd`, dicho como verificado por el desarrollador) y el repositorio local (`HEAD` en `a1653dd`; sin diferencias de código desde `7e14398`). No sé si el cliente recibió un aviso para el 11-12, si se hizo el respaldo semanal del 11-10 u 11, ni cuántos días conserva la rotación de `access.log` (la parte D de la 00-07 lo muestra con D0). El guion ajustado de la 00-07 se probó solo con registros sintéticos.

## Decisiones del desarrollador

Resueltas el 2026-11-06 (dichas por el desarrollador; no verificadas por el agente). Detalle en [bitacora-03-05-decisiones](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-decisiones.md).

1. **Qué viaja: A.** 03-01 a 03-04 en una sola etiqueta, sin migraciones. Se anota el aviso de RDA-007 (una fase cerrada con cuatro iteraciones y dos propósitos; ver «Avisos», 3).
2. **Respaldo: A.** Nuevo el día del despliegue, verificado antes de recargar.
3. **Ventana y etiqueta: A, con otra hora.** Etiqueta `v3.1-integridad`, entre las 20:00 y las 23:00 (hora de Chile; el desarrollador dice que es el horario de menor uso), un día entre el 2026-11-11 (después de la medición de la 00-07) y el 2026-11-13. Reemplaza «de madrugada» de la opción A. Se quita el `PENDIENTE_CLIENTE` de las horas de uso. El día se fijó en la ronda final: ~~jueves 2026-11-12~~. **Nota del 2026-11-16 (decisión del desarrollador, dicha por él): nueva ventana el martes 2026-11-17, de 20:00 a 23:00 (hora de Chile), en lugar del jueves 2026-11-12; día 7: martes 2026-11-24 por la noche. El límite «hasta el 2026-11-13» ya no rige (venía del vencimiento del 2026-11-20; la web app vence el 2026-12-13). Las demás decisiones no cambian.** **Ejecutado el lunes 2026-11-16 (dicho por el desarrollador el 2026-11-17):** `R` = 23:48:12, fuera de la ventana por decisión del desarrollador; día 7 desde el lunes 2026-11-23 a las 23:48:12, o el martes 2026-11-24. Ver «Ejecución del día 0 (2026-11-16)».
4. **Aviso: A.** Aviso breve antes y Ctrl+F5 después, con el texto de arriba. **Aprobado en la ronda final (2026-11-06)**, con una frase agregada por el desarrollador. Dato de la lectura del código: solo los formularios que usan `data-bloquear-envio` dependen del `index.js` nuevo; «Nuevo pedido» conserva su propio script de la 00-07.
5. **Vigilancia: lecturas solo los días 0 y 7** (no la recomendada, que eran el día 0, el 1, el 3 y el 7). Siguen la verificación deliberada de la línea `INFO` el día 0 (5b-A) y la medición de duplicados con los `POST` 302 contra los pedidos nuevos de la base. **Riesgo anotado:** un problema de los días 1 a 6 solo se vería si el cliente lo reporta. **Sugerencia, sin decidir:** una lectura extra a demanda. El umbral de los tiempos de respuesta se fijó en la ronda final.
6. **Retroceso: A, con esta regla.** Datos incorrectos o perdidos: sí (detener y evaluar el caso 3). 5xx repetido o formulario que no guarda: sí (caso 1). Un `ERROR` aislado de ítem fallido: no. Las líneas `INFO`: sin acción. Los números de «repetido» y «aislado» y el tratamiento de varios `ERROR` de ítem fallido se fijaron en la ronda final.
7. **Limpieza de la réplica y AUD-05-002: A.** Último paso de la iteración, después de la vigilancia. La fuente del respaldo se elige entonces (propuesta de ajuste en «Avisos», 5). **Es la única decisión que falta** (parte F1 de la evidencia).
8. **Regresiones: A, con una ejecución.** Una ejecución de pruebas el día del despliegue, con `OK (expected failures=9)` y 267 pruebas, más `check --deploy` y `makemigrations --check --dry-run`.

**Ronda final (2026-11-06, dicha por el desarrollador):**

- **R1 · Aviso aprobado:** el texto propuesto más la frase «Si habías elegido una imagen de referencia, vuelve a elegirla: el navegador no la conserva.» (el texto decía que no se pierde nada, y la imagen sí se pierde). Se quita el `PENDIENTE_DESARROLLADOR` de la aprobación literal.
- **R2 · Día del despliegue:** ~~jueves 2026-11-12, de 20:00 a 23:00 (hora de Chile). Día 7: 2026-11-19 por la noche.~~ ~~**Reprogramado el 2026-11-16:** martes 2026-11-17, de 20:00 a 23:00 (hora de Chile). Día 7: martes 2026-11-24 por la noche.~~ **Ejecutado el 2026-11-16** (dicho por el desarrollador el 2026-11-17): despliegue el lunes 2026-11-16, `R` a las 23:48:12, fuera de las 20:00 a 23:00 por decisión del desarrollador. Día 7: desde el lunes 2026-11-23 a las 23:48:12, o el martes 2026-11-24.
- **R3 · Tiempos:** ninguna respuesta de `GET` o `POST` de crear pedido, crear cotización e ingresar pago pasa de 2 s, sin contar la recarga. Si `access.log` no trae `response-time=`, se anota y el criterio queda en los 5xx.
- **R4 · Retroceso:** 5xx repetido = 2 o más en 24 h en la misma ruta, sin contar la recarga de unos 10 s ni las líneas ya clasificadas (`OSError`); un 5xx suelto es aislado: se investiga y no se retrocede. `ERROR` de ítem fallido: 3 o más en 24 h sin causa explicada, se reproduce en la réplica antes de decidir; los de causa explicada no cuentan.

**Cómo se aplican (lectura del agente, a confirmar por el desarrollador):** (a) «sin contar la recarga» se opera como los primeros 60 s después de `R` o de cualquier otro reinicio que liste D2 (el arranque en frío midió de 5,6 a 9 s, AUD-04-005); (b) la regla de 5xx se aplica a las rutas de las vistas modificadas, como decía la regla del mismo día; (c) con lecturas solo los días 0 y 7, las ventanas de 24 h se evalúan al leer; (d) `response-time=` está documentado solo como nombre de campo (ver «No pude ver»), y se supone en segundos.

## Datos requeridos del cliente

- ~~**`PENDIENTE_CLIENTE`:** en qué horas de entre semana la aplicación se usa menos, para elegir la ventana del despliegue (decisión 3). Solo consta que el negocio cierra el sábado en la tarde y no hay uso hasta el lunes; no hay medición de horas.~~ **Resuelto el 2026-11-06:** el desarrollador fija la ventana de 20:00 a 23:00 (hora de Chile) como la de menor uso, y el `PENDIENTE_CLIENTE` se quita. No hay medición de horas de uso: la ventana es dicha por el desarrollador.
- **Siguen abiertos, sin cambiar de comportamiento aquí:** valor de una cotización neto o con IVA (AUD-02-014), pedido de $0 como pagado y sobrepago (`registro-pendientes.md`, sección 2).
