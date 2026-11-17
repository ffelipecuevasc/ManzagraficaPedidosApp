# Iteración 04-02 · Configuración de producción

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** Pendiente (redactada, decisiones resueltas). Redactada el 2026-11-17 ([bitacora-04-02-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-02-redaccion.md)); D1 a D6 **resueltas el 2026-11-17** por el desarrollador (dicho por él; [bitacora-04-02-cierre](../../99_bitacora/epica-04-seguridad/bitacora-04-02-cierre.md)). Queda abierta solo la etiqueta y la fecha del despliegue.
- **Subfase del plan:** 4.2 «Configuración de producción» (`plan-de-trabajo.md:400-408`).
- **Depende de:** Épica 02 (Terminada). Se desarrolla en local en paralelo a la vigilancia de la 03-05. **No se despliega antes de cerrar la vigilancia de la 03-05 (desde el lunes 2026-11-23 a las 23:48:12)** ni en el mismo despliegue que la 04-01 (RDA-007). Orden: 04-01, 04-02, 04-03.
- **RDA relacionadas:** RDA-004 (PythonAnywhere, plan gratuito), RDA-007 (un despliegue, un propósito; la etiqueta marca lo que está en producción).
- **Hallazgos que cierra:** AUD-01-012 (configuración de producción sin endurecer), al verificarse en producción.
- **Hallazgos relacionados:** AUD-02-022 (`ALLOWED_HOSTS`, **ya resuelto en la 00-04**: no se repite), AUD-02-010 y la advertencia `W009` (clave secreta: 04-03, que usa la variable de D3).
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
| D1 | HSTS escalonado, sin `preload` | Primer despliegue con `SECURE_HSTS_SECONDS = 3600`; tras la observación (D6), un segundo despliegue de esta iteración sube a `604800`. Sin `SECURE_HSTS_PRELOAD` (el dominio es un subdominio de `pythonanywhere.com`, no propio) y sin `SECURE_HSTS_INCLUDE_SUBDOMAINS` (inferido: no hay subdominios propios; se anota en la ejecución). El valor alto (`31536000`) no es parte de esta iteración. |
| D2 | Django **también** redirige a HTTPS | `SECURE_SSL_REDIRECT = True` cuando la variable de D3 está activa, además de «Force HTTPS» de PythonAnywhere. Se prueba antes en la réplica (ver «Pruebas») por el riesgo de bucle. |
| D3 | Variable de entorno explícita | Las opciones seguras (cookies, redirección, HSTS) se activan con una variable propia, no derivada de `DEBUG`. Nombre propuesto: `SEGURIDAD_PRODUCCION` (`True`/`False`, falso si falta); el nombre final se confirma en la consulta previa. Va en `.env.example` sin valor real y en el `.env` del servidor (lo edita el desarrollador). |
| D4 | `CSRF_TRUSTED_ORIGINS` desde el entorno | Lista separada por comas, con valor local por defecto `http://localhost:8000,http://127.0.0.1:8000`; en el servidor, `https://manzagrafica.pythonanywhere.com`. |
| D5 | Arranque que falla | `ImproperlyConfigured` si `ALLOWED_HOSTS` contiene `manzagrafica.pythonanywhere.com` y la variable de D3 no está activa. Compensa el riesgo de olvidar la variable (D3). |
| D6 | Observación de 3 días | Tres días sin 403 de CSRF, sin bucles ni reportes del cliente antes de subir HSTS a `604800`. Sustituye los 7 días propuestos en la redacción. |

**Riesgo de D3 (olvidar la variable):** si el `.env` del servidor no la trae, Django arrancaría sin cookies seguras ni HSTS ni redirección, en silencio. D5 lo convierte en un fallo ruidoso: la web app no arranca y el despliegue se nota en la verificación. Riesgo residual: un error al escribir el dominio en `ALLOWED_HOSTS` desactivaría D5; la verificación de producción (pasos 1 y 3) lo detecta. El orden de edición en el servidor importa: **primero `.env`, luego código, luego Reload** (si se recarga código nuevo sin la variable, D5 tumba el sitio hasta corregir `.env`).

## Alcance

1. **Variable de seguridad (D3)** y bloque de seguridad en `settings.py` que depende de ella.
2. **Cookies seguras:** `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` (W012, W016).
3. **Redirección a HTTPS en Django (D2)** (W008).
4. **HSTS escalonado (D1)** (W004).
5. **Orígenes CSRF de confianza (D4).**
6. **Arranque que falla (D5).**
7. **Documentación:** lista de advertencias esperadas de `despliegue.md:114` (queda W009 en local hasta la 04-03); paso nuevo en el despliegue (editar `.env` antes del Reload) y en `retroceso.md` (qué hacer con la variable al volver atrás).
8. **Fuera:** `ALLOWED_HOSTS` (00-04), `SECRET_KEY` obligatoria y W009 (04-03), política de contenido (04-09), límites de subida (04-08), limpieza de `settings.py` (04-05).

## Pasos

0. Consulta previa al desarrollador para editar `settings.py` y `.env.example` (`AGENTS.md`, sección 6) y confirmar el nombre de la variable.
1. Línea base local: `check --deploy` con `DEBUG=False` (esperado: W004, W008, W009, W012, W016) y `test pedidos` (se anota el número tras la 04-01).
2. Pruebas primero (sección siguiente).
3. Bloque de seguridad en `settings.py` según D1 a D5, con comentarios en español.
4. `.env.example` con la variable de D3 y `CSRF_TRUSTED_ORIGINS`, sin valores reales.
5. `check --deploy` local con `DEBUG=False` y la variable activa: esperado solo W009. Con la variable apagada, `runserver` sigue entrando por `http://127.0.0.1:8000` sin redirección.
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

1. **[PA]** `check --deploy` en el servidor, con el filtro de códigos de `evidencia-03-05.md:273`, **antes** y **después**: antes, W004 W008 W012 W016 (dicho por el desarrollador); después, ninguna.
2. **[PA · Panel]** «Force HTTPS» sigue activado.
3. **[PC]** `curl -sI http://manzagrafica.pythonanywhere.com/accounts/login/` redirige a `https://`; `curl -sIL https://manzagrafica.pythonanywhere.com/accounts/login/` termina en 200 **sin bucle** (`curl` corta tras demasiadas redirecciones) y trae `Strict-Transport-Security: max-age=3600` y `Set-Cookie: csrftoken=…; Secure`.
4. **[Navegador, ventana privada]** iniciar sesión, crear un pedido y un pago de prueba según el protocolo vigente, generar un respaldo (descarga): ningún 403 de CSRF. Las pantallas de `despliegue.md`, sección 3.7.
5. **[PA]** `server.log` desde el reinicio efectivo: sin `Forbidden (CSRF` ni errores nuevos.
6. **Observación (D6):** 3 días. Después, segundo despliegue con HSTS `604800` y repetición de los pasos 1, 3 y 5.

## Plan de retroceso

- **Bucle de redirecciones o 403 de CSRF:** `retroceso.md`, caso 1 (sin migraciones): volver a la etiqueta anterior y recargar. **Más rápido:** poner la variable de D3 en `False` en el `.env` del servidor y recargar apaga redirección, cookies seguras y HSTS sin tocar el código; pero D5 impide arrancar así con el dominio de producción, de modo que con la variable apagada **hay que volver también el código**. Se ensaya en la réplica cuál de los dos caminos se documenta.
- **Lo que no se revierte:** el HSTS ya recibido, durante su `max-age`. Por eso 3600 s primero: tras el retroceso, los navegadores aceptan HTTP de nuevo en una hora como máximo. Con «Force HTTPS» activo, el sitio funciona igual por HTTPS.
- **Disparadores:** bucle de redirecciones, 403 de CSRF en formularios, el cliente no puede iniciar sesión, la web app no arranca por D5.

## Criterio de término

- `check --deploy` en producción sin advertencias (no verificado hasta el despliegue).
- Redirección a HTTPS sin bucle, cookies `Secure` y HSTS vistos en producción con el escalón vigente (3600, luego 604800).
- Arranque con el dominio de producción y la variable apagada falla con un mensaje claro (prueba automatizada).
- Suite en verde con los mismos fallos esperados que deje la 04-01.
- Observación de 3 días cumplida y subida a 604800 registrada en la bitácora.

## Riesgos

- **Bucle de redirección (D2):** solo verificable en producción; mitigado con la prueba del cliente de pruebas, la verificación 3 inmediata y el retroceso del caso 1.
- **Olvidar la variable (D3):** mitigado con D5 y con el orden `.env` → código → Reload.
- **HSTS irreversible por `max-age`:** mitigado con 3600 s primero (D1).
- **Sesiones abiertas:** al pasar las cookies a `Secure`, las sesiones vigentes siguen por HTTPS (inferido). Se avisa al cliente antes del despliegue.
- **Un despliegue, un propósito (RDA-007):** solo configuración de producción; ni la 04-01 ni la 04-03 viajan en la misma etiqueta. La subida de HSTS es un despliegue aparte de esta misma iteración.
