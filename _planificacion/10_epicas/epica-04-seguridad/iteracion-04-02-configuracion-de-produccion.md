# Iteración 04-02 · Configuración de producción

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** **Completada y verificada en producción (2026-11-19)**: `v4.3-configuracion-produccion` (`c62a92e`) y `v4.4-hsts-semana` (`854cd74`). AUD-01-012 resuelto. W005 y W021 siguen aceptadas, sin silenciar. HSTS de 604800 s ya emitido: dura hasta 7 días en los navegadores. ~~Escalón 1 desplegado y verificado (pendiente solo `sessionid` con `Secure` en el navegador); escalón 2 implementado, pendiente de despliegue~~ (2026-11-19, [bitacora-04-02](../../99_bitacora/epica-04-seguridad/bitacora-04-02.md), [bitacora-04-02-escalon-2](../../99_bitacora/epica-04-seguridad/bitacora-04-02-escalon-2.md)). ~~Escalón 1 implementado, pendiente de despliegue; escalón 2 pendiente~~. **Etiquetas (decisión del desarrollador, 2026-11-19):** `v4.3-configuracion-produccion` (HSTS 3600) y `v4.4-hsts-semana` (HSTS 604800). **Retroceso:** `v14.2-duplicar-items`. Se avisa al cliente antes del despliegue. Antes: Pendiente (redactada, decisiones resueltas). Redactada el 2026-11-17 ([bitacora-04-02-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-02-redaccion.md)); D1 a D6 **resueltas el 2026-11-17** por el desarrollador (dicho por él; [bitacora-04-02-cierre](../../99_bitacora/epica-04-seguridad/bitacora-04-02-cierre.md)). Queda abierta solo la etiqueta y la fecha del despliegue.
- **Subfase del plan:** 4.2 «Configuración de producción» (`plan-de-trabajo.md:400-408`).
- **Depende de:** Épica 02 (Terminada). Se redactó en paralelo a la vigilancia de la 03-05; ~~**su ejecución en local no empieza hasta cerrar esa vigilancia** (decisión del desarrollador, 2026-11-17). **No se despliega antes de cerrar la vigilancia de la 03-05 (desde el lunes 2026-11-23 a las 23:48:12)**~~ **superado el 2026-11-18 (RDA-021): no hay vigilancia que cerrar**; no se despliega en el mismo despliegue que la 04-01 (RDA-007). Orden (decisión del 2026-11-17; desde el 2026-11-18 la 14-01 va antes): 14-01, 04-01, **04-10**, 04-02 (dos escalones, el mismo día), 04-03 y siguientes.
- **RDA relacionadas:** RDA-004 (PythonAnywhere, plan gratuito), RDA-007 (un despliegue, un propósito; la etiqueta marca lo que está en producción).
- **Hallazgos que cierra:** AUD-01-012 (configuración de producción sin endurecer), al verificarse en producción.
- **Hallazgos relacionados:** AUD-02-022 (`ALLOWED_HOSTS`, **ya resuelto en la 00-04**: no se repite), AUD-02-010 y la advertencia `W009` (clave secreta: 04-03, que usa `SEGURIDAD_PRODUCCION`).
- **Cambio de esquema:** ninguno.
- **Respaldo previo al despliegue:** no lo exige por sí misma (sin migraciones ni datos). Se sigue el protocolo normal.
- **Archivos que tocará la ejecución:** `PedidosApp/settings.py` y `.env.example` (configuración: **requiere consulta previa**, `AGENTS.md` sección 6), `docs/operacion/despliegue.md` y `retroceso.md` (advertencias esperadas y retroceso de la variable), y pruebas. El `.env` del servidor lo edita solo el desarrollador.

## Objetivo

Que `python manage.py check --deploy` en producción no muestre advertencias resueltas a ciegas, que las cookies viajen solo por HTTPS, que Django y PythonAnywhere lleven siempre a HTTPS, que HSTS se introduzca con un periodo corto y que la aplicación se niegue a arrancar con una configuración insegura.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-17 en `main` (`253a9c2`), con archivo y línea.
- **Dicho por el desarrollador:** no comprobado por el agente.
- **Inferido:** sale de leer el código o del comportamiento documentado de Django; se dice cómo se confirma.
- **No verificado (producción):** solo se ve en el servidor o en un navegador contra el dominio real.

## Qué hay hoy

### `settings.py` (verificado)

- `DEBUG = os.getenv('DEBUG') == 'True'` (`settings.py:42`): sin la variable, `DEBUG` es falso.
- `ALLOWED_HOSTS` desde el entorno, con `localhost,127.0.0.1` por defecto y rechazo de `'*'` con `ImproperlyConfigured` (`:47-53`, 00-04). **No se toca.**
- `SECRET_KEY = os.getenv('SECRET_KEY')` sin comprobación (`:37`): es de la 04-03.
- `SecurityMiddleware` es el primero de `MIDDLEWARE` (`:70`); `XFrameOptionsMiddleware` está.
- **No hay** `SECURE_SSL_REDIRECT`, `SECURE_PROXY_SSL_HEADER`, `SECURE_HSTS_*`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` ni `CSRF_TRUSTED_ORIGINS` (búsqueda en `settings.py`).
- Ya existe el patrón «fallar al arrancar»: `ImproperlyConfigured` por `'*'` en hosts (`:52-53`), por falta de contraseña local (`:109-113`) y por base de pruebas real (`:142-145`).

### Advertencias de `check --deploy`

| Fuente | Advertencias | Estado |
| :----- | :----------- | :----- |
| Local, 00-05 (2026-10-21), `despliegue.md:114` | W004, W008, W009, W012, W016 | Documentado |
| Local, 03-05 (`evidencia-03-05.md:164`) | W004, W008, W009, W012, W016 | Documentado |
| Producción, antes y después del despliegue de la 03-05 (`evidencia-03-05.md:284`, `:341`) | «No informado» | Sin dato en el repo |
| Producción, dicho por el desarrollador (2026-11-17) | W004 (HSTS), W008 (redirección a HTTPS), W012 (cookie de sesión), W016 (cookie CSRF) | **Dicho por el desarrollador, no verificado aquí.** Coherente con AUD-02-010: la clave de producción no es la del commit inicial, por eso no sale W009. |

### PythonAnywhere

- La línea base del 2026-10-20 anotó **«Force HTTPS activado»** en la web app (`linea-base-produccion.md:141`). Medido entonces; **no verificado hoy**.
- **Inferido:** con Django 6.0, un POST por HTTPS con cabecera `Origin` solo pasa la comprobación CSRF si `request.is_secure()` es verdadero o el origen está en `CSRF_TRUSTED_ORIGINS`. Como hoy los formularios funcionan en producción sin ninguna de las dos opciones, lo más probable es que PythonAnywhere entregue la petición a Django con esquema `https`. Si no fuera así, `SECURE_SSL_REDIRECT` (D2) haría un **bucle de redirecciones**. Esto solo se confirma en producción.

## Decisiones (resueltas el 2026-11-17, dichas por el desarrollador)

| # | Decisión | Qué se hace |
| :- | :------- | :---------- |
| D1 | HSTS escalonado, sin `preload` | Primer despliegue con `SECURE_HSTS_SECONDS = 3600`; tras ~~la observación~~ **la comprobación del mismo día** (D6, RDA-021), un segundo despliegue de esta iteración sube a `604800`. Sin `SECURE_HSTS_PRELOAD` (el dominio es un subdominio de `pythonanywhere.com`, no propio) y sin `SECURE_HSTS_INCLUDE_SUBDOMAINS` (inferido: no hay subdominios propios; se anota en la ejecución). El valor alto (`31536000`) no es parte de esta iteración. |
| D2 | Django **también** redirige a HTTPS | `SECURE_SSL_REDIRECT = True` cuando `SEGURIDAD_PRODUCCION` está activa, además de «Force HTTPS» de PythonAnywhere. Se prueba antes en la réplica (ver «Pruebas») por el riesgo de bucle. |
| D3 | Variable de entorno explícita | Las opciones seguras (cookies, redirección, HSTS) se activan con una variable propia, no derivada de `DEBUG`. Nombre fijado por el desarrollador el 2026-11-17: **`SEGURIDAD_PRODUCCION`** (`True`/`False`, falso si falta). Va en `.env.example` sin valor real y en el `.env` del servidor (lo edita el desarrollador). |
| D4 | `CSRF_TRUSTED_ORIGINS` desde el entorno | Lista separada por comas, con valor local por defecto `http://localhost:8000,http://127.0.0.1:8000`; en el servidor, `https://manzagrafica.pythonanywhere.com`. |
| D5 | Arranque que falla | `ImproperlyConfigured` si `ALLOWED_HOSTS` contiene `manzagrafica.pythonanywhere.com` y `SEGURIDAD_PRODUCCION` no está activa. Compensa el riesgo de olvidar la variable (D3). |
| D6 | ~~Observación de 3 días~~ **Comprobación del mismo día (RDA-021, 2026-11-18)** | ~~Tres días sin 403 de CSRF, sin bucles ni reportes del cliente antes de subir HSTS a `604800`. Sustituye los 7 días propuestos en la redacción.~~ **El segundo escalón (`604800`) sube el mismo día, después de comprobar el primero (`3600`) con los pasos 1 a 5 de la verificación:** sin 403 de CSRF, sin bucles y sin errores nuevos en `server.log`. Siguen siendo **dos despliegues**, cada uno con su etiqueta. |

**Nota: W005 y W021 (decisión del desarrollador, 2026-11-17).** Con HSTS activo y sin `includeSubDomains` ni `preload`, `check --deploy` seguirá mostrando `security.W005` y `security.W021` (verificado en `django/core/checks/security/base.py:177-195`). **Se aceptan y quedan documentadas como esperadas; no se silencian.** Por qué: el dominio es de PythonAnywhere, no propio. `preload` exige el dominio registrable (`pythonanywhere.com`), que pertenece a la plataforma, así que el sitio no puede enviarse a esa lista. `includeSubDomains` protegería subdominios de `manzagrafica.pythonanywhere.com`, que no existen (inferido), y activarlo sin necesidad agrega un riesgo: si algún día se usara un subdominio sin HTTPS, los navegadores lo bloquearían durante el `max-age`. Dejarlas visibles evita esconder que HSTS está en modo prudente. Se anotan como esperadas en `despliegue.md` (alcance 7).

**Riesgo de D3 (olvidar la variable):** si el `.env` del servidor no la trae, Django arrancaría sin cookies seguras ni HSTS ni redirección, en silencio. D5 lo convierte en un fallo ruidoso: la web app no arranca y el despliegue se nota en la verificación. Riesgo residual: un error al escribir el dominio en `ALLOWED_HOSTS` desactivaría D5; la verificación de producción (pasos 1 y 3) lo detecta. El orden de edición en el servidor importa: **primero `.env`, luego código, luego Reload** (si se recarga código nuevo sin la variable, D5 tumba el sitio hasta corregir `.env`).

## Alcance

1. **Variable de seguridad (D3)** y bloque de seguridad en `settings.py` que depende de ella.
2. **Cookies seguras:** `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` (W012, W016).
3. **Redirección a HTTPS en Django (D2)** (W008).
4. **HSTS escalonado (D1)** (W004).
5. **Orígenes CSRF de confianza (D4).**
6. **Arranque que falla (D5).**
7. **Documentación:** lista de advertencias esperadas de `despliegue.md:114` (queda W009 en local hasta la 04-03; **W005 y W021 se agregan como esperadas**, con la nota de abajo); paso nuevo en el despliegue (editar `.env` antes del Reload) y en `retroceso.md` (qué hacer con la variable al volver atrás).
8. **Fuera:** `ALLOWED_HOSTS` (00-04), `SECRET_KEY` obligatoria y W009 (04-03), política de contenido (04-09), límites de subida (04-08), limpieza de `settings.py` (04-05).

## Pasos

0. Consulta previa al desarrollador para editar `settings.py` y `.env.example` (`AGENTS.md`, sección 6).
1. Línea base local: `check --deploy` con `DEBUG=False` (esperado: W004, W008, W009, W012, W016) y `test pedidos` (se anota el número tras la 04-01).
2. Pruebas primero (sección siguiente).
3. Bloque de seguridad en `settings.py` según D1 a D5, con comentarios en español.
4. `.env.example` con `SEGURIDAD_PRODUCCION` y `CSRF_TRUSTED_ORIGINS`, sin valores reales.
5. `check --deploy` local con `DEBUG=False` y la variable activa: esperado **W009** (la resuelve la 04-03) y **W005 y W021**, que quedan **por D1** (HSTS sin `includeSubDomains` ni `preload`; Django las emite cuando `SECURE_HSTS_SECONDS` es mayor que cero y esas opciones no son `True`, verificado en `django/core/checks/security/base.py:177-195`). **Decisión del desarrollador (2026-11-17): se aceptan y quedan documentadas como esperadas; no se silencian** (ver «Nota: W005 y W021»). Con la variable apagada, `runserver` sigue entrando por `http://127.0.0.1:8000` sin redirección.
6. Ensayo en la réplica de D2 (sección «Pruebas»).
7. `despliegue.md` y `retroceso.md`.
8. Bitácora, registro, estado «En revisión», con los pasos de producción para el desarrollador.

## Pruebas

- **Arranque inseguro (D5):** un proceso hijo que importa la configuración con `ALLOWED_HOSTS` de producción y la variable apagada termina con `ImproperlyConfigured`; con la variable activa arranca; con valores locales y la variable apagada arranca. Lugar sugerido: `test_arranque.py` o `test_entorno.py` (existen; se revisa cuál corresponde al ejecutar).
- **Valores por entorno (D3, D1, D4):** con la variable activa, las cookies son seguras, `SECURE_SSL_REDIRECT` es verdadero y HSTS vale 3600; apagada, no. `CSRF_TRUSTED_ORIGINS` toma el valor local por defecto sin variable.
- **Redirección (D2), con el cliente de pruebas:** con la variable activa, una petición normal recibe 301 a `https://`; una petición marcada segura (`secure=True`) no se redirige y lleva `Strict-Transport-Security: max-age=3600`.
- **Ensayo en la réplica (D2):** `runserver` no sirve HTTPS, así que con la variable activa el navegador recibe 301 a `https://127.0.0.1:8000` y no carga: eso confirma la redirección, **no descarta el bucle**. El bucle depende de cómo el proxy de PythonAnywhere entrega el esquema y **solo se verifica en producción** (paso 3). Se ensaya además el arranque con la variable apagada y el dominio de producción (D5) y el retroceso de la variable.
- **Sin efecto en el resto:** la suite sigue con los mismos fallos esperados que deje la 04-01 (4: R8, R9, R14, R15). Las pruebas corren con la variable apagada; si llegara activa, todas las peticiones darían 301.

## Verificación en producción (la hace el desarrollador; todo **no verificado** hasta entonces)

1. **[PA]** `check --deploy` en el servidor, con el filtro de códigos de `evidencia-03-05.md:273`, **antes** y **después**: antes, W004 W008 W012 W016 (dicho por el desarrollador); después, **solo W005 y W021** (esperadas y documentadas; el filtro de códigos las debe incluir para esta lectura).
2. **[PA · Panel]** «Force HTTPS» sigue activado.
3. **[PC]** `curl -sI http://manzagrafica.pythonanywhere.com/accounts/login/` redirige a `https://`; `curl -sIL https://manzagrafica.pythonanywhere.com/accounts/login/` termina en 200 **sin bucle** (`curl` corta tras demasiadas redirecciones) y trae `Strict-Transport-Security: max-age=3600` y `Set-Cookie: csrftoken=…; Secure`.
4. **[Navegador, ventana privada]** iniciar sesión, crear un pedido y un pago de prueba según el protocolo vigente, generar un respaldo (descarga) y **abrir «Reabrir Pedido» y enviarlo con una fecha desde mañana** sobre el pedido de prueba (formulario POST nuevo de la 14-02; agregado el 2026-11-19): ningún 403 de CSRF. Las pantallas de `despliegue.md`, sección 3.7. Los pedidos de prueba se borran al final.
5. **[PA]** `server.log` desde el reinicio efectivo: sin `Forbidden (CSRF` ni errores nuevos.
6. ~~**Observación (D6):** 3 días. Después, segundo despliegue con HSTS `604800` y repetición de los pasos 1, 3 y 5.~~ **Comprobación del mismo día (D6, RDA-021):** con los pasos 1 a 5 hechos y sin problemas, el mismo día, segundo despliegue con HSTS `604800` y repetición de los pasos 1, 3 y 5.

## Plan de retroceso

- **Bucle de redirecciones o 403 de CSRF:** `retroceso.md`, caso 1 (sin migraciones): volver a la etiqueta anterior y recargar. **Más rápido:** poner `SEGURIDAD_PRODUCCION` en `False` en el `.env` del servidor y recargar apaga redirección, cookies seguras y HSTS sin tocar el código; pero D5 impide arrancar así con el dominio de producción, de modo que con la variable apagada **hay que volver también el código**. Se ensaya en la réplica cuál de los dos caminos se documenta.
- **Lo que no se revierte:** el HSTS ya recibido, durante su `max-age`. Por eso 3600 s primero: tras el retroceso, los navegadores aceptan HTTP de nuevo en una hora como máximo. Con «Force HTTPS» activo, el sitio funciona igual por HTTPS.
- **Disparadores:** bucle de redirecciones, 403 de CSRF en formularios, el cliente no puede iniciar sesión, la web app no arranca por D5.

## Criterio de término

- `check --deploy` en producción sin advertencias, **salvo W005 y W021, documentadas como esperadas** (D1; decisión del 2026-11-17: no se silencian; no verificado hasta el despliegue).
- Redirección a HTTPS sin bucle, cookies `Secure` y HSTS vistos en producción con el escalón vigente (3600, luego 604800).
- Arranque con el dominio de producción y la variable apagada falla con un mensaje claro (prueba automatizada).
- Suite en verde con los mismos fallos esperados que deje la 04-01.
- ~~Observación de 3 días cumplida y subida a 604800 registrada en la bitácora.~~ Comprobación del primer escalón y subida a 604800 el mismo día, registradas en la bitácora (RDA-021).

## Riesgos

- **Bucle de redirección (D2):** solo verificable en producción; mitigado con la prueba del cliente de pruebas, la verificación 3 inmediata y el retroceso del caso 1.
- **Olvidar la variable (D3):** mitigado con D5 y con el orden `.env` → código → Reload.
- **HSTS irreversible por `max-age`:** mitigado con 3600 s primero (D1). **Desde el 2026-11-18 (RDA-021) el escalón de 3600 s dura solo lo que tarda la comprobación del mismo día:** un problema que aparezca después de subir a 604800 puede durar hasta 7 días en los navegadores que ya recibieron la cabecera. «Force HTTPS» de PythonAnywhere ya estaba activo (medido el 2026-10-20), lo que lo hace menos probable (inferido, no verificado hoy).
- **Sesiones abiertas:** al pasar las cookies a `Secure`, las sesiones vigentes siguen por HTTPS (inferido). Se avisa al cliente antes del despliegue.
- **Un despliegue, un propósito (RDA-007):** solo configuración de producción; ni la 04-01 ni la 04-03 viajan en la misma etiqueta. La subida de HSTS es un despliegue aparte de esta misma iteración.

## Ejecución del escalón 1 (2026-11-19)

Detalle en [bitacora-04-02](../../99_bitacora/epica-04-seguridad/bitacora-04-02.md). Consulta previa de `settings.py` y `.env.example` aprobada el 2026-11-19, solo para esta iteración.

- **`settings.py`**, después de `ALLOWED_HOSTS`: `SEGURIDAD_PRODUCCION` (solo `'True'` la activa), `ImproperlyConfigured` si `ALLOWED_HOSTS` trae `manzagrafica.pythonanywhere.com` y la variable no está activa (D5), `CSRF_TRUSTED_ORIGINS` del entorno con los dos orígenes locales por defecto (D4) y, con la variable activa, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT` y `SECURE_HSTS_SECONDS = 3600`.
- **`SECURE_PROXY_SSL_HEADER` no se define:** la iteración no lo exige y lo da por innecesario (inferido de que hoy los POST pasan CSRF). Si la verificación 3 muestra un bucle, el retroceso es el caso 1 y la cabecera se decide en otra iteración.
- **Pruebas:** `pedidos/tests/test_seguridad_produccion.py`, 11 pruebas (9 fallaban antes del cambio).
- **`.env.example`: no editado.** La configuración de permisos de Claude Code bloquea leerlo; el desarrollador agrega las líneas de la bitácora.

## Despliegue y verificación del escalón 1 (2026-11-19)

Hora de Chile; la consola de PythonAnywhere marca UTC (Chile = UTC−3). «Pegado» quiere decir que la salida se pegó en la conversación; «dicho», que lo dijo el desarrollador y el agente no lo comprobó.

| Paso | Resultado | Fuente |
| :--- | :-------- | :----- |
| Respaldo previo | `respaldo_19-11-2026_11-13-02.sql`, `VÁLIDO`, 19 de 19, SHA-256 `d239d9dd…898a` | Pegado |
| Etiqueta | `v4.3-configuracion-produccion` sobre `c62a92e`; `git diff` de `v14.2-duplicar-items` a `v4.3` solo con `settings.py` (+38) | Pegado |
| `.env` del servidor | `SEGURIDAD_PRODUCCION=True` y `CSRF_TRUSTED_ORIGINS=https://manzagrafica.pythonanywhere.com` | Pegado |
| 1 · `check --deploy` | Antes: W004, W008, W012, W016. Con el código nuevo, **antes del Reload**: solo W005 y W021. **No se repitió después del Reload** | Pegado |
| Reload | uWSGI reinicia a las 11:23:50 y queda listo a las 11:24:07, sin errores. Se había dicho 11:25: **vale el registro** | Pegado (`server.log`) |
| 2 · «Force HTTPS» | Activado en la pestaña Web | Dicho |
| 3 · `curl.exe` (11:26) | HTTP: **302** a `https://`, que hace el proxy de PythonAnywhere (la iteración esperaba el 301 de Django; `SECURE_SSL_REDIRECT` no se probó por separado en producción, solo en las pruebas automáticas). HTTPS: 200 sin bucle, `Strict-Transport-Security: max-age=3600`, `csrftoken` con `Secure` | Pegado |
| 4 · Ventana privada | Pedido, pago, respaldo y «Reabrir Pedido» sin 403 | Dicho |
| 5 · Registros | `grep` de «csrf» y «forbidden» en `server.log` y `error.log`: sin resultados | Pegado |
| No verificado | `sessionid` con `Secure` en el navegador (solo lo cubren las pruebas automáticas); se revisa en el escalón 2 | — |

## Despliegue y verificación del escalón 2 (2026-11-19)

| Paso | Resultado | Fuente |
| :--- | :-------- | :----- |
| Respaldo previo | `respaldo_19-11-2026_12-07-14.sql`, `VÁLIDO`, 19 de 19, 1.542.750 bytes, SHA-256 `b7d320f6…ba11c` | Pegado |
| Etiqueta | `v4.4-hsts-semana` sobre `854cd74`, en `origin`; `git describe` en el servidor da la etiqueta; diff de `v4.3` a `v4.4`: `settings.py`, la prueba y documentos | Pegado |
| Reload | «Starting» a las 12:10:01, listo a las 12:10:08. Se citó 11:25 (hora del escalón 1): **vale el registro** | Pegado (`server.log`) |
| 1 · `check --deploy` | Después del Reload: solo W005 y W021 | Pegado |
| 3 · `curl.exe` (15:13 UTC) | HTTPS 200, `Strict-Transport-Security: max-age=604800`, `csrftoken` `Secure`; HTTP 302 a HTTPS y luego 200, sin bucle | Pegado |
| Cookies (DevTools) | `sessionid` HttpOnly, Secure, Lax; `csrftoken` Secure, Lax. Cierra lo que faltaba del escalón 1. Además, dos `_ga` con dominio de Tailwind: AUD-05-020 (Baja, Épica 14, origen sin investigar) | Captura |
| 4 · Ventana privada | Pedido, pago, respaldo y «Reabrir Pedido» sin 403 | Dicho |
| 5 · Registros | Sin «csrf» ni «forbidden» en `server.log` ni `error.log` | Pegado |

## Escalón 2 (implementado el 2026-11-19; desplegado y verificado el mismo día)

- **Cuándo:** el mismo día, con las verificaciones 1 a 5 del escalón 1 correctas (D6, RDA-021).
- **Cambio exacto:** en `PedidosApp/settings.py`, `SECURE_HSTS_SECONDS = 3600` pasa a `SECURE_HSTS_SECONDS = 604800` y el comentario «escalón 1: una hora» pasa a «escalón 2: una semana». Nada más.
- **Prueba que cambia:** en `test_seguridad_produccion.py`, `assertEqual(datos['SECURE_HSTS_SECONDS'], 3600)` pasa a `604800` y la cabecera esperada pasa a `'max-age=604800'`. Se cambia primero la prueba (falla) y después el valor.
- **Sin cambios en el `.env`** del servidor.
- **Etiqueta:** `v4.4-hsts-semana`; retroceso: `v4.3-configuracion-produccion` (o `v14.2-duplicar-items` si el problema viene del escalón 1).
- **Verificación:** se repiten los pasos 1, 3 (ahora `max-age=604800`) y 5, y se revisa en DevTools que `sessionid` lleve `Secure`.
- **Hecho (2026-11-19):** prueba primero (2 fallos con 3600), valor cambiado y comentario actualizado; pasos de despliegue en [bitacora-04-02-escalon-2](../../99_bitacora/epica-04-seguridad/bitacora-04-02-escalon-2.md). AUD-01-012 se cierra al verificar este escalón.
