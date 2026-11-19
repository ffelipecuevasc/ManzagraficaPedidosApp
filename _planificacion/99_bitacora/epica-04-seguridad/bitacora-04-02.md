# Bitácora 04-02 · Configuración de producción (escalón 1)

- **Fecha:** 2026-11-19
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** ~~En revisión · escalón 1 implementado, pendiente de despliegue; escalón 2 pendiente~~ **Escalón 1 desplegado y verificado el 2026-11-19** (`v4.3-configuracion-produccion`, `c62a92e`; pendiente solo `sessionid` con `Secure` en el navegador). Detalle del despliegue en la iteración, sección «Despliegue y verificación del escalón 1». El escalón 2 sigue en [bitacora-04-02-escalon-2](bitacora-04-02-escalon-2.md).
- **Nota:** `.env.example` lo editó el desarrollador (commit `c62a92e`).

## Resumen

Se implementó el escalón 1 de la 04-02 (D1 a D5): variable `SEGURIDAD_PRODUCCION`, cookies seguras, redirección a HTTPS en Django, HSTS de 3600 s sin `includeSubDomains` ni `preload`, `CSRF_TRUSTED_ORIGINS` desde el entorno y arranque que falla con el dominio de producción y la variable apagada. Pruebas primero (11 nuevas, 9 fallaban antes). Sin migraciones. El escalón 2 (604800) queda descrito en la iteración. Etiquetas: `v4.3-configuracion-produccion` y `v4.4-hsts-semana`; retroceso `v14.2-duplicar-items` (decisiones del 2026-11-19).

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `PedidosApp/settings.py` | Bloque «Seguridad de producción» después de `ALLOWED_HOSTS` (CRLF conservado). Consulta previa aprobada el 2026-11-19. |
| `pedidos/tests/test_seguridad_produccion.py` | Nuevo: 11 pruebas (arranque en proceso hijo, valores por entorno, redirección 301 y HSTS). |
| `docs/operacion/despliegue.md` | Advertencias esperadas (W005, W021; W009 en local) y paso 3.1 bis: `.env` → código → Reload. |
| `docs/operacion/retroceso.md` | Qué hacer con la variable al volver atrás. |
| `_planificacion/10_epicas/epica-04-seguridad/iteracion-04-02-configuracion-de-produccion.md` | Estado, etiquetas, verificación 4 con «Reabrir Pedido», ejecución del escalón 1 y descripción del escalón 2. |
| `_planificacion/10_epicas/epica-04-seguridad/definicion-epica-04.md` | Estado de la 04-02 y próximo hito. |
| `_planificacion/00_producto/registro-pendientes.md` | Estado, etiquetas, historial. |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-01-012: corregido en código, pendiente de verificar en producción. |
| `.env.example` | **No editado:** la configuración de permisos de Claude Code bloquea leerlo. Líneas a agregar, abajo. |

## Verificación

- Línea base, `DEBUG=False python manage.py check --deploy`: W004, W008, W009, W012, W016.
- Línea base, `python manage.py test pedidos`: 316 pruebas, `OK (expected failures=4)`.
- Pruebas nuevas antes del cambio: 11, `FAILED (failures=7, errors=2)`. Las 2 que ya pasaban son de protección (valores locales arrancan; `'1'` no activa la variable).
- Pruebas nuevas después: 11, `OK`.
- `SEGURIDAD_PRODUCCION=True DEBUG=False python manage.py check --deploy`: **W005, W009, W021**, sin errores (lo esperado).
- `python manage.py check`: sin problemas. `makemigrations --check --dry-run`: `No changes detected`.
- Suite completa después: 327 pruebas, `OK (expected failures=4)`, 587 s.
- **No hecho:** el ensayo manual en la réplica con `runserver` (301 a `https://127.0.0.1:8000` con la variable activa, entrada normal con la variable apagada, arranque bloqueado con el dominio) ni la revisión de pantallas a 360 px (no hay cambios de interfaz). Las pruebas automatizadas cubren los tres comportamientos.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] Arranque con el dominio de producción y la variable apagada falla con mensaje claro (prueba en proceso hijo).
- [x] Suite en verde con los mismos 4 fallos esperados.
- [x] `check --deploy` en producción solo con W005 y W021 (pegado; leído con el código nuevo **antes** del Reload, no se repitió después).
- [x] Redirección sin bucle (302 del proxy de PythonAnywhere), `csrftoken` con `Secure` y HSTS 3600 en producción (pegado, 11:26). `sessionid` con `Secure`: no verificado en el navegador.
- [ ] Escalón 2 (604800): pendiente.

## Decisiones tomadas

- `SECURE_PROXY_SSL_HEADER` no se define: la iteración no lo exige (inferido de que hoy los POST pasan CSRF). Un bucle en la verificación 3 lo desmentiría.
- Solo el texto exacto `True` activa la variable, como `DEBUG`.
- `CSRF_TRUSTED_ORIGINS` se define siempre, también en local (D4).

## Pasos para el desarrollador

**`.env.example`** (agregar, sin valores reales):

```text
# Seguridad de producción (04-02). True solo en el servidor; si falta, apagada.
# Con ALLOWED_HOSTS de producción y esta variable apagada, Django no arranca.
SEGURIDAD_PRODUCCION=
# Orígenes de confianza para CSRF, separados por comas. Sin valor: los locales.
CSRF_TRUSTED_ORIGINS=
```

**Despliegue del escalón 1 (`v4.3-configuracion-produccion`):**

1. Aviso al cliente (abajo), antes de empezar.
2. Respaldo según el protocolo normal (la iteración no lo exige por sí misma).
3. **[PA]** `check --deploy` antes (con el filtro de `evidencia-03-05.md:273`): esperado W004, W008, W012, W016.
4. **[PA]** `.env` del servidor: agregar `SEGURIDAD_PRODUCCION=True` y `CSRF_TRUSTED_ORIGINS=https://manzagrafica.pythonanywhere.com` (`despliegue.md`, 3.1 bis).
5. **[PA]** `git fetch origin --tags`, `git checkout v4.3-configuracion-produccion`, `git describe --tags`. Sin `pip`, migraciones ni `collectstatic`.
6. **[PA · Panel]** Reload; hora de `Starting uWSGI`.
7. Verificaciones 1 a 5 de la iteración: (1) `check --deploy` solo W005 y W021; (2) «Force HTTPS» activo; (3) `curl -sI http://…/accounts/login/` → 301 a `https://`, `curl -sIL https://…/accounts/login/` → 200 sin bucle, con `Strict-Transport-Security: max-age=3600` y `Set-Cookie: csrftoken=…; Secure`; (4) ventana privada: iniciar sesión, pedido y pago de prueba, respaldo, «Reabrir Pedido» con fecha desde mañana, ningún 403; borrar los de prueba; (5) `server.log` sin `Forbidden (CSRF` ni errores nuevos.
8. **Retroceso más rápido:** `git checkout v14.2-duplicar-items` + Reload, **dejando la variable en el `.env`** (el código anterior la ignora). Nunca poner la variable en `False` con el código de la 04-02: no arranca.

**Aviso al cliente (propuesto, no enviado):**

> Hola. Hoy vamos a hacer una mejora de seguridad en la aplicación de pedidos. Es posible que te pida iniciar sesión de nuevo. Si algo no funciona como siempre, avísame y lo reviso al tiro.

## Pendientes y riesgos

- `.env.example` sin editar (permisos).
- Bucle de redirecciones: solo se ve en producción (verificación 3).
- El escalón 2 se ejecuta en otro prompt (descrito en la iteración).

## Commit sugerido

`Épica 4 - Iteración 04-02: escalón 1, SEGURIDAD_PRODUCCION con cookies seguras, HTTPS, HSTS 3600, orígenes CSRF y arranque que falla`
