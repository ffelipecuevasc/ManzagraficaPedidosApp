# Bitácora 04-09 · Política de contenido en observación

- **Fechas:** 2026-11-22 (código y pruebas) y 2026-11-27 (revisión manual y cierre documental)
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** **Terminada · verificada en producción el 2026-11-27** (`v4.11-csp-observacion`, `37527b9`). Antes: ~~En revisión · pendiente de despliegue.~~ Etiqueta propuesta `v4.11-csp-observacion`; retroceso `v4.10-acceso-limites`; `despliegue.md` 3.16. Sin migraciones, `pip` ni `collectstatic`.

## Resumen

`django.middleware.csp.ContentSecurityPolicyMiddleware` justo después de `SecurityMiddleware` y `SECURE_CSP_REPORT_ONLY` con la política final (solo `'self'`, D1), sin nonces (D2), con el interruptor `CSP_OBSERVACION` (D3) y sin punto de recepción (D4). `SECURE_CSP` sigue sin definir. Ninguna plantilla ni JavaScript cambió. El código está en `6b6f590` (commit del desarrollador).

## Decisiones del desarrollador (2026-11-22, dichas por él)

- **C1:** autoriza editar `settings.py` como se propuso; `TEMPLATES` sin tocar.
- **C2:** solo el texto exacto `False` apaga la observación; cualquier otro valor la deja activa y el sitio arranca igual (nunca `ImproperlyConfigured`).
- **C3:** autoriza editar `.env.example`. El agente no pudo leerlo (configuración de permisos): el texto quedó abajo y el desarrollador lo pegó en `6b6f590`.
- **C4:** pruebas contra el MySQL local; sin migraciones.
- **C5:** la revisión manual la hace el desarrollador.
- **Orden:** la 04-09 se despliega **antes** que la 14-04; sin RDA nueva. El retroceso de la 14-04 se ajusta en la Épica 14.

## Cambios en el código (consola, agente)

- `settings.py`: `from django.utils.csp import CSP` (`:18`); middleware en `:125`; bloque «POLÍTICA DE CONTENIDO EN OBSERVACIÓN» (`:315-337`) con `CSP_OBSERVACION = os.getenv('CSP_OBSERVACION') != 'False'`. Solo inserciones (27 líneas), fin de línea CRLF intacto.
- `pedidos/tests/test_csp.py`, nuevo: cabecera en el acceso, el panel, una 404 y el admin; sin cabecera de bloqueo; `SECURE_CSP` vacío; sin `report-uri`, `report-to`, `http` ni servidores externos; sin `upgrade-insecure-requests` ni `frame-ancestors`; `X-Frame-Options: DENY`; middleware una vez tras `SecurityMiddleware`; interruptor en proceso hijo (`False` apaga; `True`, vacío, `false`, `0`, `no`, `FALSE` y ` False` dejan activa y arrancan); con la política vacía no sale cabecera.

Texto entregado para `.env.example`:

```
# Política de contenido en observación (04-09). Activa por defecto, también en local.
# Solo el texto exacto False la apaga: deja de enviarse la cabecera
# Content-Security-Policy-Report-Only. Cualquier otro valor la deja activa.
# No bloquea nada. Ver docs/operacion/politica-de-contenido.md.
# CSP_OBSERVACION=
```

## Pruebas (consola, agente)

| Momento | Resultado |
| :-- | :-- |
| Línea base | 446 pruebas, `OK (expected failures=3)`; `check` sin problemas |
| `test_csp` antes de implementar | 15 pruebas, `FAILED (failures=13, errors=1)`, contando subpruebas; 6 ya pasaban |
| Después | 461 pruebas, `OK (expected failures=3)`; `check` sin problemas; `makemigrations --check --dry-run` → `No changes detected` |

## Revisión manual en la réplica (dicho, informe del 2026-11-27)

- 18 de 18 pantallas, 24 páginas, en escritorio y a 360 px; paridad con diferencias aceptadas; `.env` local sin `CSP_OBSERVACION`, `DEBUG=True`.
- Cabecera de observación con 9 directivas, sin cabecera de bloqueo, `X-Frame-Options: DENY` (pestaña Red). El interruptor `False` hace desaparecer los `[Report Only]`.
- **Tabla A** (páginas con la infracción): `script-src`: Tailwind 23, jsDelivr 22, jQuery 23, en línea 33; `style-src`: Google Fonts 23, jsDelivr 22, en línea 154; `font-src`: gstatic 23; `connect-src`, `img-src`, `data:` y otras: 0.
- **Tabla B:** scripts en línea 29; manejadores 4 (páginas); estilos de plantilla 13; inyectados por Tailwind 92, por SweetAlert2 37, sin origen 12; `eval` 0.
- **Tabla C:** nada distinto por la política; ningún 500; 360 px igual.
- Admin: 0 infracciones. 404 y 500: no revisadas (`DEBUG=True`).
- Aclaraciones: los 11 atributos `style` observados son los 8 del código repetidos por bucles; los manejadores de los formularios de pedido son por fila de ítem; el inventario conserva 6 manejadores; el «Recargar» de `500.html` quedó sin revisar.

## Correcciones a la redacción

- `trabajo_semanal.html:7-12`: su `<style>` usa `{{ nivel_presion }}`; no se pasa tal cual a `index.css` (08-08).
- Manejadores en línea: 6 (3 en plantillas y 3 generados por `index.js`), no 7; la 04-01 retiró el de `respaldar_bd.html`.
- Líneas movidas tras la 04-08: anotadas en la iteración.

## Hallazgos nuevos (anteriores a la 04-09, abiertos, fuera de alcance)

AUD-05-025 (calendario en modo oscuro), AUD-05-026 (fecha de entrega vacía al editar; formato del widget verificado en `forms.py`, pérdida inferida, producción sin verificar), AUD-05-027 (`$ is not defined` en «Ingresar pago»; 08-08), AUD-05-028 (imprimir detalle de pago en blanco), AUD-05-029 y AUD-05-030 (gráficos SVG; localización de números como causa probable común). Del 027 al 030, comprobados con `CSP_OBSERVACION=False` (dicho).

## Qué no se pudo ver

- El navegador (todo lo de la revisión manual es dicho) y el contenido de `.env.example`.
- Las páginas 404 y 500 propias de la aplicación en el navegador.
- La cabecera a través del proxy de PythonAnywhere (verificación del despliegue).
- Qué librería inyecta los 12 estilos sin origen.

## Cierre en producción (2026-11-27, hora de Chile)

| Fuente | Hecho |
| :-- | :-- |
| Dicho | Respaldo con `v4.10` activo: `VÁLIDO`, 19 de 19, `CUMPLE D2`, código 0; nombre, tamaño y SHA-256 no constan |
| Consola | Rotación en `error.log` 10:51:08; checkout 10:52 (respaldo anterior: inferido) |
| Consola | Antes: `HEAD` `c995647` (`v4.10-acceso-limites`), árbol limpio; `.env` con `ACCESO_FALLOS_POR_DIRECCION=20`, `ACCESO_PROXIES_CONFIABLES=1`, 0 líneas `CSP_OBSERVACION` |
| Consola | Checkout `v4.11-csp-observacion` = `37527b9`, árbol limpio; `migrate --plan` sin operaciones; `check --deploy` solo W005 y W021; `DESDE_CL` válido |
| Consola | 1 «Starting uWSGI» (10:54:00); conteo de errores a las 11:01:36: 0; `error.log` sin entradas posteriores al arranque |
| Pantalla (captura) | `/accounts/login/` 200 con `Content-Security-Policy-Report-Only`, 9 directivas (`Date` 13:59:41 GMT); `Content-Security-Policy` ausente (inferido) |
| Dicho | Sitio igual; mensajes `[Report Only]` en la consola |
| No consta | `Strict-Transport-Security` y `X-Frame-Options` en producción; si el conteo fue después del uso |

Retroceso del despliegue siguiente (14-04): `v4.11-csp-observacion`. Destino de los hallazgos (2026-11-27): AUD-05-025, 027, 028, 029 y 030 a la Épica 14, agrupados por tema; AUD-05-026 Media (propuesta), pendiente de comprobar en la réplica (si la fecha se pierde al guardar, pasa a Crítica, RDA-022).

## Archivos

`settings.py` y `pedidos/tests/test_csp.py` (en `6b6f590`); en el cierre: `iteracion-04-09-…md`, `definicion-epica-04.md`, `registro-pendientes.md`, `auditoria-tecnica.md`, `docs/operacion/despliegue.md` (3.16 y fila prevista), `docs/operacion/politica-de-contenido.md` (nueva) y esta bitácora.
