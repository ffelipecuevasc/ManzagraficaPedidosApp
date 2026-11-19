# Bitácora 04-02 · Configuración de producción (escalón 2, HSTS 604800)

- **Fecha:** 2026-11-19
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** **Completada y verificada en producción (2026-11-19)** · `v4.4-hsts-semana` (`854cd74`). ~~En revisión · escalón 2 implementado, pendiente de despliegue~~

## Cierre en producción (2026-11-19)

- Respaldo previo `respaldo_19-11-2026_12-07-14.sql`, `VÁLIDO`, 19 de 19, 1.542.750 bytes (pegado).
- Reload: «Starting» 12:10:01, listo 12:10:08 según `server.log` (se citó 11:25, hora del escalón 1; vale el registro).
- `check --deploy` después del Reload: solo W005 y W021 (pegado). Siguen aceptadas y sin silenciar.
- `curl.exe` (15:13 UTC): `max-age=604800`, `csrftoken` `Secure`, HTTP 302 → HTTPS 200 sin bucle (pegado).
- DevTools (captura): `sessionid` HttpOnly, Secure, Lax; `csrftoken` Secure, Lax.
- Sin 403 en la ventana privada (dicho); sin «csrf» ni «forbidden» en los registros (pegado).
- AUD-01-012: resuelto y verificado en producción. Hallazgo nuevo: AUD-05-020 (Baja, Épica 14), dos cookies `_ga` con dominio de Tailwind, origen sin investigar.
- **El HSTS de 604800 s ya emitido dura hasta 7 días** en los navegadores que lo recibieron, aunque se haga un retroceso.
- Destino de retroceso para la siguiente iteración: `v4.4-hsts-semana`.

## Resumen

El escalón 1 (`v4.3-configuracion-produccion`) quedó desplegado y verificado el mismo día ([bitacora-04-02](bitacora-04-02.md)). Este escalón solo sube `SECURE_HSTS_SECONDS` de 3600 a 604800 (una semana), con las pruebas primero. Sin migraciones, estáticos ni cambios en el `.env`. Etiqueta propuesta: `v4.4-hsts-semana`; retroceso: `v4.3-configuracion-produccion`.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `PedidosApp/settings.py` | `SECURE_HSTS_SECONDS = 604800` y su comentario (CRLF conservado). Consulta previa aprobada el 2026-11-19. |
| `pedidos/tests/test_seguridad_produccion.py` | El valor esperado pasa a 604800 y la cabecera a `max-age=604800`. |
| `docs/operacion/despliegue.md` | Fila de `v4.3-configuracion-produccion` en la sección 5. |
| Iteración, `bitacora-04-02.md`, `registro-pendientes.md`, `definicion-epica-04.md` | Cierre del escalón 1 y estado del escalón 2. |

## Verificación

- Pruebas de `test_seguridad_produccion` con la prueba nueva y el valor viejo: 11, `FAILED (failures=2)` (las dos que fijan `max-age`).
- Las mismas después del cambio: 11, `OK`.
- Suite completa: 327 pruebas antes y después, `OK (expected failures=4)` (después: 613 s).
- `SEGURIDAD_PRODUCCION=True DEBUG=False python manage.py check --deploy`: W005, W009 y W021, sin errores (lo esperado).
- `makemigrations --check --dry-run`: `No changes detected`.
- `settings.py` y `registro-pendientes.md` siguen en CRLF.

## Migraciones

- Ninguna.

## Pasos de despliegue para el desarrollador (`v4.4-hsts-semana`)

1. **[PC]** Después del commit y la etiqueta: `git diff --stat v4.3-configuracion-produccion v4.4-hsts-semana` debe mostrar solo `PedidosApp/settings.py` (y, si van en el mismo commit, la prueba y los documentos; nada de `requirements.txt`, `pedidos/migrations/` ni estáticos).
2. Respaldo según el protocolo normal (este escalón no lo exige por sí mismo). Sin cambios en el `.env`.
3. **[PA · Bash]** `git fetch origin --tags`, `git checkout v4.4-hsts-semana`, `git describe --tags` → `v4.4-hsts-semana`. Sin `pip`, migraciones ni `collectstatic`.
4. **[PA · Panel]** Reload; anota la hora de `Starting uWSGI` en `server.log`.
5. **Verificación 1:** `check --deploy` en el servidor, **esta vez después del Reload**: solo W005 y W021.
6. **Verificación 3:** `curl.exe -sI https://manzagrafica.pythonanywhere.com/accounts/login/` trae `Strict-Transport-Security: max-age=604800`; `curl.exe -sIL http://manzagrafica.pythonanywhere.com/accounts/login/` termina en 200 sin bucle.
7. **`sessionid` con `Secure`:** ventana privada, iniciar sesión, DevTools → Application (Aplicación) → Cookies → `https://manzagrafica.pythonanywhere.com`: `sessionid` y `csrftoken` con la casilla **Secure** marcada.
8. **Verificación 5:** `server.log` y `error.log` desde el reinicio: sin `Forbidden (CSRF` ni errores nuevos.
9. **Retroceso:** `git checkout v4.3-configuracion-produccion` y Reload (`retroceso.md`, caso 1; el `.env` no se toca). **Lo que no se revierte:** los navegadores que ya recibieron `max-age=604800` siguen yendo solo por HTTPS hasta 7 días. Con «Force HTTPS» activo el sitio funciona igual por HTTPS. Un problema del escalón 1 se vuelve a `v14.2-duplicar-items`.

## Criterios de aceptación

- [x] Prueba primero que falla con 3600 y pasa con 604800.
- [x] HSTS 604800 en producción (`curl`, pegado).
- [x] `sessionid` con `Secure` en el navegador (captura de DevTools).
- [x] AUD-01-012 resuelto y verificado en producción.

## Pendientes y riesgos

- Con 604800 s, un problema de HTTPS dura hasta 7 días en los navegadores que ya recibieron la cabecera.

## Commit sugerido

`Épica 4 - Iteración 04-02: escalón 2, HSTS de 604800 s y cierre del escalón 1 verificado en producción`
