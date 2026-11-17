# Bitácora · Revisión final de la Épica 04 (documental)

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Sonnet 5.5)
- **Alcance:** revisión de las diez iteraciones (04-01 a 04-10), la definición, el registro, la auditoría, `decisiones.md`, `AGENTS.md` y las bitácoras de la épica. **Solo documentos:** sin código, pruebas, `manage.py`, consultas a la base ni acceso a producción.
- **Estado de la épica tras esta revisión:** **Pendiente (redactada completa, sin ejecutar)**. Ninguna iteración se ha ejecutado ni desplegado.
- **Actualizada el 2026-11-17** con las decisiones posteriores del desarrollador (orden con la 04-10 tras la 04-01; W005 y W021 aceptadas; excepción a la sección 11; ejecución local en espera): ver [bitacora-04-cierre-redaccion](bitacora-04-cierre-redaccion.md).

## Cómo se lee esta bitácora

| Marca | Significa |
| :---- | :-------- |
| **[V]** | Verificado en el repo (o en el código de Django 6.0.1 de `.venv`) el 2026-11-17, con archivo y línea. |
| **[D]** | Dicho por el desarrollador; el agente no lo comprobó. |
| **[I]** | Inferido de leer el código o la documentación; se dice cómo se confirma. |
| **[NV]** | No verificado: solo se ve en producción (PythonAnywhere) o en un navegador real. |

Fechas de despliegue: **no hay ninguna** [D]. Nada se despliega antes de cerrar la vigilancia de la 03-05 (lectura del día 7 desde el **lunes 2026-11-23 a las 23:48:12**, hora de Chile) [D].

## 1. Las diez iteraciones

Todas están «Pendiente (redactada, decisiones resueltas)», con el estado de sus decisiones en [bitacora-04-01-cierre](bitacora-04-01-cierre.md) y las siguientes. Las etiquetas distintas de la 04-01 **no están fijadas** (`PENDIENTE_DESARROLLADOR`); la sección 2 trae **propuestas**.

| It. | Qué cambia | Tipo de cambio | Migración | Etiqueta | Regresiones a verde | Consultas previas (`AGENTS.md`, sección 6) | Respaldo previo |
| :-- | :--------- | :------------- | :-------- | :------- | :------------------ | :------------------------------------------ | :-------------- |
| **04-01** | Cambiar estado, duplicar (con autor) y respaldo solo por POST; `pago_confirm_delete.html`; el modal envía el formulario; sin recarga a los 2 s | Código (`views.py`, plantillas, `index.js`, `ayudas.py`) | No | **`v4.1-mutaciones-post`** [D, 2026-11-17] | **R6a, R6b, R6c, R7, R19** | Ninguna (sin configuración ni migración) | Rutina |
| **04-02** | Cookies seguras, redirección a HTTPS en Django, HSTS escalonado (3600 y luego 604800), orígenes CSRF, arranque que falla | Configuración (`settings.py`, `.env.example`) y `docs/operacion/` | No | Por fijar (**dos despliegues**: HSTS 3600 y 604800) | Ninguna | `settings.py` y `.env.example` | No la exige |
| **04-03** | Archivo temporal de opciones para `mysqldump` y `mysql`; clave secreta obligatoria | Código (`utils.py`) y configuración (`settings.py`, `.env.example`) | No | Por fijar | Ninguna | `settings.py` y `.env.example` | **Sí** (cambia respaldo y restauración) |
| **04-04** | Restauración: tope de 20 MB, validación por estructura, `RESTAURAR`, constancia, respaldo `emergencia_`, sin `.sql` vacío | Código (`utils.py`, `views.py`, `restaurar_bd.html`) | No | Por fijar | Ninguna | Ninguna de archivos (la 04-04 no toca configuración) | **Sí** |
| **04-05** | `django.conf.settings`, `conn_health_checks`, importaciones duplicadas, `TEMPLATES['DIRS']` vacío, pruebas con `override_settings` | Configuración y código (`settings.py`, `views.py`, `pedidos/urls.py`, `utils.py`) | No (Clase 1 sin migraciones) | Por fijar | Ninguna | `settings.py` | Rutina |
| **04-06** | `PROTECT` en `Pedido.cliente` y `Cotizacion.cliente`; `eliminar_cliente` informa por qué no | Código y **migración** | **`0008`** (Clase 1 esperada) | Por fijar | **R14** | `makemigrations` y `migrate` en local | **Sí** |
| **04-07** | Lista blanca con `nh3` al guardar y al mostrar; guardia de SQL con `ast` | Código y **dependencia** (`requirements.txt`) | No | Por fijar | Ninguna | `nh3` (**respondida**) y `mysql` para la consulta de revisión | Rutina |
| **04-08** | Límite de intentos por usuario y por dirección (admin y `accounts/login/`); evento `acceso_bloqueado`; imagen de 5 MB; chequeo temprano de `CONTENT_LENGTH`; redirección con sesión | Código, configuración (`settings.py`, `urls.py`, `.env.example`) y **migración** | **`0009`** (Clase 1, después de la `0008`) | Por fijar | Ninguna | `settings.py`, `urls.py`, `.env.example`, `makemigrations`/`migrate` y `mysql` | **Sí** |
| **04-09** | Cabecera `Content-Security-Policy-Report-Only` (solo observación) | Configuración (`settings.py`, `.env.example`) | No | Por fijar | Ninguna | `settings.py` y `.env.example` | No |
| **04-10** | Aviso con cantidad y monto de pagos, `ELIMINAR` exigido si hay pagos, evento `pedido_eliminado` con la cantidad | Código (`views.py`, `pedido_confirm_delete.html`) | **No** (la `0010` quedó descartada) | Por fijar | Ninguna (la cascada no cambia) | Ninguna de archivos; **+1 consulta** por pantalla: excepción a la sección 11 **aceptada el 2026-11-17** | Rutina |

[V] Cada fila sale del encabezado y los alcances de su iteración. Las etiquetas distintas de la 04-01 y las fechas no existen en ningún documento.

## 2. Orden de despliegue recomendado

Cada despliegue es un propósito, con etiqueta anotada antes (RDA-007) [V]. **Nada antes de cerrar la vigilancia de la 03-05** [D].

| Orden | Despliegue | Etiqueta (propuesta, salvo la 04-01) | Depende de (duro) | Antes del Reload |
| :---- | :--------- | :----------------------------------- | :---------------- | :--------------- |
| 1 | 04-01 | **`v4.1-mutaciones-post`** [D, fijada] | Épica 02 (terminada) | Respaldo de rutina |
| 2 | **04-10** (decisión del 2026-11-17: justo después de la 04-01) | `v4.2-confirmar-eliminar-pedido` | 04-01 | Respaldo de rutina |
| 3 | 04-02, escalón 1 (HSTS 3600) | `v4.3-configuracion-produccion` | — | **`.env` primero** (`SEGURIDAD_PRODUCCION`, `CSRF_TRUSTED_ORIGINS`) |
| 4 | 04-02, escalón 2 (HSTS 604800), tras **3 días** de observación sin 403 de CSRF ni bucles | `v4.4-hsts-semana` | escalón 1 | — |
| 5 | 04-03 | `v4.5-credenciales` | 04-02 (su variable y su regla de arranque) | Respaldo previo; ensayo de respaldo y restauración en la réplica |
| 6 | 04-04 | `v4.6-restauracion` | 04-03 y 04-01 | Respaldo previo |
| 7 | 04-05 | `v4.7-correcciones-config` | 04-02 y 04-04 (mismos archivos) | Respaldo de rutina |
| 8 | 04-06 | `v4.8-historial-clientes` | 04-01 y 04-05 | Respaldo previo; `migrate` (`0008`) |
| 9 | 04-07 | `v4.9-sanitizacion-html` | — (comparte `pedido_detail.html` con la 04-01 y `forms.py` con la 04-08) | **Instalar `nh3` en la consola antes** |
| 10 | 04-08 | `v4.10-acceso-limites` | 04-04 (chequeo temprano en `restaurar_bd`), 04-06 (numeración), 04-02 y 04-05 (`settings.py`) | Respaldo previo; `migrate` (`0009`); variables opcionales |
| 11 | 04-09 | `v4.11-csp-observacion` | 04-02 | — |

- **Orden decidido por el desarrollador el 2026-11-17 [D]:** la 04-10 va justo después de la 04-01. Antes iba al final; solo depende de la 04-01 y su riesgo (perder pagos al borrar un pedido) existe cada día. No cambia el diseño de ninguna iteración. Siguen valiendo el paso a paso de la épica y la regla «un despliegue, un propósito» (RDA-007) [V]; cada despliegue necesita `git checkout <etiqueta>` en el servidor (no `git pull`) [V, `despliegue.md`, 00-05].
- **Etiquetas: son una propuesta [I].** Siguen el patrón de las anteriores (`v0.1`, `v0.2` y `v0.3` en la Épica 00; `v1.1` y `v1.2`; `v3.1`) [V]: el número es el orden de despliegue dentro de la épica, sin tildes y con guiones. Solo `v4.1-mutaciones-post` está fijada. Confirmarlas o cambiarlas, y las fechas, es `PENDIENTE_DESARROLLADOR`; si el orden cambia, se renumeran.
- **Una sola rama (`main`):** para poder etiquetar el commit de cada iteración, **cada iteración va en su propio commit, en el orden de despliegue** (precedente: `v3.1-integridad` sobre `7e14398`, que reunió la 03-01 a la 03-04) [V].
- **Lo que exigen la Épica 08 y la 09:** la 08 pide la 04-09 desplegada; la 09 pide la 04-07 y la 04-08 [V].

### Dependencias y archivos compartidos con el nuevo orden (revisión del 2026-11-17)

**Nada se pisa**; cinco avisos para quien ejecute:

1. **Dependencias:** la 04-10 depende solo de la 04-01; ninguna de las otras depende de que la 04-10 vaya al final.
2. **`pedidos/views.py`:** la 04-01 cambia `cambiar_estado_pedido`, `duplicar_pedido`, `generar_respaldo_bd` y `eliminar_pago`; la 04-10, `eliminar_pedido`. Son funciones distintas, en commits separados y consecutivos. Los números de línea citados se desplazan: buscar por nombre.
3. **Plantillas:** la 04-01 crea `pago_confirm_delete.html` **copiando** `pedido_confirm_delete.html` y la 04-10 cambia esta después; la de pagos queda sin el campo de palabra (no se cambia el diseño). `pedido_detail.html` (04-01 y 04-07) no se cruza con la de confirmación.
4. **Criterio de comparación de `RESTAURAR` y `ELIMINAR`:** la 04-10 se despliega antes que la 04-04. El criterio está fijado en ambas (exacta, sensible a mayúsculas, con `strip()`); la 04-04 reutiliza la función si la 04-10 la crea.
5. **Importaciones de `views.py` y pruebas:** la 04-10 puede agregar importaciones (`Count`, `Sum`) que la 04-05 revisa después; las pruebas de la 04-10 (`test_eventos_negocio.py`, `test_bloqueo_envio.py:38`) no chocan con la caché que la 04-08 vacía más tarde. Línea base de la 04-10: **4 fallos esperados** (R8, R9, R14 y R15). Migraciones sin cambio: `0008` y `0009`.

### Qué se puede hacer mientras tanto [D]

**Hoy no se ejecuta nada en local.** Decisión del desarrollador del 2026-11-17: la ejecución de la 04-01 en local **espera el cierre de la vigilancia de la 03-05** (lectura del día 7 desde el lunes 2026-11-23 a las 23:48). **Próximo hito:** (a) viernes 2026-11-20, informe C2 de desconexiones de la 00-06; (b) desde el lunes 2026-11-23 a las 23:48, lectura del día 7, cierre de la 03-05 y limpieza de la réplica (parte F); (c) después, decidir el inicio de la 04-01. Lo que se hace ahora son solo documentos.

Cuando empiece, para no pisarse (sección 4): ejecutar **en el orden de despliegue**, una iteración por commit, con `test pedidos` en verde y el MySQL de Docker encendido (lo enciende el desarrollador). La **04-01** y la **04-10** no piden consultas previas de archivos (sin configuración ni migraciones); las demás sí (sección 6). Las revisiones de datos con consulta (04-06, 04-07, 04-08, 04-10) valen **a la fecha del último refresco de la réplica**: se hacen **después del refresco de la parte F de la 03-05** (`PENDIENTE_DESARROLLADOR`). El ensayo local de respaldo se ve limitado porque `mysqldump` no estaba instalado en la réplica (01-09, citado en la 04-03) [V].

## 3. Variables de entorno nuevas

**No hay otras** (búsqueda de nombres en las diez iteraciones el 2026-11-17) [V]. Las demás que usa `settings.py` ya existían: `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, `DB_*` (la 04-05 no agrega ninguna).

| Variable | Iteración | Por defecto | Qué pasa si falta |
| :------- | :-------- | :---------- | :---------------- |
| `SEGURIDAD_PRODUCCION` | 04-02 (D3); la usa la 04-03 | Falsa | En local: sin cookies seguras, HSTS ni redirección (es lo correcto). **En el servidor, con el dominio de producción en `ALLOWED_HOSTS`, la aplicación no arranca** (D5 de la 04-02). Con ella activa, la 04-03 además rechaza una clave con prefijo `django-insecure-` o corta |
| `CSRF_TRUSTED_ORIGINS` | 04-02 (D4) | `http://localhost:8000,http://127.0.0.1:8000` | En producción sin el origen `https://manzagrafica.pythonanywhere.com` [D, valor], los formularios podrían dar 403 de CSRF **[I]** (hoy funcionan sin ella porque el proxy probablemente entrega el esquema `https`; **[NV]**) |
| `SECRET_KEY` (ya existe) | 04-03 (D2) la vuelve obligatoria | — | No arranca (`ImproperlyConfigured`) en todo entorno |
| `ACCESO_PROXIES_CONFIABLES` | 04-08 (D3) | `0` (usa `REMOTE_ADDR`) | Si producción está tras un proxy y la variable no se fija, **todos los clientes comparten una dirección** y el contador por dirección bloquea a todos tras 20 fallos **[I]**; qué cabecera trae la dirección real y cuántos proxies hay: **[NV]**, se mide en la verificación 3 de la 04-08 |
| `ACCESO_FALLOS_POR_DIRECCION` | 04-08 (confirmada [D]) | `20` | Usa 20. `0` apaga **solo** el contador por dirección (interruptor de emergencia) |
| `CSP_OBSERVACION` | 04-09 (D3) | Activa (también en local) | Se envía la cabecera de observación. `False` la apaga. **Independiente** de `SEGURIDAD_PRODUCCION` |

**Orden en el servidor:** **`.env` primero**, luego el código (`git checkout <etiqueta>`), luego el Reload [V, 04-02]. Con las variables que cambian el arranque (`SEGURIDAD_PRODUCCION`), recargar código nuevo sin ellas tumba el sitio. Pasos intermedios: **`pip install` de `nh3` antes del Reload** (04-07) y **`migrate` después del checkout y antes del Reload** (04-06 y 04-08) [V, sus verificaciones de producción]. Las variables opcionales de la 04-08 y la 04-09 funcionan sin definirse; la 04-08 las necesita solo para medir la dirección. `.env.example` las documenta **sin valores reales** (04-02, 04-03, 04-08 y 04-09) [V].

## 4. Iteraciones que tocan los mismos archivos

[V] según el campo «Archivos que tocará la ejecución» de cada iteración.

| Archivo | Iteraciones | Riesgo de pisarse |
| :------ | :---------- | :---------------- |
| `PedidosApp/settings.py` | 04-02, 04-03, 04-05, 04-08, 04-09 | **Medio.** Zonas distintas (seguridad, `SECRET_KEY`, `TEMPLATES`/`BASE_DIR`/`DATABASES`, `CACHES` y límites, `MIDDLEWARE` y CSP) pero **cinco ediciones del mismo archivo**. Riesgo propio: cada una puede definir su propio lector de variables booleanas (`SEGURIDAD_PRODUCCION`, `CSP_OBSERVACION`); conviene reutilizar el de la 04-02 **[I]** |
| `PedidosApp/urls.py` | 04-08 | Bajo (única). La decisión de AUD-02-030 («solo documentado») evita una segunda edición de la misma línea |
| `pedidos/views.py` | 04-01, 04-04, 04-05, 04-06, 04-08, 04-10 | **Medio.** `restaurar_bd` lo tocan la 04-04 y la 04-08; las importaciones del encabezado, la 04-05 y las demás. **Los números de línea citados en las iteraciones se desplazan** con cada una: se buscan por nombre de función, no por número |
| `pedidos/utils.py` | 04-03, 04-04, 04-05 | **Alto entre la 04-03 y la 04-04:** ambas cambian `generar_respaldo_mysql` y `restaurar_bd_mysql`. Se ejecutan en ese orden |
| `pedidos/static/pedidos/js/index.js` | 04-01 | Bajo (única: `initDetailModals`) |
| `pedidos/templates/pedidos/base.html` | **Ninguna** | Ninguno (la 04-09 no toca plantillas; la 04-08 cambia `login.html`, que no extiende la base) |
| `pedido_detail.html` | 04-01 (botones, líneas 66 y 73), 04-07 (línea 115) | Bajo (zonas distintas) |
| Otras plantillas | `respaldar_bd.html` (04-01), `restaurar_bd.html` (04-04), `cliente_confirm_delete.html` (04-06), `cotizacion_detail.html` y `producto_detail.html` (04-07), `login.html` (04-08), `pedido_confirm_delete.html` (04-10) | Bajo (una cada una; `pago_confirm_delete.html` de la 04-01 copia el patrón de la de pedidos) |
| `pedidos/models.py` | 04-06 (claves foráneas), 04-08 (`choices` de eventos) | Bajo (zonas distintas) pero **migraciones encadenadas** |
| `pedidos/migrations/` | **`0008`** (04-06) y **`0009`** (04-08) | **La numeración depende del orden.** Hoy la última es `0007_registroevento` [V]. La `0009` depende de la `0008`: si cambiara el orden, se renumera y se revisa con `showmigrations` |
| `pedidos/forms.py` | 04-07, 04-08 | Bajo |
| `pedidos/senales.py`, `pedidos/admin.py` | 04-08 | Bajo (únicas) |
| `.env.example`, `docs/operacion/` | 04-02, 04-03, 04-08, 04-09 (y notas de la revisión final) | Bajo |
| Pruebas | `test_regresiones.py` (04-01 quita cinco marcas y actualiza su encabezado; 04-06 quita una), `ayudas.py` (04-01), `test_eventos_negocio.py` (04-08, 04-10), `test_acceso.py`, `test_bloqueo_envio.py` (04-10 conserva `data-bloquear-envio`), `test_arranque.py` (04-02) | Bajo |

**Recomendación:** ejecutar en orden, **un commit por iteración**, y repetir `test pedidos` entre una y otra. Como la caché local **no se vacía entre pruebas**, las pruebas de acceso fallido de la 04-08 deben vaciarla en `setUp` (está en su plan) **[V]**.

## 5. Regresiones y fallos esperados

[V] `pedidos/tests/test_regresiones.py` el 2026-11-17: **nueve** `@expectedFailure` reales (el décimo resultado de la búsqueda es la línea 5, de un comentario del encabezado). La línea base documentada es **267 pruebas, `OK (expected failures=9)`** (dato de la 03-04, citado por la 04-01 [V]; **no se volvió a medir**: se mide de nuevo al ejecutar).

| Después de… | Pasan a verde | Fallos esperados |
| :---------- | :------------ | :--------------- |
| Hoy | — | **9:** R6a, R6b, R6c, R7, R8, R9, R14, R15, R19 |
| 04-01 | R6a, R6b, R6c (escritura por GET), R7 (confirmar eliminar pago), R19 (duplicado con autor) | **4:** R8, R9, R14, R15 |
| 04-06 | R14 (eliminar cliente con pedidos) | **3:** R8, R9, R15 |
| 04-02, 04-03, 04-04, 04-05, 04-07, 04-08, 04-09, 04-10 | Ninguna | 3 |

- **Fallos esperados finales de la Épica 04: 3** (R8 y R9, día y mes en UTC, van a la **06-01**; R15, porcentaje con `float`, a la **06-05**) [V, comentarios de `test_regresiones.py`].
- La 04-10 **no** retira ningún `expectedFailure`: no cambia la cascada de pagos. Sus pruebas son nuevas de comportamiento.
- Las demás iteraciones agregan pruebas nuevas (cada una lista su tabla); el número exacto se mide al ejecutar. La 04-05 reescribe seis pruebas que parchan `views.settings.BASE_DIR` (`override_settings`) [V].

## 6. RDA propuestos y consultas previas pendientes

**RDA** (`decisiones.md`: la última vigente es la RDA-019 [V]):

| RDA | Estado | Cuándo |
| :-- | :----- | :----- |
| **RDA-020** · sanitización del HTML enriquecido con `nh3`, al guardar y al mostrar | **Propuesto; se escribe al ejecutar la 04-07** [D]; no está en `decisiones.md` | Paso 7 de la 04-07 |
| RDA-021 | **No hace falta**: se habría usado solo con `django-axes` (descartado) | — |

**Consultas previas** (`AGENTS.md`, secciones 6 y 11) que quedan **pendientes** para ejecutar:

| Qué | Iteraciones |
| :-- | :---------- |
| Editar `PedidosApp/settings.py` | 04-02, 04-03, 04-05, 04-08, 04-09 |
| Editar `.env.example` | 04-02, 04-03, 04-08, 04-09 |
| Editar `PedidosApp/urls.py` | 04-08 |
| `makemigrations` y `migrate` en local, y editar `pedidos/migrations/` | 04-06 (`0008`), 04-08 (`0009`) |
| Dependencia **`nh3`** (`requirements.txt` e instalación) | 04-07: **la consulta está respondida** [D]; falta comprobar la instalación en PythonAnywhere (paso 0 de la 04-07; peso y arranque en frío sin medir) **[NV]** |
| `mysql`/`dbshell`, incluso en local (consultas de solo lectura) | 04-06 (`SHOW CREATE TABLE`), 04-07 (conteos), 04-08 (fallos por ventana), 04-10 (conteos) |
| **Aumento de consultas por página** (`AGENTS.md`, sección 11) | 04-10: +1 en la pantalla de confirmación: **excepción aceptada el 2026-11-17** [D], solo esa pantalla y solo +1; se mide antes y después |

Ninguna iteración crea ramas ni elimina o mueve archivos [V, búsqueda en sus pasos].

## 7. Contradicciones

### 7.1 Corregidas en esta revisión (error de redacción)

| # | Contradicción | Corrección |
| :- | :------------ | :--------- |
| 1 | La 04-02 y la definición piden `check --deploy` **sin advertencias** y la 04-02 D1 fija HSTS **sin `includeSubDomains` ni `preload`**. Django emite `security.W005` y `security.W021` cuando `SECURE_HSTS_SECONDS` es mayor que cero y esas opciones no son `True` [V, `django/core/checks/security/base.py:177-195`]. La 04-02 esperaba «solo W009» en local y «ninguna» en producción | Se corrigen el paso 5, la verificación 1 y el criterio de término de la 04-02 y el criterio de la definición: **quedan W005 y W021 por D1**, **aceptadas y documentadas como esperadas** (decisión del 2026-11-17, sin silenciar; ver la nota de la 04-02: el dominio es de PythonAnywhere) |
| 2 | La 04-10 decía que alinearía `ELIMINAR` con la 04-04, pero la 04-04 no fijaba el criterio de comparación de `RESTAURAR` | La 04-04 sí rechaza `restaurar` en minúsculas (fila 3 de sus pruebas) [V]: **coincidencia exacta y sensible a mayúsculas**; en ambas se ignoran los espacios del inicio y del final (`strip()`). Se agrega a la fila de pruebas de la 04-04 y a la 04-10 |
| 3 | La 04-10 se había redactado con la opción de un tipo de evento nuevo y la migración `0010`; el desarrollador la descartó (D1) | Retirada de la 04-10 y del registro: **la 04-10 no crea migración**. Los textos históricos (bitácora de redacción, notas fechadas) conservan la mención como registro |
| 4 | La definición llama «límite de tamaño» a `FILE_UPLOAD_MAX_MEMORY_SIZE`, que en Django es un umbral entre memoria y disco [V, `uploadhandler.py:208`] | Aclaración en el alcance 8 de la definición (la 04-08 ya lo trataba) |
| 5 | El criterio de término de la definición **no cubría** la 04-04, la 04-05 ni los tamaños de la 04-08, y el de intentos fallidos no tenía las cifras | Bullets agregados (sección 9) |
| 6 | La 04-10 decía «sin consulta previa» y su pantalla hace **una consulta más** (`AGENTS.md`, sección 11) | Paso 0 de la 04-10 con la medición antes y después y el aviso |
| 7 | La 04-07 decía compartir `views.py` con la 04-01 y la 04-06, pero su lista de archivos no incluye `views.py` (la creación rápida de productos usa `ProductoForm`, que cambia en `forms.py`) | Encabezado de la 04-07 corregido: comparte `pedido_detail.html` con la 04-01 y `forms.py` con la 04-08 |

### 7.2 Que son decisión del desarrollador (no se corrigieron)

1. **W005 y W021** (7.1, punto 1): **resuelta el 2026-11-17 [D]:** se aceptan y quedan documentadas como esperadas; **no se silencian**. Razón (nota de la 04-02): `preload` exige el dominio registrable, que es de la plataforma, y `includeSubDomains` protegería subdominios que no existen [I].
2. **`AGENTS.md`, regla 8.5 (GET nunca escribe):** al terminar la épica queda **una** escritura con GET, el panel (`registrar_metricas_diarias`, AUD-01-006). Es la excepción P2 de la 04-01 (decisión del desarrollador, 2026-11-17): la corrige la 06-01 [V].
3. **Regla 8.10 (un worker, nada lento en la petición):** la restauración (04-04) corre dentro de la petición; está anotada como riesgo y propuesta (registro, sección 4: restaurar desde consola, 06-03 o Épica 14) [V]. Además, la 04-08 agrega el chequeo temprano de `CONTENT_LENGTH` a esas vistas (barato) y la 04-10 borra dentro de la petición (corto).
4. **Regla 8.17 (sin recursos nuevos desde CDN):** las diez iteraciones **no agregan ninguno** [V]. Los cinco servidores externos que ya existen (Tailwind, jQuery, Select2, Summernote, SweetAlert2, Google Fonts) los resuelve la Épica 08 (08-05 a 08-08); la 04-09 solo los observa. `login.html` repite su propio `<head>` y no extiende la base.
5. **Regla 8.12 / sección 11 (consultas por página):** la 04-10 suma una consulta en su pantalla. **Excepción aceptada el 2026-11-17 [D]**, solo para esa pantalla y para +1; consta en la 04-10, la definición y el registro.
6. **`DESIGN.md` (modal de confirmación) frente a las confirmaciones como página** (04-01 P1 y 04-10): se mantiene el patrón vigente; lo cambia la Épica 08.
7. **Reglas que se cumplen** (no son contradicción): 8.9 (`nh3` se importa dentro de la función, 04-07), 8.11 (la 04-08 no crea tablas; el evento nuevo usa la tabla existente, con retención de 365 días), 8.3 y 8.4 (las operaciones de varias filas van en `atomic` y sin supresión silenciosa), 8.7 (variables de entorno, sin secretos).

## 8. Abiertos

### 8.1 `PENDIENTE_CLIENTE`

- **Pagos borrados en cascada con el pedido:** ¿el borrado es intencional? El cliente **no ha respondido** (registro, sección 2); la 04-10 no espera la respuesta [D].
- **Duplicar un pedido:** ¿se copian ítems y pagos? Abierta (registro, sección 2); la 04-01 no cambia qué se copia, salvo `creado_por`.
- Las demás preguntas de la sección 2 del registro (IVA, pedido de $0, sobrepago, `ENTREGADO` atrasado, pedidos duplicados históricos, qué vio el cliente el 2026-10-27) **no son de la Épica 04**.

### 8.2 `PENDIENTE_DESARROLLADOR` de la épica

1. **Etiquetas** de la 04-02 a la 04-10 (hay una propuesta en la sección 2; incluye la del segundo escalón de la 04-02) y **fechas** de todos los despliegues; la 04-01 ya tiene etiqueta y su fecha se fija al cerrar la vigilancia.
2. **Cuándo empieza la 04-01 en local:** no antes de cerrar la vigilancia de la 03-05; después, decidirlo (próximo hito, sección 2).
3. **Escribir la RDA-020 y las notas operativas «documentado»** en `docs/operacion/` (AUD-04-003, AUD-02-030, AUD-02-023 y «eliminar cotización sin evento»): **al ejecutar la 04-07** (decisión del 2026-11-17).
4. **Revisiones de datos en la réplica** (04-06, 04-07, 04-08, 04-10): después del refresco de la parte F de la 03-05.
5. **04-08:** la consulta de fallos por ventana y el archivo más grande de `media/referencias/` (evidencia previa, con regla de detención); el **número de usuarios de producción**; y la **medición de la dirección real** tras el proxy (no se puede calibrar el límite por dirección con datos).
6. **04-01:** deja abierta la **página 405 propia** (otra iteración).
7. **Propuesta ya registrada:** restauración fuera de la petición (06-03 o Épica 14).

### 8.3 Resuelto el 2026-11-17 (decisiones posteriores del desarrollador)

W005 y W021 aceptadas y documentadas; la 04-10 se despliega justo después de la 04-01; excepción a la sección 11 de `AGENTS.md` por la consulta adicional de la 04-10; la ejecución local de la 04-01 espera el cierre de la vigilancia de la 03-05. Detalle en [bitacora-04-cierre-redaccion](bitacora-04-cierre-redaccion.md).

## 9. Criterio de término frente a lo que cubren las diez iteraciones

| Criterio de la definición | Lo cubre | Cómo se verifica |
| :------------------------ | :------- | :--------------- |
| `check --deploy` en producción sin advertencias | 04-02 (W004, W008, W012, W016), 04-03 (W009) | **Producción [NV].** **Salvo W005 y W021, documentadas como esperadas** (decisión del 2026-11-17) |
| R6a-c, R7, R19 y R14 pasan a verde | 04-01 y 04-06 | Pruebas automatizadas |
| Ningún proceso muestra la contraseña de la base | 04-03 | Producción [NV] |
| Un respaldo desde la web se descarga en el equipo | 04-01 | Producción [NV], después del despliegue de la 04-01 |
| Un `<script>` guardado no se ejecuta | 04-07 | Prueba automatizada |
| Después de N intentos fallidos, bloqueo y evento | 04-08 (**N = 5 por usuario y 20 por dirección, 15 minutos**) | Prueba automatizada; la dirección real, **producción [NV]** |
| CSP activa en modo observación en producción | 04-09 | Producción [NV] |
| Pedido con pagos solo se elimina con confirmación y deja evento con la cantidad | 04-10 | Prueba automatizada |
| **Agregados en esta revisión:** la restauración rechaza archivos inválidos, exige `RESTAURAR` y deja constancia | 04-04 | Pruebas automatizadas y producción |
| **Agregado:** la imagen de referencia de más de 5 MB se rechaza | 04-08 | Prueba automatizada |
| **Agregado:** las correcciones de configuración no cambian el comportamiento | 04-05 | Suite en verde y revisión manual |
| Las decisiones «riesgo aceptado» y «solo documentado» están escritas en `docs/operacion/` | Se escriben al ejecutar la 04-07 (decisión del 2026-11-17) | Revisión de documentos |

**Cobertura:** las diez iteraciones cubren los once puntos de alcance de la definición (con el 12 agregado por la 04-10); AUD-04-003 y AUD-02-030 se resuelven por decisión documentada, sin iteración; la página de error de CSRF va a la Épica 08 y AUD-02-023 a la Épica 14. **Hallazgos que se cierran al cumplirse la épica** (cada uno al verificarse en producción): AUD-01-009, -012, -013, -016, -018, -025; AUD-02-001, -002, -006 (parte GET), -016, -024, -028; AUD-03-001, -002, -004; AUD-05-008 (parte 2); AUD-02-010 y AUD-04-003 por riesgo aceptado.

## Archivos de esta revisión

`bitacora-04-revision-final.md` (nuevo), `bitacora-04-10-cierre.md` (nuevo), `iteracion-04-10-…`, `iteracion-04-04-…`, `iteracion-04-02-…`, `definicion-epica-04.md` y `00_producto/registro-pendientes.md` (por bytes, CRLF intacto). `auditoria-tecnica.md` no cambió.
