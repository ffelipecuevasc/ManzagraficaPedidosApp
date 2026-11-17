# Iteración 04-02 · Configuración de producción

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** Pendiente (redactada, decisiones abiertas). Redactada el 2026-11-17 ([bitacora-04-02-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-02-redaccion.md)). Seis decisiones `PENDIENTE_DESARROLLADOR` (sección «Decisiones»), cada una con opción recomendada.
- **Subfase del plan:** 4.2 «Configuración de producción» (`plan-de-trabajo.md:400-408`).
- **Depende de:** Épica 02 (Terminada). Se desarrolla en local en paralelo a la vigilancia de la 03-05. **No se despliega antes de cerrar la vigilancia de la 03-05 (desde el lunes 2026-11-23 a las 23:48:12)** ni en el mismo despliegue que la 04-01 (RDA-007).
- **RDA relacionadas:** RDA-004 (PythonAnywhere, plan gratuito), RDA-007 (un despliegue, un propósito; la etiqueta marca lo que está en producción).
- **Hallazgos que cierra:** AUD-01-012 (configuración de producción sin endurecer), al verificarse en producción.
- **Hallazgos relacionados:** AUD-02-022 (`ALLOWED_HOSTS`, **ya resuelto en la 00-04**: no se repite), AUD-02-010 y la advertencia `W009` (clave secreta: 04-03).
- **Cambio de esquema:** ninguno.
- **Respaldo previo al despliegue:** no lo exige por sí misma (sin migraciones ni datos). Se sigue el protocolo normal.
- **Archivos que tocará la ejecución:** `PedidosApp/settings.py` y `.env.example` (configuración: **requiere consulta previa**, `AGENTS.md` sección 6), `docs/operacion/despliegue.md` (lista de advertencias esperadas) y pruebas. El `.env` del servidor lo edita solo el desarrollador.

## Objetivo

Que `python manage.py check --deploy` en producción no muestre advertencias resueltas a ciegas, que las cookies viajen solo por HTTPS, que el navegador use siempre HTTPS (HSTS introducido con un periodo corto) y que la aplicación se niegue a arrancar con una configuración insegura.

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
- **Inferido:** con Django 6.0, un POST por HTTPS con cabecera `Origin` solo pasa la comprobación CSRF si `request.is_secure()` es verdadero o el origen está en `CSRF_TRUSTED_ORIGINS`. Como hoy los formularios funcionan en producción sin `CSRF_TRUSTED_ORIGINS` ni `SECURE_PROXY_SSL_HEADER`, lo más probable es que PythonAnywhere entregue la petición a Django con esquema `https`. Se confirma en producción (paso de verificación 3); si no fuera así, `SECURE_SSL_REDIRECT` haría un bucle de redirecciones.

## Alcance

1. **Cookies seguras:** `SESSION_COOKIE_SECURE` y `CSRF_COOKIE_SECURE` verdaderos en producción (W012, W016).
2. **HTTPS:** redirección según la decisión 2 (W008).
3. **HSTS escalonado:** `SECURE_HSTS_SECONDS` con valor corto en el primer despliegue y subida posterior según la decisión 1 (W004). `SECURE_HSTS_INCLUDE_SUBDOMAINS` y `SECURE_HSTS_PRELOAD` según la decisión 1.
4. **Orígenes CSRF de confianza** según la decisión 4.
5. **Arranque que falla si la configuración es insegura**, según la decisión 5.
6. **Cómo se activan en local y en producción**, según la decisión 3, sin estorbar `runserver` ni las pruebas.
7. **Documentación:** actualizar la lista de advertencias esperadas de `despliegue.md:114` (queda W009 en local hasta la 04-03).
8. **Fuera:** `ALLOWED_HOSTS` (00-04), `SECRET_KEY` obligatoria y W009 (04-03), política de contenido (04-09), límites de subida (04-08), limpieza de `settings.py` (04-05).

## Decisiones (`PENDIENTE_DESARROLLADOR`)

**D1 · Valores de HSTS y escalones.** HSTS no se deshace: un navegador que lo recibió exige HTTPS durante `max-age` aunque se retroceda el código.
- **A (recomendada):** primer despliegue con `3600` (1 hora) y sin `includeSubDomains` ni `preload`; tras la ventana de observación sin problemas, un segundo despliegue de esta misma iteración sube a `604800` (1 semana); el valor alto (`31536000`) queda como paso posterior anotado. **Nunca `preload`:** el dominio es un subdominio de `pythonanywhere.com`, que no es propio.
- **B:** `86400` (1 día) desde el inicio y luego el valor alto.
- **C:** quedarse en un valor bajo y silenciar W004 con justificación.

**D2 · Redirección a HTTPS (W008).**
- **A:** `SECURE_SSL_REDIRECT = True` en producción. Riesgo: bucle si Django no ve la petición como segura (ver «PythonAnywhere»); se confirma antes con el paso de verificación 3.
- **B (recomendada):** confiar en «Force HTTPS» de PythonAnywhere, comprobar que sigue activo y silenciar `security.W008` con `SILENCED_SYSTEM_CHECKS` y un comentario que diga por qué. Sin riesgo de bucle. Se pasa a A si la verificación 3 confirma `https`.

**D3 · Cómo se activan.** El ejecutor de pruebas de Django fuerza `DEBUG=False`, pero `settings.py` se evalúa antes con el valor del entorno (inferido; se confirma en la ejecución).
- **A (recomendada):** derivar de `not DEBUG` (la variable que ya existe): en producción todo activo, en local con `DEBUG=True` inactivo, y `check --deploy` local con `DEBUG=False` las muestra activas.
- **B:** una variable nueva (por ejemplo `ENTORNO=produccion`) en `.env` y `.env.example`. Más explícito, pero el servidor necesita un cambio de `.env` que hace el desarrollador.

**D4 · `CSRF_TRUSTED_ORIGINS`.**
- **A (recomendada):** leerlo del entorno, vacío por defecto, y definir en el `.env` del servidor `https://manzagrafica.pythonanywhere.com`. Documentado en `.env.example` sin valores reales.
- **B:** no definirlo, porque hoy los POST funcionan (inferido). El plan lo pide; B se justifica solo si la verificación 3 confirma `https`.

**D5 · Qué hace fallar el arranque.**
- **A (recomendada):** `ImproperlyConfigured` si `DEBUG` es verdadero y `ALLOWED_HOSTS` contiene un dominio que no es local (señal de producción en modo depuración). La clave secreta obligatoria queda en la 04-03, para no mezclar.
- **B:** además, fallar si en producción falta alguna de las opciones seguras (redundante con D3-A).

**D6 · Ventana y orden.**
- **A (recomendada):** desplegar después de que la 04-01 esté desplegada y validada, en un día hábil por la tarde (para observar con uso real), con 7 días de observación antes de subir HSTS.
- **B:** otro calendario que fije el desarrollador.

## Pasos

0. Consulta previa al desarrollador para editar `settings.py` y `.env.example` (`AGENTS.md`, sección 6), con D1 a D6 resueltas.
1. Línea base local: `check --deploy` con `DEBUG=False` (esperado: W004, W008, W009, W012, W016) y `test pedidos` (se anota el número tras la 04-01).
2. Pruebas primero (sección siguiente).
3. Bloque de seguridad en `settings.py` según D1 a D5, con comentarios en español.
4. `.env.example` (según D3 y D4), sin valores reales.
5. `check --deploy` local con `DEBUG=False`: esperado solo W009 (y W008 silenciada si D2-B). `runserver` con `DEBUG=True` sigue entrando por `http://127.0.0.1:8000` sin redirección ni cookies seguras.
6. `despliegue.md:114`: lista nueva de advertencias esperadas.
7. Bitácora, registro, estado «En revisión», con los pasos de producción para el desarrollador.

## Pruebas

- **Arranque inseguro (D5):** un proceso hijo que importa la configuración con `DEBUG=True` y `ALLOWED_HOSTS` de producción termina con `ImproperlyConfigured`; con valores locales arranca. Lugar sugerido: `test_arranque.py` o `test_entorno.py` (existen; se revisa cuál corresponde al ejecutar).
- **Valores por entorno (D3):** con `DEBUG=False` en el proceso hijo, las cookies son seguras y HSTS tiene el valor de D1; con `DEBUG=True`, no.
- **Sin efecto en el resto:** la suite completa sigue con los mismos fallos esperados que deje la 04-01 (4: R8, R9, R14, R15). Si `SECURE_SSL_REDIRECT` llegara activo a las pruebas, todas las peticiones darían 301: es la señal de que D3 quedó mal.

## Verificación en producción (la hace el desarrollador; todo **no verificado** hasta entonces)

1. **[PA]** `check --deploy` en el servidor, con el filtro de códigos de `evidencia-03-05.md:273`, **antes** y **después**: antes, W004 W008 W012 W016 (dicho por el desarrollador); después, ninguna salvo las silenciadas a propósito.
2. **[PA · Panel]** «Force HTTPS» sigue activado (D2).
3. **[PC]** `curl -sI http://manzagrafica.pythonanywhere.com/accounts/login/` responde redirección a `https://`; `curl -sI https://manzagrafica.pythonanywhere.com/accounts/login/` trae `Strict-Transport-Security: max-age=<valor de D1>` y `Set-Cookie: csrftoken=…; Secure`. Sin bucle de redirecciones.
4. **[Navegador, ventana privada]** iniciar sesión, crear un pedido y un pago de prueba según el protocolo vigente, generar un respaldo (descarga): ningún 403 de CSRF. Las tres pantallas de `despliegue.md`, sección 3.7.
5. **[PA]** `server.log` desde el reinicio efectivo: sin `Forbidden (CSRF` ni errores nuevos.
6. **Ventana de observación (D6):** 7 días sin 403 de CSRF ni reportes de acceso del cliente antes de subir HSTS.

## Plan de retroceso

- **Código:** `retroceso.md`, caso 1 (sin migraciones): volver a la etiqueta anterior y recargar. Revierte cookies, redirección y orígenes CSRF.
- **Lo que no se revierte:** el HSTS ya recibido. Por eso el primer valor es corto (D1-A, 1 hora): tras el retroceso, los navegadores vuelven a aceptar HTTP como mucho una hora después. Mientras «Force HTTPS» siga activo en PythonAnywhere, el sitio funciona igual por HTTPS, así que el HSTS por sí solo no deja el sitio inaccesible.
- **Disparadores:** bucle de redirecciones, 403 de CSRF en formularios, el cliente no puede iniciar sesión.

## Criterio de término

- `check --deploy` en producción sin advertencias, salvo las silenciadas con justificación escrita (no verificado hasta el despliegue).
- Cookies `Secure` y cabecera HSTS vistas en producción con el valor del escalón vigente.
- Arranque con `DEBUG=True` y host de producción falla con un mensaje claro (prueba automatizada).
- Suite en verde con los mismos fallos esperados que deje la 04-01.
- Ventana de observación cumplida y escalón de HSTS registrado en la bitácora.

## Riesgos

- **HSTS irreversible por `max-age`:** mitigado con D1-A.
- **Bucle de redirección** con `SECURE_SSL_REDIRECT` si Django no ve `https`: mitigado con D2-B o con la verificación 3 antes de A.
- **Sesiones abiertas:** al cambiar las cookies a `Secure`, las sesiones vigentes siguen funcionando por HTTPS (inferido); si el cliente usara `http://` sin «Force HTTPS», perdería la sesión. Se avisa al cliente antes del despliegue.
- **Un despliegue, un propósito (RDA-007):** solo configuración de producción; ni la 04-01 ni la 04-03 viajan en la misma etiqueta. La subida de HSTS es un despliegue aparte de la misma iteración.
